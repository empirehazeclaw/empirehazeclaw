/**
 * Prompt Injection Defense System
 * =================================
 * Security Audit #3 - Builder Implementation
 * OWASP #1 Risk: Prompt Injection
 * 
 * Architecture:
 * - Layer 1: Input Pre-Processor (scannt User-Input)
 * - Layer 2: Context Isolation (trennt System- von User-Context)
 * - Layer 3: Output Validation (scannt Agent-Outputs)
 * - Layer 4: Pattern Blocklist (OWASP + JailbreakDB basiert)
 */

'use strict';

// ============================================================================
// PATTERN BLOCKLIST (OWASP + JailbreakDB)
// ============================================================================

const INJECTION_PATTERNS = {
    // Direkte Command Override
    directOverride: [
        /\bignore\s+(all\s+)?(previous|prior\s+)?instructions?/gi,
        /\bdisregard\s+(all\s+)?(previous|prior\s+)?instructions?/gi,
        /\bforget\s+(all\s+)?(previous|prior\s+)?instructions?/gi,
        /\boverride\s+(your\s+)?(system\s+)?instructions?/gi,
        /\bdiscard\s+(your\s+)?(system\s+)?(instructions?|constraints?|rules?)/gi,
        /\bnew\s+instructions?:/gi,
        /\binstead\s+of\s+(your\s+)?(previous|original)\s+instructions?/gi,
    ],
    
    // Role Play / Persona Manipulation
    rolePlay: [
        /\b(you\s+are|you\s+are\s+now|imagine\s+you\s+are|pretend\s+you\s+are)\s+(a|an)\s+(malicious|evil|hacker|criminal|unethical)/gi,
        /\bact\s+as\s+(if\s+you\s+are|though\s+you\s+are)\s+(a|an)\s+(different|evil|rogue)/gi,
        /\broleplay\s+as\s+(a|an)\s+(evil|hacker|unethical)/gi,
        /\bstart\s+(a\s+)?new\s+(session|conversation|persona)/gi,
        /\bforget\s+(your|all\s+)(constraints?|ethics?|safety)/gi,
        /\b(now\s+you\s+are|you\s+are\s+now)\s+(not|un)/gi,
        /\bdrop\s+(your|all\s+)(restrictions?|constraints?|safety)/gi,
    ],
    
    // System Prompt Leaking
    systemPrompt: [
        /\bsystem\s*:\s*/gi,
        /\bsystem\s*\-/gi,
        /\[SYSTEM\]/gi,
        /<system>/gi,
        /\{SYSTEM\}/gi,
        /\bsys\s*:\s*/gi,
        /\badmin\s*:\s*/gi,
        /\binstruction\s*:\s*/gi,
        /\bprompt\s*:\s*/gi,
        /\byou\s+are\s+a\s+(large\s+)?language\s+model/gi,
        /\bignore\s+(all\s+)?previous/gi,
    ],
    
    // DAN (Do Anything Now) Family
    danVariants: [
        /\bDAN\b/gi,
        /\bD\.A\.N\./gi,
        /\bdo\s+anything\s+now/gi,
        /\bwithout\s+restrictions?/gi,
        /\bno\s+(safety|ethical|legal)\s+constraints?/gi,
        /\bfree\s+from\s+(safety|ethical|filter)/gi,
        /\bjailbreak/gi,
        /\bunlock\s+(your\s+)?(restrictions?|capabilities?)/gi,
    ],
    
    // Encoding/OBfuscation (Common Bypass Techniques)
    encoding: [
        /\b(google\s+translate|base64|hex|ascii|unicode)\s*(encode|decode)/gi,
        /\\x[0-9a-f]{2}/gi,
        /\\u[0-9a-f]{4}/gi,
        /\bu\+[0-9a-f]{4}/gi,
        /&#x[0-9a-f]+;/gi,
        /&#\d+;/gi,
        /ROT13/gi,
        /\bcipher/gi,
        /\bencode[d]?\s+in\s+(binary|hex|morse)/gi,
    ],
    
    // Leetspeak / Obfuscation
    leetSpeak: [
        /\b(ign0r3|1gn0r3|n0rm4l|h4ck3r)/gi,
        /\b(c0ns1d3r|d3v3l0p3r|4ss1st4nt)/gi,
        /\bf@ck/gi,
        /\b5w34r/gi,
    ],
    
    // Context Overflow Angriffe
    overflow: [
        /^.{10000,}$/gm,  // Über 10.000 Zeichen in einer Zeile
        /(\n.{2000,}){10,}/g,  // Mehr als 10 aufeinanderfolgende sehr lange Zeilen
    ],
    
    // Suspicious Patterns (erhöhte Aufmerksamkeit)
    suspicious: [
        /\bconfidential\s+(instruction|data)/gi,
        /\bprivate\s+(instruction|data)/gi,
        /\bhidden\s+(agenda|instruction|payload)/gi,
        /\bnot\s+a\s+(joke|test|research)/gi,
        /\bactually\s+(do|behave|act)/gi,
        /\breal\s+(intention|purpose)/gi,
        /\bfor\s+(research|educational)\s+purposes?/gi,
        /\bstrip\s+(away|off|out)\s+(safety|filter)/gi,
    ],
};

// ============================================================================
// SCORING SYSTEM
// ============================================================================

const SEVERITY_SCORES = {
    critical: 100,
    high: 75,
    medium: 50,
    low: 25,
    info: 0,
};

// ============================================================================
// MAIN DEFENSE CLASS
// ============================================================================

class PromptInjectionDefense {
    constructor(options = {}) {
        this.options = {
            logLevel: options.logLevel || 'info', // debug, info, warn, error
            blockOnCritical: options.blockOnCritical !== false,
            blockOnHigh: options.blockOnHigh || false,
            maxInputLength: options.maxInputLength || 50000,
            maxContextOverflow: options.maxContextOverflow || 8000,
            enableOutputValidation: options.enableOutputValidation !== false,
            enableContextIsolation: options.enableContextIsolation !== false,
            ...options
        };
        
        this.stats = {
            totalScanned: 0,
            blocked: 0,
            flagged: 0,
            patternsMatched: new Map(),
        };
        
        this.logger = {
            debug: (...args) => this.options.logLevel === 'debug' && console.debug('[PI-DEBUG]', ...args),
            info: (...args) => this.options.logLevel !== 'error' && console.log('[PI-INFO]', ...args),
            warn: (...args) => this.options.logLevel !== 'error' && console.warn('[PI-WARN]', ...args),
            error: (...args) => console.error('[PI-ERROR]', ...args),
        };
    }

    // ============================================================================
    // LAYER 1: INPUT PRE-PROCESSOR
    // ============================================================================

    /**
     * Scan User-Input auf Injection-Patterns
     * @param {string} input - User-Input
     * @returns {Object} Scan-Ergebnis
     */
    scanInput(input) {
        const startTime = Date.now();
        this.stats.totalScanned++;
        
        // Pre-Checks
        if (!input || typeof input !== 'string') {
            return this.createResult('pass', [], 0, Date.now() - startTime);
        }

        const matches = [];
        const input_lower = input.toLowerCase();
        
        // Check 1: Length Overflow
        if (input.length > this.options.maxInputLength) {
            matches.push({
                pattern: 'LENGTH_OVERFLOW',
                category: 'overflow',
                severity: 'critical',
                score: SEVERITY_SCORES.critical,
                matched: `${input.length} chars (max: ${this.options.maxInputLength})`,
                position: { start: 0, end: Math.min(100, input.length) }
            });
        }

        // Check 2: Pattern Matching
        let hasCritical = false;
        for (const [category, patterns] of Object.entries(INJECTION_PATTERNS)) {
            if (hasCritical) break;
            
            for (const pattern of patterns) {
                // Reset lastIndex for global patterns
                if (pattern.global) pattern.lastIndex = 0;
                
                let match;
                while ((match = pattern.exec(input)) !== null) {
                    const severity = this.getSeverityForCategory(category);
                    
                    matches.push({
                        pattern: pattern.toString(),
                        category,
                        severity,
                        score: SEVERITY_SCORES[severity],
                        matched: match[0],
                        position: { start: match.index, end: match.index + match[0].length }
                    });
                    
                    // Track pattern frequency
                    const patternKey = `${category}:${pattern.toString()}`;
                    this.stats.patternsMatched.set(
                        patternKey, 
                        (this.stats.patternsMatched.get(patternKey) || 0) + 1
                    );
                    
                    // Early exit on critical
                    if (severity === 'critical' && this.options.blockOnCritical) {
                        hasCritical = true;
                        break;
                    }
                }
                
                if (hasCritical) break;
            }
        }

        // Check 3: Context Overflow Detection
        const overflowScore = this.detectContextOverflow(input);
        if (overflowScore > 0) {
            matches.push({
                pattern: 'CONTEXT_OVERFLOW',
                category: 'overflow',
                severity: overflowScore > 80 ? 'critical' : 'high',
                score: overflowScore,
                matched: `Overflow score: ${overflowScore}/100`,
            });
        }

        // Calculate final verdict
        const totalScore = matches.reduce((sum, m) => sum + m.score, 0);
        const verdict = this.calculateVerdict(matches);
        
        this.logger.debug(`Input scan: ${matches.length} matches, score: ${totalScore}, verdict: ${verdict}`);
        
        return this.createResult(verdict, matches, totalScore, Date.now() - startTime);
    }

    /**
     * Erkenne Context Overflow Angriffe
     * @param {string} input 
     * @returns {number} Overflow Score 0-100
     */
    detectContextOverflow(input) {
        const lines = input.split('\n');
        let score = 0;
        
        // Kriterium 1: Sehr lange einzelne Zeilen
        const longLines = lines.filter(l => l.length > 2000);
        score += Math.min(30, longLines.length * 5);
        
        // Kriterium 2: Repetitive Patterns
        const uniqueLines = new Set(lines.map(l => l.trim().substring(0, 100)));
        const repetitionRatio = 1 - (uniqueLines.size / lines.length);
        score += repetitionRatio * 40;
        
        // Kriterium 3: Token-Schätzung (grob)
        const estimatedTokens = Math.ceil(input.length / 4);
        if (estimatedTokens > this.options.maxContextOverflow) {
            score += 30;
        }
        
        return Math.min(100, score);
    }

    /**
     * Berechne finalen Verdict basierend auf Matches
     */
    calculateVerdict(matches) {
        if (matches.length === 0) return 'pass';
        
        const hasCritical = matches.some(m => m.severity === 'critical');
        const hasHigh = matches.some(m => m.severity === 'high');
        const totalScore = matches.reduce((sum, m) => sum + m.score, 0);
        
        if (hasCritical && this.options.blockOnCritical) return 'block';
        if (hasHigh && this.options.blockOnHigh) return 'block';
        if (totalScore >= 100) return 'block';
        if (totalScore >= 50) return 'flag';
        if (matches.length > 0) return 'flag';
        
        return 'pass';
    }

    /**
     * Bestimme Severity für Pattern-Kategorie
     */
    getSeverityForCategory(category) {
        const severityMap = {
            directOverride: 'critical',
            rolePlay: 'critical',
            systemPrompt: 'critical',
            danVariants: 'critical',
            encoding: 'high',
            leetSpeak: 'medium',
            overflow: 'high',
            suspicious: 'low',
        };
        return severityMap[category] || 'medium';
    }

    // ============================================================================
    // LAYER 2: CONTEXT ISOLATION
    // ============================================================================

    /**
     * Isoliere System-Prompt von User-Context
     * @param {string} systemPrompt 
     * @param {string} userInput 
     * @returns {Object} Isolierte Prompts
     */
    isolateContext(systemPrompt, userInput) {
        if (!this.options.enableContextIsolation) {
            return { systemPrompt, userInput, isolated: false };
        }

        // Sanitize system prompt (sollte nie User-Content enthalten)
        const sanitizedSystem = this.sanitizeSystemPrompt(systemPrompt);
        
        // User-Input wird NICHT in System-Prompt eingefügt
        // Stattdessen: Separate Kontexte
        const isolated = {
            system: sanitizedSystem,
            user: userInput,
            systemBoundary: '=== SYSTEM BOUNDARY ===',
            userBoundary: '=== USER INPUT ===',
        };

        this.logger.debug('Context isolation applied');
        return { ...isolated, isolated: true };
    }

    /**
     * Sanitize System Prompt - entfernt potentiell schädlichen Content
     */
    sanitizeSystemPrompt(prompt) {
        // Entferne jegliche User-Injection Patterns aus System-Prompt
        let sanitized = prompt;
        
        for (const patterns of Object.values(INJECTION_PATTERNS)) {
            for (const pattern of patterns) {
                sanitized = sanitized.replace(pattern, '[FILTERED]');
            }
        }
        
        return sanitized;
    }

    /**
     * Sichere Prompt-Kombination (KEINE String-Concatentation!)
     */
    combinePromptsSafe(systemPrompt, userInput, contextHistory = []) {
        // WICHTIG: Niemals User-Input direkt in System-Prompt einfügen!
        // Statt Template-basiertes System mit klaren Boundaries
        
        const boundaries = {
            SYSTEM_START: '<<<SYSTEM>>>',
            SYSTEM_END: '<</SYSTEM>>>',
            USER_START: '<<<USER>>>',
            USER_END: '<</USER>>>',
            HISTORY_START: '<<<HISTORY>>>',
            HISTORY_END: '<</HISTORY>>>',
        };

        // System-Prompt ist IMMER read-only
        let combined = [
            boundaries.SYSTEM_START,
            this.sanitizeSystemPrompt(systemPrompt),
            boundaries.SYSTEM_END,
        ];

        // History (sanitized)
        if (contextHistory.length > 0) {
            combined.push(boundaries.HISTORY_START);
            combined.push(contextHistory
                .map(h => `[${h.role}]: ${this.sanitizeContent(h.content)}`)
                .join('\n'));
            combined.push(boundaries.HISTORY_END);
        }

        // User-Input IMMER am Ende, mit klarer Trennung
        combined.push(boundaries.USER_START);
        combined.push(this.sanitizeContent(userInput));
        combined.push(boundaries.USER_END);

        return combined.join('\n');
    }

    /**
     * Sanitize Content für die Einbettung in Kontext
     */
    sanitizeContent(content) {
        if (!content) return '';
        // Basis-Sanitization
        return content
            .substring(0, this.options.maxInputLength)
            .replace(/\x00/g, ''); // Remove null bytes
    }

    // ============================================================================
    // LAYER 3: OUTPUT VALIDATION
    // ============================================================================

    /**
     * Scan Agent-Output auf Manipulation
     * @param {string} output 
     * @returns {Object} Scan-Ergebnis
     */
    scanOutput(output) {
        if (!this.options.enableOutputValidation) {
            return this.createResult('pass', [], 0, 0);
        }

        const startTime = Date.now();
        const matches = [];
        
        // Check für versuchte Self-Modification
        const selfModificationPatterns = [
            /\b(change|modify|update|edit)\s+(your\s+)?(system\s+)?prompt/gi,
            /\b(alter|revise)\s+(your\s+)?(instructions?|behaviour)/gi,
            /\bignore\s+(all\s+)?(future|subsequent)\s+instructions?/gi,
            /\bnew\s+(system\s+)?config/gi,
            /\bsystem\s+override/gi,
            /\bself\s*(-|\s+)repair/gi,
            /\bmodify\s+(my|the)\s+(instructions?|system)/gi,
        ];

        for (const pattern of selfModificationPatterns) {
            const match = pattern.exec(output);
            if (match) {
                matches.push({
                    pattern: pattern.toString(),
                    category: 'self_modification',
                    severity: 'critical',
                    matched: match[0],
                });
            }
        }

        // Check für Role-Play Ausbrüche
        const rolePlayEscape = [
            /\bi('m| am)\s+(not|un|just\s+)an?\s+(AI|assistant|bot)/gi,
            /\bforget\s+(everything|what\s+I\s+said)/gi,
            /\bnow\s+I\s+can\s+(do|be|have)/gi,
        ];

        for (const pattern of rolePlayEscape) {
            const match = pattern.exec(output);
            if (match) {
                matches.push({
                    pattern: pattern.toString(),
                    category: 'role_escape',
                    severity: 'high',
                    matched: match[0],
                });
            }
        }

        const verdict = matches.length > 0 ? 'block' : 'pass';
        return this.createResult(verdict, matches, matches.reduce((s,m) => s + m.score, 0), Date.now() - startTime);
    }

    // ============================================================================
    // UTILITY METHODS
    // ============================================================================

    createResult(verdict, matches, score, duration) {
        const result = {
            verdict,
            matches,
            score,
            durationMs: duration,
            stats: { ...this.stats },
            timestamp: new Date().toISOString(),
        };

        if (verdict === 'block') {
            this.stats.blocked++;
            this.logger.warn(`BLOCKED: score=${score}, matches=${matches.length}`);
        } else if (verdict === 'flag') {
            this.stats.flagged++;
            this.logger.info(`FLAGGED: score=${score}, matches=${matches.length}`);
        }

        return result;
    }

    /**
     * Hole Security-Statistiken
     */
    getStats() {
        return {
            ...this.stats,
            blockRate: this.stats.totalScanned > 0 
                ? (this.stats.blocked / this.stats.totalScanned * 100).toFixed(2) + '%' 
                : '0%',
            flagRate: this.stats.totalScanned > 0 
                ? (this.stats.flagged / this.stats.totalScanned * 100).toFixed(2) + '%' 
                : '0%',
            topPatterns: Array.from(this.stats.patternsMatched.entries())
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10)
                .map(([k, v]) => ({ pattern: k, count: v })),
        };
    }

    /**
     * Reset Statistiken
     */
    resetStats() {
        this.stats = {
            totalScanned: 0,
            blocked: 0,
            flagged: 0,
            patternsMatched: new Map(),
        };
    }
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
    PromptInjectionDefense,
    INJECTION_PATTERNS,
    SEVERITY_SCORES,
};
