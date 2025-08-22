// Popup JavaScript for Chrome Extension
document.addEventListener('DOMContentLoaded', function() {
    const apiKeyInput = document.getElementById('apiKey');
    const textInput = document.getElementById('textInput');
    const getSelectedTextBtn = document.getElementById('getSelectedText');
    const summarizeBtn = document.getElementById('summarizeBtn');
    const messageDiv = document.getElementById('message');
    const loadingDiv = document.getElementById('loading');
    const summaryDiv = document.getElementById('summary');
    const summaryContent = document.getElementById('summaryContent');

    // Load saved API key
    chrome.storage.sync.get(['groqApiKey'], function(result) {
        if (result.groqApiKey) {
            apiKeyInput.value = result.groqApiKey;
        }
    });

    // Save API key when changed
    apiKeyInput.addEventListener('change', function() {
        chrome.storage.sync.set({
            groqApiKey: apiKeyInput.value
        });
    });

    // Get selected text from the current tab
    getSelectedTextBtn.addEventListener('click', async function() {
        try {
            const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
            
            const results = await chrome.scripting.executeScript({
                target: {tabId: tab.id},
                function: getSelectedText,
            });
            
            const selectedText = results[0].result;
            if (selectedText) {
                textInput.value = selectedText;
                showMessage('Selected text retrieved successfully!', 'success');
            } else {
                showMessage('No text selected on the page. Please select some text first.', 'error');
            }
        } catch (error) {
            console.error('Error getting selected text:', error);
            showMessage('Error getting selected text. Please try again.', 'error');
        }
    });

    // Summarize text
    summarizeBtn.addEventListener('click', async function() {
        const apiKey = apiKeyInput.value.trim();
        const text = textInput.value.trim();

        if (!apiKey) {
            showMessage('Please enter your Groq API key.', 'error');
            return;
        }

        if (!text) {
            showMessage('Please enter or select text to summarize.', 'error');
            return;
        }

        showLoading(true);
        clearMessages();
        summaryDiv.style.display = 'none';

        try {
            const summary = await summarizeText(text, apiKey);
            showSummary(summary);
            showMessage('Summary generated successfully!', 'success');
        } catch (error) {
            console.error('Error:', error);
            showMessage('Failed to generate summary. Please check your API key and try again.', 'error');
        } finally {
            showLoading(false);
        }
    });

    function showMessage(message, type) {
        messageDiv.innerHTML = `<div class="${type}-message">${message}</div>`;
    }

    function clearMessages() {
        messageDiv.innerHTML = '';
    }

    function showLoading(show) {
        loadingDiv.style.display = show ? 'block' : 'none';
        summarizeBtn.disabled = show;
    }

    function showSummary(summary) {
        summaryContent.textContent = summary;
        summaryDiv.style.display = 'block';
    }
});

// Function to be injected into the page to get selected text
function getSelectedText() {
    return window.getSelection().toString();
}

// Function to call Groq API for summarization
async function summarizeText(text, apiKey) {
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            model: 'mixtral-8x7b-32768',
            messages: [
                {
                    role: 'system',
                    content: `You are a professional text summarizer. Your job is to create clear, concise summaries of provided text.

Instructions:
1. Start with a brief "Motivation" section explaining why this text is important
2. Provide a precise summary with an introduction
3. Present the main points as numbered points
4. Keep the summary informative but concise
5. Maintain the key insights and important details`
                },
                {
                    role: 'user',
                    content: `Please summarize the following text:\n\n${text}`
                }
            ],
            temperature: 0.3,
            max_tokens: 1000
        }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`API request failed: ${response.status} ${response.statusText}. ${errorData.error?.message || ''}`);
    }

    const data = await response.json();
    
    if (!data.choices || !data.choices[0] || !data.choices[0].message) {
        throw new Error('Invalid response format from API');
    }
    
    return data.choices[0].message.content;
}
