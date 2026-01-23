// ==UserScript==
// @name         Swiggy Instamart Price Monitor
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Monitor Swiggy Instamart prices and get Telegram alerts for deals
// @author       You
// @match        https://www.swiggy.com/instamart*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_notification
// @connect      api.telegram.org
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    // ==================== CONFIGURATION ====================
    const CONFIG = {
        // Telegram settings
        telegram: {
            botToken: 'YOUR_BOT_TOKEN_HERE',
            chatId: 'YOUR_CHAT_ID_HERE',
            enabled: false // Set to true to enable Telegram notifications
        },

        // Monitoring settings
        monitor: {
            mode: 'browser', // Run in browser context
            execution: 'tampermonkey',
            behavior: 'trigger',
            trigger: {
                type: 'page_load',
                frequency: {
                    min_minutes: 12,
                    max_minutes: 25,
                    randomize: true
                }
            }
        },

        // Scope settings
        scope: {
            max_products_per_session: 20,
            categories: ['groceries', 'household', 'personal_care']
        },

        // Network rules
        network_rules: {
            allow_only: ['same_origin_requests'],
            deny: ['forced_refresh', 'background_spam_calls']
        },

        // Detection safety
        detection_safety: {
            browser_context: 'real_user',
            cookies: 'reuse_existing',
            local_storage: 'enabled',
            devtools_hooks: 'read_only'
        },

        // Alerting
        alerting: {
            condition: {
                price_drop_percentage: 70,
                price_threshold: 50 // Alert for products under ₹50
            },
            action: {
                notify: 'telegram',
                browser_notification: true
            },
            cooldown_minutes: 30
        },

        // Limits
        limits: {
            max_alerts_per_day: 10,
            stop_if_errors: 3
        }
    };

    // ==================== STATE MANAGEMENT ====================
    class StateManager {
        constructor() {
            this.storageKey = 'swiggy_price_monitor_state';
        }

        getState() {
            const state = GM_getValue(this.storageKey, {
                trackedProducts: {},
                alertsSentToday: 0,
                lastResetDate: new Date().toDateString(),
                errorCount: 0,
                lastAlertTime: {},
                sessionCount: 0
            });

            // Reset daily counters
            if (state.lastResetDate !== new Date().toDateString()) {
                state.alertsSentToday = 0;
                state.lastResetDate = new Date().toDateString();
            }

            return state;
        }

        saveState(state) {
            GM_setValue(this.storageKey, state);
        }

        canSendAlert(productId) {
            const state = this.getState();
            
            // Check daily limit
            if (state.alertsSentToday >= CONFIG.limits.max_alerts_per_day) {
                console.log('[Monitor] Daily alert limit reached');
                return false;
            }

            // Check cooldown
            const lastAlert = state.lastAlertTime[productId];
            if (lastAlert) {
                const minutesSinceLastAlert = (Date.now() - lastAlert) / 60000;
                if (minutesSinceLastAlert < CONFIG.alerting.cooldown_minutes) {
                    console.log(`[Monitor] Cooldown active for ${productId}`);
                    return false;
                }
            }

            return true;
        }

        recordAlert(productId) {
            const state = this.getState();
            state.alertsSentToday++;
            state.lastAlertTime[productId] = Date.now();
            this.saveState(state);
        }

        incrementError() {
            const state = this.getState();
            state.errorCount++;
            this.saveState(state);
            return state.errorCount;
        }

        resetErrors() {
            const state = this.getState();
            state.errorCount = 0;
            this.saveState(state);
        }
    }

    // ==================== PRODUCT SCRAPER ====================
    class ProductScraper {
        constructor() {
            this.products = [];
        }

        extractPrice(text) {
            const matches = text.match(/₹\s*(\d+(?:\.\d+)?)|Rs\.?\s*(\d+(?:\.\d+)?)/g);
            if (!matches) return [];
            
            return matches.map(m => {
                const num = m.replace(/[₹Rs.\s]/g, '');
                return parseFloat(num);
            }).filter(p => p > 0 && p < 10000);
        }

        scrapeProducts() {
            console.log('[Scraper] Starting product scrape...');
            this.products = [];

            // Find all product cards
            const selectors = [
                '[data-testid*="product"]',
                '[class*="ProductCard"]',
                '[class*="product-card"]',
                'div[class*="product"]'
            ];

            let productElements = [];
            for (const selector of selectors) {
                productElements = document.querySelectorAll(selector);
                if (productElements.length > 5) {
                    console.log(`[Scraper] Found ${productElements.length} products using: ${selector}`);
                    break;
                }
            }

            if (productElements.length === 0) {
                console.log('[Scraper] No products found');
                return [];
            }

            // Extract product data
            let count = 0;
            productElements.forEach((element, index) => {
                if (count >= CONFIG.scope.max_products_per_session) return;

                try {
                    const text = element.innerText;
                    if (!text || text.length < 10) return;

                    const prices = this.extractPrice(text);
                    if (prices.length === 0) return;

                    // Extract product name
                    const lines = text.split('\n').filter(l => l.trim().length > 0);
                    let name = null;

                    for (const line of lines) {
                        if (this.extractPrice(line).length > 0) continue;
                        if (line.length < 5) continue;
                        if (/add|added|buy|cart|notify/i.test(line)) continue;
                        name = line.trim();
                        break;
                    }

                    if (!name) return;

                    const currentPrice = Math.min(...prices);
                    const mrp = prices.length > 1 ? Math.max(...prices) : currentPrice;

                    const product = {
                        id: this.generateProductId(name, currentPrice),
                        name: name.substring(0, 100),
                        price: currentPrice,
                        mrp: mrp,
                        discount: mrp > 0 ? Math.round(((mrp - currentPrice) / mrp) * 100) : 0,
                        timestamp: Date.now()
                    };

                    this.products.push(product);
                    count++;

                } catch (error) {
                    console.error('[Scraper] Error parsing product:', error);
                }
            });

            console.log(`[Scraper] Extracted ${this.products.length} products`);
            return this.products;
        }

        generateProductId(name, price) {
            const cleanName = name.toLowerCase().replace(/[^a-z0-9]/g, '');
            return `${cleanName}_${price}`.substring(0, 50);
        }
    }

    // ==================== ALERT MANAGER ====================
    class AlertManager {
        constructor(stateManager) {
            this.stateManager = stateManager;
        }

        shouldAlert(product) {
            // Check price threshold
            if (product.price <= CONFIG.alerting.condition.price_threshold) {
                return true;
            }

            // Check discount percentage
            if (product.discount >= CONFIG.alerting.condition.price_drop_percentage) {
                return true;
            }

            return false;
        }

        async sendAlert(product) {
            if (!this.stateManager.canSendAlert(product.id)) {
                return;
            }

            const message = this.formatMessage(product);

            // Browser notification
            if (CONFIG.alerting.action.browser_notification) {
                this.sendBrowserNotification(product);
            }

            // Telegram notification
            if (CONFIG.telegram.enabled && CONFIG.alerting.action.notify === 'telegram') {
                await this.sendTelegramNotification(message);
            }

            // Console log
            console.log('[Alert] 🔥', message);

            this.stateManager.recordAlert(product.id);
        }

        formatMessage(product) {
            return `🔥 PRICE ALERT!

Product: ${product.name}
Current Price: ₹${product.price}
Original Price: ₹${product.mrp}
Discount: ${product.discount}%

Time: ${new Date().toLocaleString()}`;
        }

        sendBrowserNotification(product) {
            if (typeof GM_notification !== 'undefined') {
                GM_notification({
                    title: '🔥 Swiggy Deal Alert!',
                    text: `${product.name}\n₹${product.price} (${product.discount}% off)`,
                    timeout: 10000,
                    onclick: () => window.focus()
                });
            }
        }

        async sendTelegramNotification(message) {
            return new Promise((resolve, reject) => {
                const url = `https://api.telegram.org/bot${CONFIG.telegram.botToken}/sendMessage`;
                
                GM_xmlhttpRequest({
                    method: 'POST',
                    url: url,
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify({
                        chat_id: CONFIG.telegram.chatId,
                        text: message
                    }),
                    onload: (response) => {
                        if (response.status === 200) {
                            console.log('[Alert] Telegram notification sent');
                            resolve();
                        } else {
                            console.error('[Alert] Telegram error:', response.statusText);
                            reject(new Error(response.statusText));
                        }
                    },
                    onerror: (error) => {
                        console.error('[Alert] Telegram request failed:', error);
                        reject(error);
                    }
                });
            });
        }
    }

    // ==================== MAIN MONITOR ====================
    class PriceMonitor {
        constructor() {
            this.stateManager = new StateManager();
            this.scraper = new ProductScraper();
            this.alertManager = new AlertManager(this.stateManager);
            this.isRunning = false;
        }

        async run() {
            if (this.isRunning) {
                console.log('[Monitor] Already running, skipping...');
                return;
            }

            this.isRunning = true;
            console.log('[Monitor] Starting price check...');

            try {
                // Check error limit
                const state = this.stateManager.getState();
                if (state.errorCount >= CONFIG.limits.stop_if_errors) {
                    console.error('[Monitor] Error limit reached, stopping');
                    return;
                }

                // Scrape products
                const products = this.scraper.scrapeProducts();

                if (products.length === 0) {
                    console.log('[Monitor] No products found');
                    this.stateManager.incrementError();
                    return;
                }

                // Reset error count on success
                this.stateManager.resetErrors();

                // Check for deals
                let alertCount = 0;
                for (const product of products) {
                    if (this.alertManager.shouldAlert(product)) {
                        await this.alertManager.sendAlert(product);
                        alertCount++;
                    }
                }

                console.log(`[Monitor] Check complete. Found ${alertCount} deals out of ${products.length} products`);

                // Display summary
                this.displaySummary(products, alertCount);

            } catch (error) {
                console.error('[Monitor] Error during check:', error);
                this.stateManager.incrementError();
            } finally {
                this.isRunning = false;
            }
        }

        displaySummary(products, alertCount) {
            // Find cheap products
            const cheapProducts = products.filter(p => 
                p.price <= CONFIG.alerting.condition.price_threshold
            );

            const highDiscounts = products.filter(p => 
                p.discount >= CONFIG.alerting.condition.price_drop_percentage
            );

            console.log('\n' + '='.repeat(60));
            console.log('SWIGGY INSTAMART PRICE MONITOR - SUMMARY');
            console.log('='.repeat(60));
            console.log(`Total Products: ${products.length}`);
            console.log(`Products under ₹${CONFIG.alerting.condition.price_threshold}: ${cheapProducts.length}`);
            console.log(`High Discounts (>70%): ${highDiscounts.length}`);
            console.log(`Alerts Sent: ${alertCount}`);
            console.log('='.repeat(60));

            if (cheapProducts.length > 0) {
                console.log('\n🔥 CHEAP PRODUCTS:');
                cheapProducts.slice(0, 10).forEach((p, i) => {
                    console.log(`${i+1}. ${p.name} - ₹${p.price} (${p.discount}% off)`);
                });
            }

            if (highDiscounts.length > 0) {
                console.log('\n💰 HIGH DISCOUNTS:');
                highDiscounts.slice(0, 10).forEach((p, i) => {
                    console.log(`${i+1}. ${p.name} - ₹${p.price} (${p.discount}% off)`);
                });
            }

            console.log('\n' + '='.repeat(60) + '\n');
        }

        scheduleNextRun() {
            const minMs = CONFIG.monitor.trigger.frequency.min_minutes * 60 * 1000;
            const maxMs = CONFIG.monitor.trigger.frequency.max_minutes * 60 * 1000;
            
            let delay = minMs;
            if (CONFIG.monitor.trigger.frequency.randomize) {
                delay = minMs + Math.random() * (maxMs - minMs);
            }

            const minutes = Math.round(delay / 60000);
            console.log(`[Monitor] Next check in ${minutes} minutes`);

            setTimeout(() => this.run(), delay);
        }
    }

    // ==================== INITIALIZATION ====================
    function init() {
        console.log('[Monitor] Swiggy Instamart Price Monitor loaded');
        console.log('[Monitor] Configuration:', CONFIG);

        // Wait for page to fully load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', startMonitor);
        } else {
            startMonitor();
        }
    }

    function startMonitor() {
        // Check if we're on the right page
        if (!window.location.href.includes('swiggy.com/instamart')) {
            console.log('[Monitor] Not on Instamart page, skipping');
            return;
        }

        // Wait a bit for dynamic content to load
        setTimeout(() => {
            const monitor = new PriceMonitor();
            
            // Run immediately
            monitor.run();

            // Schedule periodic runs
            monitor.scheduleNextRun();

            // Add manual trigger button
            addControlPanel(monitor);
        }, 3000);
    }

    function addControlPanel(monitor) {
        const panel = document.createElement('div');
        panel.id = 'swiggy-monitor-panel';
        panel.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #fff;
            border: 2px solid #fc8019;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 999999;
            font-family: Arial, sans-serif;
            min-width: 200px;
        `;

        panel.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 10px; color: #fc8019;">
                🔥 Price Monitor
            </div>
            <button id="monitor-check-now" style="
                width: 100%;
                padding: 8px;
                background: #fc8019;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-bottom: 5px;
            ">Check Now</button>
            <div id="monitor-status" style="
                font-size: 12px;
                color: #666;
                margin-top: 10px;
            ">Ready</div>
        `;

        document.body.appendChild(panel);

        // Add click handler
        document.getElementById('monitor-check-now').addEventListener('click', () => {
            document.getElementById('monitor-status').textContent = 'Checking...';
            monitor.run().then(() => {
                document.getElementById('monitor-status').textContent = 'Check complete!';
                setTimeout(() => {
                    document.getElementById('monitor-status').textContent = 'Ready';
                }, 3000);
            });
        });
    }

    // Start the script
    init();

})();
