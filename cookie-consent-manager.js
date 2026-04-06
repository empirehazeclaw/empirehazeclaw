/**
 * DSGVO Cookie Consent Manager v2.0
 * Blocks 3rd-party scripts until user consent is given.
 * Works with GTM, GA4, Facebook Pixel, Hotjar, etc.
 * 
 * Usage: Include this script BEFORE any 3rd-party tags.
 * Scripts tagged with data-cookie-category will be blocked until consent.
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'ehc_cookie_consent_v2';
    const VERSION = '2.0';

    // Cookie categories configuration
    const CATEGORIES = {
        necessary: {
            label: 'Notwendig',
            description: 'Für die Grundfunktionen der Website erforderlich. Immer aktiv.',
            required: true,
            locked: true
        },
        analytics: {
            label: 'Analytics',
            description: 'Helfen uns zu verstehen, wie Besucher unsere Website nutzen.',
            required: false
        },
        marketing: {
            label: 'Marketing',
            description: 'Werden verwendet, um relevante Werbung anzuzeigen.',
            required: false
        }
    };

    // Default consent state (nothing enabled except necessary)
    const DEFAULT_CONSENT = {
        version: VERSION,
        timestamp: null,
        necessary: true,
        analytics: false,
        marketing: false,
        categories: ['necessary']
    };

    // Read current consent from localStorage
    function getConsent() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                return JSON.parse(stored);
            }
        } catch (e) {}
        return null;
    }

    // Save consent to localStorage
    function saveConsent(consent) {
        consent.timestamp = new Date().toISOString();
        consent.version = VERSION;
        localStorage.setItem(STORAGE_KEY, JSON.stringify(consent));
        applyConsent(consent);
        dispatchConsentEvent(consent);
    }

    // Apply consent - enable/disable scripts
    function applyConsent(consent) {
        // Block all tagged scripts until category is consented
        document.querySelectorAll('script[data-cookie-category]').forEach(function(script) {
            const category = script.getAttribute('data-cookie-category');
            if (consent.categories.includes(category)) {
                // Consent given - reload script
                const newScript = document.createElement('script');
                Array.from(script.attributes).forEach(function(attr) {
                    if (attr.name !== 'data-cookie-category') {
                        newScript.setAttribute(attr.name, attr.value);
                    }
                });
                newScript.textContent = script.textContent;
                script.parentNode.replaceChild(newScript, script);
            }
        });

        // Update dataLayer consent
        if (window.dataLayer) {
            window.dataLayer.push({
                'event': 'consent_update',
                'consent_categories': consent.categories
            });
        }
    }

    // Dispatch custom event for other scripts to listen
    function dispatchConsentEvent(consent) {
        window.dispatchEvent(new CustomEvent('cookieConsentUpdate', {
            detail: consent
        }));
    }

    // Show banner UI
    function showBanner() {
        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        const overlay = document.createElement('div');
        overlay.id = 'cookie-overlay';

        const banner = document.createElement('div');
        banner.id = 'cookie-banner';
        banner.setAttribute('role', 'dialog');
        banner.setAttribute('aria-label', 'Cookie-Einstellungen');

        banner.innerHTML = `
        <div class="cookie-content">
            <div class="cookie-header">
                <div class="cookie-title-row">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00ff88" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M12 8v4M12 16h.01"/>
                    </svg>
                    <h2>🍪 Cookie-Einstellungen</h2>
                </div>
                <p>Wir verwenden Cookies, um Ihre Erfahrung zu verbessern. Sie können Ihre Präferenzen unten anpassen.</p>
            </div>

            <div class="cookie-categories" id="cookieCategories">
                ${Object.entries(CATEGORIES).map(([key, cat]) => `
                <div class="cookie-category ${cat.required ? 'category-locked' : ''}" data-category="${key}">
                    <div class="category-info">
                        <div class="category-label-row">
                            <span class="category-name">${cat.label}</span>
                            ${cat.required ? '<span class="category-badge">Immer aktiv</span>' : ''}
                        </div>
                        <p class="category-desc">${cat.description}</p>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox" 
                               id="cat-${key}" 
                               value="${key}"
                               ${cat.required ? 'checked disabled' : ''}
                               ${getConsent()?.categories?.includes(key) ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                </div>
                `).join('')}
            </div>

            <div class="cookie-actions">
                <button id="cookieRejectAll" class="btn-cookie btn-reject">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                    Nur Notwendig
                </button>
                <button id="cookieAcceptAll" class="btn-cookie btn-accept">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    Alle akzeptieren
                </button>
            </div>

            <div class="cookie-footer-link">
                <a href="/datenschutz" class="privacy-link">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                    </svg>
                    Datenschutzerklärung
                </a>
                <button id="cookieSaveSettings" class="btn-cookie btn-save">
                    Einstellungen speichern
                </button>
            </div>
        </div>`;

        overlay.appendChild(banner);
        document.body.appendChild(overlay);

        // Inject styles
        injectStyles();

        // Event listeners
        document.getElementById('cookieRejectAll').addEventListener('click', function() {
            const consent = { ...DEFAULT_CONSENT, categories: ['necessary'], timestamp: new Date().toISOString() };
            saveConsent(consent);
            closeBanner();
        });

        document.getElementById('cookieAcceptAll').addEventListener('click', function() {
            const consent = {
                ...DEFAULT_CONSENT,
                analytics: true,
                marketing: true,
                categories: ['necessary', 'analytics', 'marketing'],
                timestamp: new Date().toISOString()
            };
            saveConsent(consent);
            closeBanner();
        });

        document.getElementById('cookieSaveSettings').addEventListener('click', function() {
            const checked = Array.from(document.querySelectorAll('#cookieCategories input:checked'))
                .map(input => input.value);
            const consent = {
                ...DEFAULT_CONSENT,
                necessary: true,
                analytics: checked.includes('analytics'),
                marketing: checked.includes('marketing'),
                categories: checked.length > 0 ? checked : ['necessary'],
                timestamp: new Date().toISOString()
            };
            saveConsent(consent);
            closeBanner();
        });

        // Close on overlay click (outside banner)
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                // Don't close, require explicit action
            }
        });

        function closeBanner() {
            document.body.style.overflow = '';
            if (document.getElementById('cookie-overlay')) {
                document.getElementById('cookie-overlay').remove();
            }
        }

        // ESC key does NOT close - user must make a choice
        document.addEventListener('keydown', function onEsc(e) {
            if (e.key === 'Escape') {
                e.preventDefault();
                // Don't allow ESC to close without consent
            }
        });
    }

    function injectStyles() {
        if (document.getElementById('cookie-styles')) return;

        const style = document.createElement('style');
        style.id = 'cookie-styles';
        style.textContent = `
            #cookie-overlay {
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(4px);
                z-index: 999997;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            #cookie-banner {
                background: #12121a;
                border: 1px solid #2a2a3a;
                border-radius: 16px;
                max-width: 520px;
                width: 100%;
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(0, 255, 136, 0.1);
                z-index: 999998;
                animation: cookieSlideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1);
            }
            @keyframes cookieSlideUp {
                from { opacity: 0; transform: translateY(30px) scale(0.97); }
                to { opacity: 1; transform: translateY(0) scale(1); }
            }
            .cookie-content { padding: 28px; }
            .cookie-header { margin-bottom: 24px; }
            .cookie-title-row {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 10px;
            }
            .cookie-header h2 {
                font-size: 20px;
                font-weight: 700;
                color: #ffffff;
                font-family: 'Syne', 'Outfit', sans-serif;
            }
            .cookie-header p {
                font-size: 14px;
                color: #8888aa;
                line-height: 1.5;
            }
            .cookie-categories { display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px; }
            .cookie-category {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 16px;
                padding: 16px;
                background: #0a0a0f;
                border: 1px solid #1e1e2e;
                border-radius: 10px;
                transition: border-color 0.2s;
            }
            .cookie-category:hover { border-color: #2a2a3a; }
            .cookie-category.category-locked { opacity: 0.7; }
            .category-label-row {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 4px;
            }
            .category-name {
                font-size: 15px;
                font-weight: 600;
                color: #ffffff;
            }
            .category-badge {
                font-size: 10px;
                font-weight: 600;
                background: rgba(0, 255, 136, 0.15);
                color: #00ff88;
                padding: 2px 7px;
                border-radius: 100px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .category-desc { font-size: 13px; color: #6666888; color: #8888aa; line-height: 1.4; }
            .toggle-switch {
                position: relative;
                display: inline-block;
                width: 48px;
                height: 26px;
                flex-shrink: 0;
            }
            .toggle-switch input { opacity: 0; width: 0; height: 0; }
            .toggle-slider {
                position: absolute;
                cursor: pointer;
                inset: 0;
                background: #2a2a3a;
                border-radius: 26px;
                transition: background 0.3s;
            }
            .toggle-slider::before {
                content: '';
                position: absolute;
                height: 20px;
                width: 20px;
                left: 3px;
                bottom: 3px;
                background: white;
                border-radius: 50%;
                transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            }
            .toggle-switch input:checked + .toggle-slider { background: #00ff88; }
            .toggle-switch input:checked + .toggle-slider::before { transform: translateX(22px); }
            .toggle-switch input:disabled + .toggle-slider { opacity: 0.5; cursor: not-allowed; }
            .cookie-actions {
                display: flex;
                gap: 10px;
                margin-bottom: 16px;
            }
            .btn-cookie {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 7px;
                padding: 12px 16px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                font-family: 'Outfit', sans-serif;
                transition: all 0.2s;
            }
            .btn-reject {
                background: #1e1e2e;
                color: #8888aa;
                border: 1px solid #2a2a3a;
            }
            .btn-reject:hover { background: #252535; color: #ffffff; }
            .btn-accept {
                background: #00ff88;
                color: #000000;
            }
            .btn-accept:hover { background: #00e077; transform: translateY(-1px); }
            .btn-save {
                background: transparent;
                color: #8888aa;
                border: 1px solid #2a2a3a;
                font-size: 13px;
            }
            .btn-save:hover { background: #1e1e2e; color: #ffffff; }
            .cookie-footer-link {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
            }
            .privacy-link {
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 13px;
                color: #8888aa;
                text-decoration: none;
                transition: color 0.2s;
            }
            .privacy-link:hover { color: #00ff88; }
            @media (max-width: 480px) {
                #cookie-overlay { padding: 12px; align-items: flex-end; }
                #cookie-banner { border-radius: 16px 16px 0 0; max-height: 85vh; }
                .cookie-actions { flex-direction: column; }
                .cookie-footer-link { flex-direction: column; align-items: flex-start; gap: 8px; }
            }
        `;
        document.head.appendChild(style);
    }

    // Public API
    window.CookieConsent = {
        getConsent: getConsent,
        showBanner: showBanner,
        showSettings: showBanner,  // alias
        acceptAll: function() {
            const consent = {
                ...DEFAULT_CONSENT,
                analytics: true,
                marketing: true,
                categories: ['necessary', 'analytics', 'marketing'],
                timestamp: new Date().toISOString()
            };
            saveConsent(consent);
        },
        rejectAll: function() {
            const consent = { ...DEFAULT_CONSENT, categories: ['necessary'], timestamp: new Date().toISOString() };
            saveConsent(consent);
        }
    };

    // Auto-initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        const existing = getConsent();
        if (existing) {
            // Consent already given - apply it
            applyConsent(existing);
            dispatchConsentEvent(existing);
        } else {
            // Show banner - don't load any 3rd party scripts
            showBanner();
        }
    });

    // Prevent 3rd-party scripts from loading automatically
    // by intercepting document.write (for synchronous scripts)
    (function() {
        const originalWrite = document.write;
        document.write = function() {
            // Allow our own scripts
            if (arguments[0] && typeof arguments[0] === 'string' && arguments[0].includes('cookie-banner')) {
                return originalWrite.apply(document, arguments);
            }
            // Block all others until consent
            const consent = getConsent();
            if (!consent) {
                console.warn('[CookieConsent] Script blocked until consent:', arguments[0] ? arguments[0].substring(0, 100) : '');
                return;
            }
            return originalWrite.apply(document, arguments);
        };
    })();

})();
