/**
 * MCP — Model Context Protocol Implementation
 * Version: 1.0
 * EmpireHazeClaw Fleet
 */

const crypto = require('crypto');

// ============================================================
// CONSTANTS
// ============================================================

const MCP_CONFIG = {
  VERSION: '1.0',
  MAX_DEPTH: 64,
  MAX_RETRIES: 3,
  BACKOFF_BASE: 1000,
  BACKOFF_MULTIPLIER: 2,
  TOOL_CALL: 'tool_call',
  RESPONSE: 'response',
  ERROR: 'error',
  CASCADE: 'cascade'
};

const MCP_ERRORS = {
  INVALID_SCHEMA: { code: 'MCP001', name: 'INVALID_SCHEMA' },
  CYCLE_DETECTED: { code: 'MCP002', name: 'CYCLE_DETECTED' },
  DUPLICATE_BLOCKED: { code: 'MCP003', name: 'DUPLICATE_BLOCKED' },
  MAX_DEPTH_EXCEEDED: { code: 'MCP004', name: 'MAX_DEPTH_EXCEEDED' },
  MAX_RETRIES_EXCEEDED: { code: 'MCP005', name: 'MAX_RETRIES_EXCEEDED' },
  UNKNOWN_TOOL: { code: 'MCP006', name: 'UNKNOWN_TOOL' },
  ROUTING_FAILED: { code: 'MCP007', name: 'ROUTING_FAILED' }
};

// ============================================================
// TOOL SCHEMAS
// ============================================================

const TOOL_SCHEMAS = {
  exec: {
    input: {
      command: { type: 'string', required: true },
      workdir: { type: 'string', required: false },
      timeout: { type: 'number', required: false, min: 1, max: 300 },
      env: { type: 'object', required: false }
    },
    output: {
      stdout: { type: 'string' },
      stderr: { type: 'string' },
      exitCode: { type: 'number' },
      duration: { type: 'number' }
    }
  },
  write: {
    input: {
      path: { type: 'string', required: true, pattern: '^/' },
      content: { type: 'string', required: true }
    },
    output: {
      success: { type: 'boolean' },
      bytesWritten: { type: 'number' }
    }
  },
  edit: {
    input: {
      path: { type: 'string', required: true, pattern: '^/' },
      edits: {
        type: 'array',
        required: true,
        items: {
          oldText: { type: 'string' },
          newText: { type: 'string' }
        }
      }
    },
    output: {
      success: { type: 'boolean' },
      editsApplied: { type: 'number' }
    }
  },
  message: {
    input: {
      action: { type: 'string', required: true, enum: ['send', 'react', 'delete', 'edit'] },
      channel: { type: 'string', required: true },
      target: { type: 'string', required: false },
      message: { type: 'string', required: false },
      media: { type: 'string', required: false }
    },
    output: {
      success: { type: 'boolean' },
      messageId: { type: 'string' }
    }
  }
};

// ============================================================
// AGENT ROUTING
// ============================================================

const AGENT_ROUTING = {
  ceo: 'agent:ceo:telegram:direct:5392634979',
  security: 'agent:security:telegram:direct:5392634979',
  builder: 'agent:builder:telegram:direct:5392634979',
  data: 'agent:data:telegram:direct:5392634979',
  qc: 'agent:qc:telegram:direct:5392634979'
};

// ============================================================
// MESSAGE HISTORY (for cycle detection)
// ============================================================

const messageHistory = new Map();

/**
 * Generate UUID v4
 */
function generateUUID() {
  return crypto.randomUUID();
}

/**
 * Generate trace ID for request chain
 */
function generateTraceId() {
  return `${generateUUID()}-${Date.now()}`;
}

// ============================================================
// CORE FUNCTIONS
// ============================================================

/**
 * Create a new MCP Message
 */
function createMCPMMessage(type, source, target, payload) {
  const message = {
    version: MCP_CONFIG.VERSION,
    type: type,
    source: source,
    target: target,
    payload: {
      tool: payload.tool || null,
      input: payload.input || {},
      output: payload.output || null
    },
    metadata: {
      traceId: payload.traceId || generateTraceId(),
      depth: payload.depth || 1,
      retryCount: payload.retryCount || 0,
      timestamp: new Date().toISOString(),
      ttl: MCP_CONFIG.MAX_DEPTH
    }
  };

  return message;
}

/**
 * Validate MCP Schema
 */
function validateMCPSchema(message) {
  const errors = [];

  // Check required top-level fields
  if (!message.version) errors.push('Missing: version');
  if (!message.type) errors.push('Missing: type');
  if (!message.source) errors.push('Missing: source');
  if (!message.target) errors.push('Missing: target');
  if (!message.payload) errors.push('Missing: payload');
  if (!message.metadata) errors.push('Missing: metadata');

  // Validate version
  if (message.version && message.version !== MCP_CONFIG.VERSION) {
    errors.push(`Invalid version: ${message.version}`);
  }

  // Validate type
  const validTypes = [MCP_CONFIG.TOOL_CALL, MCP_CONFIG.RESPONSE, MCP_CONFIG.ERROR, MCP_CONFIG.CASCADE];
  if (message.type && !validTypes.includes(message.type)) {
    errors.push(`Invalid type: ${message.type}`);
  }

  // Validate tool schema if present
  if (message.payload && message.payload.tool) {
    const toolSchema = TOOL_SCHEMAS[message.payload.tool];
    if (!toolSchema) {
      errors.push(`Unknown tool: ${message.payload.tool}`);
    } else {
      // Validate input against schema
      const inputErrors = validateInputSchema(message.payload.input, toolSchema.input);
      errors.push(...inputErrors);
    }
  }

  // Validate depth
  if (message.metadata && message.metadata.depth > MCP_CONFIG.MAX_DEPTH) {
    errors.push(`MAX_DEPTH_EXCEEDED: depth ${message.metadata.depth} > ${MCP_CONFIG.MAX_DEPTH}`);
  }

  if (errors.length > 0) {
    return {
      valid: false,
      errors: errors
    };
  }

  return { valid: true, errors: [] };
}

/**
 * Validate input against schema
 */
function validateInputSchema(input, schema) {
  const errors = [];

  if (!schema) return errors;

  for (const [field, rules] of Object.entries(schema)) {
    const value = input[field];

    // Check required
    if (rules.required && (value === undefined || value === null)) {
      errors.push(`Missing required field: ${field}`);
      continue;
    }

    // Skip validation if not provided and not required
    if (value === undefined || value === null) continue;

    // Type check
    if (rules.type && typeof value !== rules.type) {
      errors.push(`Field ${field}: expected ${rules.type}, got ${typeof value}`);
    }

    // Min/Max for numbers
    if (rules.min !== undefined && value < rules.min) {
      errors.push(`Field ${field}: value ${value} < min ${rules.min}`);
    }
    if (rules.max !== undefined && value > rules.max) {
      errors.push(`Field ${field}: value ${value} > max ${rules.max}`);
    }

    // Pattern for strings
    if (rules.pattern && !new RegExp(rules.pattern).test(value)) {
      errors.push(`Field ${field}: value "${value}" does not match pattern ${rules.pattern}`);
    }

    // Enum
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push(`Field ${field}: value "${value}" not in enum [${rules.enum.join(', ')}]`);
    }
  }

  return errors;
}

/**
 * Check for cycles and duplicates
 */
function checkCycle(message, history = messageHistory) {
  const { traceId, depth, payload } = message.metadata;
  const inputHash = hashInput(payload.input || {});

  // Check max depth
  if (depth > MCP_CONFIG.MAX_DEPTH) {
    return {
      blocked: true,
      reason: 'MAX_DEPTH_EXCEEDED',
      error: MCP_ERRORS.MAX_DEPTH_EXCEEDED
    };
  }

  // Check for duplicate (same traceId + same input)
  const historyKey = `${traceId}:${inputHash}`;
  if (history.has(historyKey)) {
    const existing = history.get(historyKey);
    if (existing.depth <= depth) {
      return {
        blocked: true,
        reason: 'DUPLICATE_DETECTED',
        error: MCP_ERRORS.DUPLICATE_BLOCKED,
        cachedResponse: existing.response
      };
    }
  }

  // Record in history
  history.set(historyKey, {
    traceId,
    depth,
    inputHash,
    timestamp: Date.now()
  });

  return { blocked: false };
}

/**
 * Hash input for comparison
 */
function hashInput(input) {
  return crypto.createHash('sha256').update(JSON.stringify(input)).digest('hex').substring(0, 16);
}

/**
 * Calculate backoff delay
 */
function getBackoffDelay(retryCount) {
  return MCP_CONFIG.BACKOFF_BASE * Math.pow(MCP_CONFIG.BACKOFF_MULTIPLIER, retryCount);
}

/**
 * Sleep utility for retry delays
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Execute tool with retry logic
 */
async function executeWithRetry(tool, input, maxRetries = MCP_CONFIG.MAX_RETRIES) {
  let lastError = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // Simulate tool execution (replace with actual tool execution)
      const result = await executeTool(tool, input);
      return {
        success: true,
        result,
        attempts: attempt + 1
      };
    } catch (error) {
      lastError = error;
      console.log(`[MCP] Tool execution attempt ${attempt + 1} failed: ${error.message}`);

      if (attempt < maxRetries) {
        const delay = getBackoffDelay(attempt);
        console.log(`[MCP] Retrying in ${delay}ms...`);
        await sleep(delay);
      }
    }
  }

  return {
    success: false,
    error: lastError,
    attempts: maxRetries + 1,
    errorCode: MCP_ERRORS.MAX_RETRIES_EXCEEDED.code
  };
}

/**
 * Execute a tool (placeholder - integrate with actual tools)
 */
async function executeTool(tool, input) {
  const schema = TOOL_SCHEMAS[tool];
  if (!schema) {
    throw new Error(`Unknown tool: ${tool}`);
  }

  // Validate input
  const validation = validateInputSchema(input, schema.input);
  if (validation.length > 0) {
    throw new Error(`Validation failed: ${validation.join(', ')}`);
  }

  // Placeholder: Return mock result
  // In production, this would call the actual tool
  return {
    executed: true,
    tool,
    input,
    timestamp: new Date().toISOString()
  };
}

/**
 * Route message to appropriate agent
 */
function routeMessage(message) {
  const { target, payload } = message;

  // Check if target is a known agent
  if (AGENT_ROUTING[target]) {
    return {
      routed: true,
      target: target,
      sessionKey: AGENT_ROUTING[target],
      payload: payload
    };
  }

  // Route based on tool type
  const tool = payload?.tool;
  let routedTo = null;

  switch (tool) {
    case 'exec':
    case 'write':
    case 'edit':
      routedTo = 'builder';
      break;
    case 'message':
      routedTo = 'ceo'; // Messages go through CEO
      break;
    default:
      routedTo = 'ceo';
  }

  return {
    routed: true,
    target: routedTo,
    sessionKey: AGENT_ROUTING[routedTo],
    payload: payload
  };
}

/**
 * Create error response
 */
function createErrorResponse(originalMessage, error) {
  return createMCPMMessage(
    MCP_CONFIG.ERROR,
    'system',
    originalMessage.source,
    {
      tool: originalMessage.payload?.tool,
      input: originalMessage.payload?.input,
      output: {
        error: error.message || String(error),
        code: error.code || MCP_ERRORS.ROUTING_FAILED.code
      }
    }
  );
}

/**
 * Create success response
 */
function createResponse(originalMessage, result) {
  return createMCPMMessage(
    MCP_CONFIG.RESPONSE,
    'system',
    originalMessage.source,
    {
      tool: originalMessage.payload?.tool,
      input: originalMessage.payload?.input,
      output: result
    }
  );
}

// ============================================================
// MCP PROCESSOR (Main Handler)
// ============================================================

/**
 * Process an incoming MCP message
 */
async function processMCPMessage(message) {
  // 1. Validate schema
  const validation = validateMCPSchema(message);
  if (!validation.valid) {
    return createErrorResponse(message, {
      message: `Schema validation failed: ${validation.errors.join(', ')}`,
      code: MCP_ERRORS.INVALID_SCHEMA.code
    });
  }

  // 2. Check for cycles
  const cycleCheck = checkCycle(message);
  if (cycleCheck.blocked) {
    if (cycleCheck.cachedResponse) {
      return cycleCheck.cachedResponse;
    }
    return createErrorResponse(message, {
      message: cycleCheck.reason,
      code: cycleCheck.error.code
    });
  }

  // 3. Route message
  const route = routeMessage(message);

  // 4. Execute tool with retry
  const result = await executeWithRetry(
    message.payload.tool,
    message.payload.input
  );

  // 5. Create response
  if (result.success) {
    return createResponse(message, result.result);
  } else {
    return createErrorResponse(message, {
      message: result.error.message,
      code: result.errorCode || MCP_ERRORS.MAX_RETRIES_EXCEEDED.code
    });
  }
}

// ============================================================
// EXPORTS
// ============================================================

module.exports = {
  // Constants
  MCP_CONFIG,
  MCP_ERRORS,
  TOOL_SCHEMAS,
  AGENT_ROUTING,

  // Core functions
  createMCPMMessage,
  validateMCPSchema,
  validateInputSchema,
  checkCycle,
  routeMessage,
  executeWithRetry,
  processMCPMessage,

  // Utility functions
  createErrorResponse,
  createResponse,
  generateTraceId,
  hashInput,
  getBackoffDelay,
  sleep,

  // Accessors
  messageHistory
};
