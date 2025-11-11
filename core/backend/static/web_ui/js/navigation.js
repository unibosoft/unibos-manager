/**
 * UNIBOS Web Interface Keyboard Navigation
 * Provides CLI-like keyboard navigation in web interface
 */

(function() {
    let currentModuleIndex = 0;
    let currentToolIndex = 0;
    let currentSection = 'modules'; // 'modules', 'tools', 'dev'
    let navigationEnabled = true;

    // Get all navigable items
    function getNavigableItems() {
        const modules = Array.from(document.querySelectorAll('.sidebar-section:nth-child(1) .sidebar-item'));
        const tools = Array.from(document.querySelectorAll('.sidebar-section:nth-child(2) .sidebar-item'));
        const devTools = Array.from(document.querySelectorAll('.sidebar-section:nth-child(3) .sidebar-item'));
        
        return { modules, tools, devTools };
    }

    // Highlight current item
    function highlightItem(section, index) {
        // Remove all highlights
        document.querySelectorAll('.sidebar-item').forEach(item => {
            item.classList.remove('keyboard-selected');
        });

        // Get items for current section
        const items = getNavigableItems();
        let targetItems = [];
        
        switch(section) {
            case 'modules':
                targetItems = items.modules;
                break;
            case 'tools':
                targetItems = items.tools;
                break;
            case 'dev':
                targetItems = items.devTools;
                break;
        }

        // Highlight current item
        if (targetItems[index]) {
            targetItems[index].classList.add('keyboard-selected');
            targetItems[index].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    // Navigate to selected item
    function activateCurrentItem() {
        const selectedItem = document.querySelector('.sidebar-item.keyboard-selected');
        if (selectedItem) {
            selectedItem.click();
        }
    }

    // Handle keyboard events
    document.addEventListener('keydown', function(e) {
        // Skip if user is typing in an input field
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || !navigationEnabled) {
            return;
        }

        const items = getNavigableItems();
        let handled = false;

        switch(e.key) {
            case 'ArrowUp':
                e.preventDefault();
                handled = true;
                
                if (currentSection === 'modules') {
                    if (currentModuleIndex > 0) {
                        currentModuleIndex--;
                    }
                } else if (currentSection === 'tools') {
                    if (currentToolIndex > 0) {
                        currentToolIndex--;
                    } else {
                        // Move to modules section
                        currentSection = 'modules';
                        currentModuleIndex = items.modules.length - 1;
                    }
                } else if (currentSection === 'dev') {
                    // Move to tools section
                    currentSection = 'tools';
                    currentToolIndex = items.tools.length - 1;
                }
                break;

            case 'ArrowDown':
                e.preventDefault();
                handled = true;
                
                if (currentSection === 'modules') {
                    if (currentModuleIndex < items.modules.length - 1) {
                        currentModuleIndex++;
                    } else {
                        // Move to tools section
                        currentSection = 'tools';
                        currentToolIndex = 0;
                    }
                } else if (currentSection === 'tools') {
                    if (currentToolIndex < items.tools.length - 1) {
                        currentToolIndex++;
                    } else if (items.devTools.length > 0) {
                        // Move to dev section
                        currentSection = 'dev';
                        currentToolIndex = 0;
                    }
                } else if (currentSection === 'dev') {
                    if (currentToolIndex < items.devTools.length - 1) {
                        currentToolIndex++;
                    }
                }
                break;

            case 'ArrowRight':
            case 'Enter':
                e.preventDefault();
                activateCurrentItem();
                handled = true;
                break;

            case 'ArrowLeft':
            case 'Escape':
                e.preventDefault();
                // Go back to main dashboard
                if (window.location.pathname !== '/') {
                    window.location.href = '/';
                }
                handled = true;
                break;

            // Number keys for quick module access
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
            case '6':
            case '7':
            case '8':
            case '9':
                e.preventDefault();
                const moduleIndex = parseInt(e.key) - 1;
                if (items.modules[moduleIndex]) {
                    currentSection = 'modules';
                    currentModuleIndex = moduleIndex;
                    highlightItem(currentSection, currentModuleIndex);
                    setTimeout(() => activateCurrentItem(), 100);
                }
                handled = true;
                break;

            // Quick navigation keys
            case 'm':
                e.preventDefault();
                currentSection = 'modules';
                currentModuleIndex = 0;
                handled = true;
                break;

            case 't':
                e.preventDefault();
                currentSection = 'tools';
                currentToolIndex = 0;
                handled = true;
                break;

            case 'd':
                e.preventDefault();
                if (items.devTools.length > 0) {
                    currentSection = 'dev';
                    currentToolIndex = 0;
                    handled = true;
                }
                break;

            case 'h':
                e.preventDefault();
                // Show help
                showNavigationHelp();
                handled = true;
                break;

            case 'q':
                e.preventDefault();
                // Quick logout
                if (confirm('logout from unibos?')) {
                    window.location.href = '/logout/';
                }
                handled = true;
                break;
        }

        if (handled) {
            const index = currentSection === 'modules' ? currentModuleIndex : currentToolIndex;
            highlightItem(currentSection, index);
        }
    });

    // Show navigation help
    function showNavigationHelp() {
        const helpText = `
keyboard navigation help:
━━━━━━━━━━━━━━━━━━━━━━━
↑/↓     : navigate items
→/enter : select item
←/esc   : go back
1-9     : quick module access
m       : jump to modules
t       : jump to tools
d       : jump to dev tools
h       : show this help
q       : logout
━━━━━━━━━━━━━━━━━━━━━━━`;
        
        // Create help modal
        const modal = document.createElement('div');
        modal.className = 'navigation-help-modal';
        modal.innerHTML = `
            <div class="navigation-help-content">
                <pre>${helpText}</pre>
                <button onclick="this.parentElement.parentElement.remove()">close (esc)</button>
            </div>
        `;
        document.body.appendChild(modal);

        // Close on escape
        const closeHandler = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', closeHandler);
            }
        };
        document.addEventListener('keydown', closeHandler);
    }

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        // Add CSS for keyboard navigation
        const style = document.createElement('style');
        style.textContent = `
            .sidebar-item.keyboard-selected {
                background-color: rgba(0, 255, 255, 0.1) !important;
                border-left: 3px solid #00ffff !important;
            }
            
            .navigation-help-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
            }
            
            .navigation-help-content {
                background: #1a1a1a;
                padding: 30px;
                border-radius: 8px;
                border: 2px solid #00ffff;
                max-width: 500px;
            }
            
            .navigation-help-content pre {
                color: #00ff00;
                font-family: 'Courier New', monospace;
                margin: 0 0 20px 0;
            }
            
            .navigation-help-content button {
                background: #333;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 10px 20px;
                cursor: pointer;
                border-radius: 4px;
                width: 100%;
                text-transform: lowercase;
            }
            
            .navigation-help-content button:hover {
                background: #444;
            }
        `;
        document.head.appendChild(style);

        // Show initial selection
        highlightItem('modules', 0);

        // Show help hint
        console.log('%c📌 Press "h" for keyboard navigation help', 'color: #00ff00; font-size: 14px;');
    });

})();