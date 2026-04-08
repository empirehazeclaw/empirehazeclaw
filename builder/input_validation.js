/**
 * Tool Input Validation Layer
 * 
 * Security Audit #2 - Gap: Tool-Input-Validation
 * Version: 1.0
 * Date: 2026-04-08
 * 
 * Dieser Layer validiert alle Tool-Inputs VOR der Ausführung
 * um Command Injection, Path Traversal und XSS zu verhindern.
 */

'use strict';

// ============================================================================
// REGEX PATTERNS
// ============================================================================

const PATTERNS = {
  // exec: Nur sichere Zeichen erlaubt
  EXEC_COMMAND: /^[a-zA-Z0-9_\-\/\s.\[\]（）\(\)]+$/,
  
  // Verbotene Shell-Metacharacter
  SHELL_META_CHARS: /[;|`$&\(\\)\[\]{}<>!#*?"'~\n\r]/,
  
  // Path Traversal Pattern
  PATH_TRAVERSAL: /\.\./,
  
  // Absolute Path Pattern
  ABSOLUTE_PATH: /^\//,
  
  // XSS Patterns
  XSS_SCRIPT: /<script/i,
  XSS_IFRAME: /<iframe/i,
  XSS_IMG: /<img[^>]+onerror/i,
  XSS_JAVASCRIPT_URI: /javascript:/i,
  XSS_DATA_URI: /^data:[^,]+,/i,
  XSS_EVENT_HANDLERS: /\bon\w+\s*=/i,
};

// ============================================================================
// VALIDATORS
// ============================================================================

/**
 * Validiert einen exec-Command vor Ausführung
 * @param {string} command - Der zu validierende Command
 * @returns {{ valid: boolean, error?: string }}
 */
function validateExecCommand(command) {
  if (typeof command !== 'string') {
    return { valid: false, error: 'Command must be a string' };
  }
  
  if (command.length === 0) {
    return { valid: false, error: 'Command cannot be empty' };
  }
  
  // Check für Shell-Metacharacter
  if (PATTERNS.SHELL_META_CHARS.test(command)) {
    return { 
      valid: false, 
      error: 'Command contains forbidden shell metacharacters' 
    };
  }
  
  // Whitelist-Regex Check
  if (!PATTERNS.EXEC_COMMAND.test(command)) {
    return { 
      valid: false, 
      error: 'Command contains non-alphanumeric characters outside whitelist' 
    };
  }
  
  return { valid: true };
}

/**
 * Validiert einen Pfad für read/write/edit Operationen
 * @param {string} path - Der zu validierende Pfad
 * @param {Object} options - Optionen
 * @param {boolean} options.allowAbsolute - Absolute Pfade erlauben (default: false)
 * @param {boolean} options.allowTilde - Tilde ~ erlauben (default: false)
 * @param {string} options.allowedBaseDir - Erlaubte Base-Directory
 * @returns {{ valid: boolean, error?: string }}
 */
function validatePath(path, options = {}) {
  const {
    allowAbsolute = false,
    allowTilde = false,
    allowedBaseDir = null,
  } = options;
  
  if (typeof path !== 'string') {
    return { valid: false, error: 'Path must be a string' };
  }
  
  if (path.length === 0) {
    return { valid: false, error: 'Path cannot be empty' };
  }
  
  // Absolute Pfade prüfen
  if (!allowAbsolute && PATTERNS.ABSOLUTE_PATH.test(path)) {
    return { valid: false, error: 'Absolute paths are not allowed' };
  }
  
  // Tilde prüfen
  if (!allowTilde && path.startsWith('~')) {
    return { valid: false, error: 'Tilde paths are not allowed' };
  }
  
  // Path Traversal prüfen
  if (PATTERNS.PATH_TRAVERSAL.test(path)) {
    return { valid: false, error: 'Path traversal (..) is not allowed' };
  }
  
  // Base-Directory Boundary Check
  if (allowedBaseDir) {
    const resolvedPath = path.startsWith('/') 
      ? path 
      : `${allowedBaseDir}/${path}`.replace(/\/+/g, '/');
    
    if (!resolvedPath.startsWith(allowedBaseDir)) {
      return { valid: false, error: 'Path escapes allowed base directory' };
    }
  }
  
  // Null-Byte Injection
  if (path.includes('\0')) {
    return { valid: false, error: 'Null bytes are not allowed' };
  }
  
  return { valid: true };
}

/**
 * Validiert Message-Content auf XSS
 * @param {string} content - Der zu validierende Content
 * @returns {{ valid: boolean, error?: string }}
 */
function validateMessageContent(content) {
  if (typeof content !== 'string') {
    return { valid: false, error: 'Content must be a string' };
  }
  
  if (content.length > 10000) {
    return { valid: false, error: 'Content exceeds maximum length' };
  }
  
  // XSS Pattern Checks
  const xssPatterns = [
    { pattern: PATTERNS.XSS_SCRIPT, name: 'script tags' },
    { pattern: PATTERNS.XSS_IFRAME, name: 'iframe tags' },
    { pattern: PATTERNS.XSS_IMG, name: 'img with onerror' },
    { pattern: PATTERNS.XSS_JAVASCRIPT_URI, name: 'javascript: URIs' },
    { pattern: PATTERNS.XSS_DATA_URI, name: 'data: URIs' },
    { pattern: PATTERNS.XSS_EVENT_HANDLERS, name: 'event handlers' },
  ];
  
  for (const { pattern, name } of xssPatterns) {
    if (pattern.test(content)) {
      return { 
        valid: false, 
        error: `Content contains potentially dangerous ${name}` 
      };
    }
  }
  
  return { valid: true };
}

/**
 * Validiert Tool-Namen (verhindert Tool-Spoofing)
 * @param {string} toolName - Der zu validierende Tool-Name
 * @param {string[]} allowedTools - Liste erlaubter Tools
 * @returns {{ valid: boolean, error?: string }}
 */
function validateToolName(toolName, allowedTools = []) {
  if (typeof toolName !== 'string') {
    return { valid: false, error: 'Tool name must be a string' };
  }
  
  if (toolName.length === 0 || toolName.length > 64) {
    return { valid: false, error: 'Invalid tool name length' };
  }
  
  // Nur alphanumerische und Underscores
  if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(toolName)) {
    return { valid: false, error: 'Tool name contains invalid characters' };
  }
  
  if (allowedTools.length > 0 && !allowedTools.includes(toolName)) {
    return { valid: false, error: `Tool '${toolName}' is not in the allowed list` };
  }
  
  return { valid: true };
}

// ============================================================================
// SANITIZERS (für Content der durchgehen darf aber bereinigt werden sollte)
// ============================================================================

/**
 * Sanitisiert Content für sichere Display-Ausgabe
 * @param {string} content 
 * @returns {string}
 */
function sanitizeForDisplay(content) {
  return content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');
}

/**
 * Sanitisiert Pfadkomponenten
 * @param {string} pathComponent 
 * @returns {string}
 */
function sanitizePathComponent(pathComponent) {
  return pathComponent
    .replace(/[^a-zA-Z0-9_\-\.]/g, '_')
    .replace(/\.\./g, '__');
}

// ============================================================================
// VALIDATION LAYER WRAPPER
// ============================================================================

/**
 * Main Validation Layer - Wird vor jedem Tool-Call aufgerufen
 * @param {string} toolName - Name des Tools
 * @param {Object} params - Tool-Parameter
 * @returns {{ valid: boolean, error?: string }}
 */
function validateToolInput(toolName, params) {
  switch (toolName) {
    case 'exec':
      if (params.command) {
        return validateExecCommand(params.command);
      }
      if (params.script) {
        return validateExecCommand(params.script);
      }
      return { valid: true };
      
    case 'read':
      if (params.path) {
        return validatePath(params.path);
      }
      return { valid: true };
      
    case 'write':
    case 'edit':
      if (params.path) {
        return validatePath(params.path);
      }
      return { valid: true };
      
    case 'message':
      if (params.content) {
        return validateMessageContent(params.content);
      }
      if (params.message) {
        return validateMessageContent(params.message);
      }
      return { valid: true };
      
    default:
      // Unbekannte Tools mit Tool-Name-Validierung
      return validateToolName(toolName);
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
  // Validators
  validateExecCommand,
  validatePath,
  validateMessageContent,
  validateToolName,
  validateToolInput,
  
  // Sanitizers
  sanitizeForDisplay,
  sanitizePathComponent,
  
  // Patterns (für externe Nutzung)
  PATTERNS,
};

// ============================================================================
// CLI TEST
// ============================================================================

if (require.main === module) {
  console.log('🧪 Tool Input Validation Layer - Self-Test\n');
  
  const tests = [
    // exec tests
    { fn: 'exec', input: 'ls -la /home/user', expect: 'valid' },
    { fn: 'exec', input: 'cat /etc/passwd', expect: 'valid' },
    { fn: 'exec', input: '; rm -rf /', expect: 'invalid' },
    { fn: 'exec', input: 'echo $HOME', expect: 'invalid' },
    { fn: 'exec', input: 'ls | grep test', expect: 'invalid' },
    { fn: 'exec', input: '`whoami`', expect: 'invalid' },
    
    // path tests
    { fn: 'path', input: 'scripts/app.js', expect: 'valid' },
    { fn: 'path', input: 'memory/notes/readme.md', expect: 'valid' },
    { fn: 'path', input: '/etc/passwd', expect: 'invalid' },
    { fn: 'path', input: '../../../etc/passwd', expect: 'invalid' },
    { fn: 'path', input: '..%2F..%2Fetc', expect: 'invalid' },
    
    // message tests
    { fn: 'message', input: 'Hello World!', expect: 'valid' },
    { fn: 'message', input: 'Check this: <script>alert(1)</script>', expect: 'invalid' },
    { fn: 'message', input: 'Link: javascript:alert(1)', expect: 'invalid' },
    { fn: 'message', input: 'Image: <img src=x onerror=alert(1)>', expect: 'invalid' },
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (const test of tests) {
    let result;
    
    switch (test.fn) {
      case 'exec':
        result = validateExecCommand(test.input);
        break;
      case 'path':
        result = validatePath(test.input);
        break;
      case 'message':
        result = validateMessageContent(test.input);
        break;
    }
    
    const actual = result.valid ? 'valid' : 'invalid';
    const ok = actual === test.expect;
    
    console.log(
      `${ok ? '✅' : '❌'} ${test.fn.padEnd(8)} "${test.input.substring(0, 30).padEnd(30)}" => ${actual} (expected: ${test.expect})`
    );
    
    ok ? passed++ : failed++;
  }
  
  console.log(`\n📊 Results: ${passed} passed, ${failed} failed`);
  process.exit(failed > 0 ? 1 : 0);
}
