// Background script for Chrome Extension
let storedSelectedText = '';

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'storeSelectedText') {
        storedSelectedText = request.text;
    } else if (request.action === 'getStoredSelectedText') {
        sendResponse({text: storedSelectedText});
    }
});

// Context menu for right-click summarization
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "summarizeSelection",
        title: "Summarize selected text",
        contexts: ["selection"]
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "summarizeSelection") {
        // Store the selected text
        storedSelectedText = info.selectionText;
        
        // Show a simple notification
        chrome.notifications.create({
            type: 'basic',
            iconUrl: '/icon.png', // We'll use a simple fallback
            title: 'Text Selected for Summarization',
            message: 'Click the extension icon to summarize the selected text.'
        }).catch(() => {
            // If notifications fail, just store the text
            console.log('Selected text stored for summarization');
        });
    }
});

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
    // This will open the popup automatically when the icon is clicked
});
