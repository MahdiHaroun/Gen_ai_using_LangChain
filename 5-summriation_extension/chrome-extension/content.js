// Content script for Chrome Extension
(function() {
    'use strict';

    // Add a context menu item for summarizing selected text
    let selectedText = '';
    
    document.addEventListener('mouseup', function() {
        const selection = window.getSelection();
        selectedText = selection.toString().trim();
        
        if (selectedText) {
            // Store the selected text so the popup can access it
            chrome.runtime.sendMessage({
                action: 'storeSelectedText',
                text: selectedText
            });
        }
    });

    // Listen for messages from the popup
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.action === 'getSelectedText') {
            const selection = window.getSelection().toString().trim();
            sendResponse({text: selection});
        }
    });

    // Add visual indicator when text is selected
    function addSelectionIndicator() {
        const existingIndicator = document.getElementById('summarizer-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }

        const selection = window.getSelection();
        if (selection.toString().trim().length > 0) {
            const range = selection.getRangeAt(0);
            const rect = range.getBoundingClientRect();
            
            const indicator = document.createElement('div');
            indicator.id = 'summarizer-indicator';
            indicator.innerHTML = '📝 Click extension to summarize';
            indicator.style.cssText = `
                position: fixed;
                top: ${rect.top - 30}px;
                left: ${rect.left}px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 10000;
                pointer-events: none;
                animation: fadeIn 0.3s ease-in;
            `;
            
            document.body.appendChild(indicator);
            
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.remove();
                }
            }, 2000);
        }
    }

    // Add CSS for the fade-in animation
    if (!document.getElementById('summarizer-styles')) {
        const style = document.createElement('style');
        style.id = 'summarizer-styles';
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        `;
        document.head.appendChild(style);
    }

    document.addEventListener('mouseup', addSelectionIndicator);
})();
