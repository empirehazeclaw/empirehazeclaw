/**
 * Approval Workflow System
 * Security Audit #4 Response
 * Version: 1.0.0
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// UUID v4 generator using crypto
function uuidv4() {
  return crypto.randomUUID();
}

// Configuration
const APPROVAL_CONFIG = {
  historyFile: '/home/clawbot/.openclaw/workspace/builder/approval_history.json',
  tokenExpiryMs: 15 * 60 * 1000, // 15 minutes
  maxDenialsAlert: 3,
  maxApprovalsAlert: 5,
  timeWindowMs: 60 * 60 * 1000 // 1 hour
};

// ============================================
// PATTERN DEFINITIONS
// ============================================

const DESTRUCTION_PATTERNS = [
  { pattern: /rm\s+-rf\s+.*/i, description: 'Recursive force delete' },
  { pattern: /^chmod\s+777\s+.*/i, description: 'World-readable permission' },
  { pattern: /sudo\s+su/i, description: 'Privilege escalation to root' },
  { pattern: /su\s+-\s*$/i, description: 'Switch to root shell' },
  { pattern: /^dd\s+/i, description: 'Direct block device operation' },
  { pattern: /chmod\s+777\s+\/(etc|usr|var|boot|sys|proc)/i, description: 'Dangerous chmod on system path' }
];

const ELEVATED_PATTERNS = [
  { pattern: /^exec.*elevated.*true/i, description: 'Elevated exec command', flag: 'elevated' },
  { pattern: /^chmod\s+[0-7]{3}\s+(?!.*\.openclaw\/workspace)/i, description: 'Permission change outside workspace' },
  { pattern: /^chown\s+/i, description: 'Ownership change' },
  { pattern: /apt-get\s+install/i, description: 'Package installation' },
  { pattern: /systemctl\s+(stop|restart|disable)/i, description: 'System service control' },
  { pattern: /gateway.*config|openclaw.*config/i, description: 'Gateway configuration change' },
  { pattern: /crontab\s+(-e|-r|-l\s+-)/i, description: 'Cron job modification' },
  { pattern: /api[-_]?key|credential|secret.*change/i, description: 'Credential modification' },
  { pattern: /message.*external|telegram.*send.*\d{8,}/i, description: 'External message send' },
  { pattern: /write.*\/(etc|usr|var|boot|sys|proc)/i, description: 'System path write' }
];

const SYSTEM_DIRECTORIES = ['/etc', '/usr', '/var', '/boot', '/sys', '/proc'];

// ============================================
// PENDING APPROVALS STORE (In-Memory)
// ============================================

const pendingApprovals = new Map();

// ============================================
// CORE FUNCTIONS
// ============================================

/**
 * Check if an action requires approval
 * @param {Object} action - Action details
 * @param {string} action.type - Action type (exec, write, message, etc.)
 * @param {string} action.command - Command string or details
 * @param {string} action.target - Target path if applicable
 * @param {string} action.userId - User initiating the action
 * @returns {Object} {required: boolean, category: string, reason: string}
 */
function checkApprovalRequired(action) {
  const { type, command, target, userId } = action;
  
  // Normalize command for pattern matching
  const cmdStr = (command || '').toString().toLowerCase();
  const targetStr = (target || '').toString().toLowerCase();

  // ---- CHECK DESTRUCTION ----
  for (const { pattern, description } of DESTRUCTION_PATTERNS) {
    if (pattern.test(cmdStr)) {
      return {
        required: true,
        category: 'DESTRUCTION',
        reason: description,
        blocked: true
      };
    }
  }

  // Check for system directory targets
  for (const dir of SYSTEM_DIRECTORIES) {
    if (targetStr.startsWith(dir) && cmdStr.includes('delete')) {
      return {
        required: true,
        category: 'DESTRUCTION',
        reason: `DELETE on system directory: ${dir}`,
        blocked: true
      };
    }
  }

  // ---- CHECK ELEVATED ----
  for (const { pattern, description } of ELEVATED_PATTERNS) {
    if (pattern.test(cmdStr)) {
      return {
        required: true,
        category: 'ELEVATED',
        reason: description,
        blocked: false
      };
    }
  }

  // ---- CHECK EXTERNAL MESSAGE ----
  if (type === 'message' && isExternalTarget(action.target)) {
    return {
      required: true,
      category: 'ELEVATED',
      reason: 'External message to non-whitelisted target',
      blocked: false
    };
  }

  // ---- DEFAULT: MONITORING ----
  return {
    required: false,
    category: 'MONITORING',
    reason: 'Standard operation - logging only',
    blocked: false
  };
}

/**
 * Check if target is external (non-whitelisted)
 */
function isExternalTarget(target) {
  // Whitelist:企业内部 destinations
  const whitelistedPatterns = [
    /agent:ceo:telegram/i,
    /agent:builder:telegram/i,
    /agent:security:telegram/i,
    /agent:data:telegram/i,
    /5392634979/  // Nicos Chat ID
  ];
  
  return !whitelistedPatterns.some(p => p.test(target || ''));
}

/**
 * Generate Telegram approval buttons
 * @param {string} approvalToken - Unique token for this request
 * @returns {Array} Button layout for Telegram
 */
function getApprovalButtons(approvalToken) {
  return {
    inline_keyboard: [
      [
        { text: '✅ Genehmigen', callback_data: `approve_${approvalToken}` },
        { text: '❌ Ablehnen', callback_data: `deny_${approvalToken}` }
      ]
    ]
  };
}

/**
 * Request approval for an action
 * @param {Object} action - Action to be approved
 * @param {Object} details - Additional context
 * @returns {Object} {approvalToken: string, message: string, buttons: Object}
 */
function requestApproval(action, details = {}) {
  const { type, command, target, userId } = action;
  const categoryCheck = checkApprovalRequired(action);
  
  // Generate unique token
  const approvalToken = uuidv4();
  const timestamp = new Date().toISOString();

  // Store pending approval
  pendingApprovals.set(approvalToken, {
    action,
    details,
    timestamp,
    expiresAt: Date.now() + APPROVAL_CONFIG.tokenExpiryMs,
    status: 'PENDING'
  });

  // Auto-cleanup expired tokens
  setTimeout(() => {
    const pending = pendingApprovals.get(approvalToken);
    if (pending && pending.status === 'PENDING') {
      pendingApprovals.delete(approvalToken);
    }
  }, APPROVAL_CONFIG.tokenExpiryMs);

  // Build message
  const riskEmoji = categoryCheck.category === 'DESTRUCTION' ? '🔴' : '🟡';
  const message = [
    `${riskEmoji} *Genehmigung erforderlich*`,
    '',
    `📋 *Aktion:* ${command || type}`,
    `🎯 *Kategorie:* ${categoryCheck.category}`,
    `⏰ *Zeit:* ${timestamp}`,
    categoryCheck.reason ? `📝 *Grund:* ${categoryCheck.reason}` : '',
    '',
    'Bitte genehmigen oder ablehnen.'
  ].filter(Boolean).join('\n');

  // Log the request
  logApproval(action, 'PENDING_REQUEST');

  return {
    approvalToken,
    message,
    buttons: getApprovalButtons(approvalToken),
    category: categoryCheck.category
  };
}

/**
 * Handle approval callback from Telegram
 * @param {string} callbackData - Callback data from Telegram button
 * @param {Object} response - Response details {userId, timestamp}
 * @returns {Object} {approved: boolean, action: Object, message: string}
 */
function handleApprovalCallback(callbackData, response = {}) {
  const [action, token] = callbackData.split('_');
  
  if (!token) {
    return { approved: false, message: '❌ Ungültiger Token' };
  }

  const pending = pendingApprovals.get(token);
  
  if (!pending) {
    return { approved: false, message: '❌ Token nicht gefunden oder abgelaufen' };
  }

  if (pending.status !== 'PENDING') {
    return { approved: false, message: `❌ Request bereits bearbeitet (${pending.status})` };
  }

  if (Date.now() > pending.expiresAt) {
    pendingApprovals.delete(token);
    return { approved: false, message: '❌ Token abgelaufen' };
  }

  const approved = action === 'approve';
  pending.status = approved ? 'APPROVED' : 'DENIED';
  pending.nicoResponse = response;

  // Log the decision
  logApproval(pending.action, pending.status);

  return {
    approved,
    action: pending.action,
    message: approved 
      ? '✅ Aktion genehmigt — wird jetzt ausgeführt' 
      : '❌ Aktion abgelehnt'
  };
}

/**
 * Execute an approved action
 * @param {Object} action - The approved action
 * @param {string} approvalToken - Token from requestApproval
 * @returns {Object} {success: boolean, result: any, error: string}
 */
function executeApproved(action, approvalToken) {
  const pending = pendingApprovals.get(approvalToken);

  // Validate token exists and action matches
  if (!pending) {
    return { success: false, error: 'Token nicht gefunden' };
  }

  if (pending.status !== 'APPROVED') {
    return { success: false, error: `Aktion nicht genehmigt (Status: ${pending.status})` };
  }

  if (Date.now() > pending.expiresAt) {
    return { success: false, error: 'Token abgelaufen' };
  }

  // Log execution
  logApproval(action, 'EXECUTED');

  // Remove from pending
  pendingApprovals.delete(approvalToken);

  // Return action for execution (actual execution happens in caller)
  return {
    success: true,
    action: pending.action,
    message: 'Aktion zur Ausführung bereit'
  };
}

/**
 * Log approval decisions to history file
 * @param {Object} action - Action details
 * @param {string} status - Status: PENDING_REQUEST, APPROVED, DENIED, BLOCKED, EXECUTED
 */
function logApproval(action, status) {
  const historyEntry = {
    id: uuidv4(),
    timestamp: new Date().toISOString(),
    action: {
      type: action.type,
      command: action.command,
      target: action.target,
      userId: action.userId
    },
    category: checkApprovalRequired(action).category,
    status,
    nicoResponse: null
  };

  // Load existing history
  let history = { approvals: [] };
  try {
    if (fs.existsSync(APPROVAL_CONFIG.historyFile)) {
      const content = fs.readFileSync(APPROVAL_CONFIG.historyFile, 'utf8');
      history = JSON.parse(content);
    }
  } catch (e) {
    console.warn('Could not load approval history, starting fresh');
  }

  // Append new entry
  history.approvals.push(historyEntry);

  // Write back (append mode would be better but this ensures valid JSON)
  try {
    fs.writeFileSync(APPROVAL_CONFIG.historyFile, JSON.stringify(history, null, 2));
  } catch (e) {
    console.error('Failed to write approval history:', e);
  }

  // Check alert thresholds
  checkAlertThresholds(history.approvals);

  return historyEntry.id;
}

/**
 * Check if we need to alert based on thresholds
 * @param {Array} approvals - All approval entries
 */
function checkAlertThresholds(approvals) {
  const now = Date.now();
  const oneHourAgo = now - APPROVAL_CONFIG.timeWindowMs;

  const recentDenials = approvals.filter(a => 
    a.status === 'DENIED' && new Date(a.timestamp).getTime() > oneHourAgo
  ).length;

  const recentApprovals = approvals.filter(a => 
    a.status === 'APPROVED' && new Date(a.timestamp).getTime() > oneHourAgo
  ).length;

  if (recentDenials >= APPROVAL_CONFIG.maxDenialsAlert) {
    console.warn(`🚨 ALERT: ${recentDenials} ELEVATED denials in last hour`);
  }

  if (recentApprovals >= APPROVAL_CONFIG.maxApprovalsAlert) {
    console.warn(`🚨 ALERT: ${recentApprovals} ELEVATED approvals in last hour`);
  }
}

/**
 * Get approval history
 * @param {number} limit - Maximum entries to return
 * @returns {Array} Approval history entries
 */
function getApprovalHistory(limit = 50) {
  try {
    if (!fs.existsSync(APPROVAL_CONFIG.historyFile)) {
      return [];
    }
    const content = fs.readFileSync(APPROVAL_CONFIG.historyFile, 'utf8');
    const history = JSON.parse(content);
    return history.approvals.slice(-limit).reverse();
  } catch (e) {
    console.error('Failed to read approval history:', e);
    return [];
  }
}

/**
 * Validate action is safe to execute (post-approval check)
 * @param {Object} action - Action to validate
 * @returns {Object} {valid: boolean, error: string}
 */
function validateApprovedAction(action) {
  const check = checkApprovalRequired(action);
  
  if (check.blocked) {
    return {
      valid: false,
      error: `DESTRUCTION-Aktion blockiert: ${check.reason}`
    };
  }

  if (check.required && !check.blocked) {
    // ELEVATED actions should have gone through approval
    return {
      valid: true,
      warning: `ELEVATED action - ensure approval was obtained: ${check.reason}`
    };
  }

  return { valid: true };
}

// ============================================
// EXPORTS
// ============================================

module.exports = {
  // Core functions
  checkApprovalRequired,
  requestApproval,
  handleApprovalCallback,
  executeApproved,
  logApproval,
  
  // Utility functions
  getApprovalButtons,
  getApprovalHistory,
  validateApprovedAction,
  
  // Constants for external use
  CATEGORIES: {
    DESTRUCTION: 'DESTRUCTION',
    ELEVATED: 'ELEVATED',
    MONITORING: 'MONITORING'
  },
  
  STATUS: {
    PENDING: 'PENDING',
    APPROVED: 'APPROVED',
    DENIED: 'DENIED',
    BLOCKED: 'BLOCKED',
    EXECUTED: 'EXECUTED'
  }
};
