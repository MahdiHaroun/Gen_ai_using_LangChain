# AI Text Summarizer Chrome Extension

This Chrome extension allows you to summarize any text on web pages using AI (Groq API).

## Features

- **Popup Interface**: Click the extension icon to open a popup where you can paste text or get selected text from the current page
- **Selected Text Integration**: Highlight text on any webpage and use the "Get Selected Text" button to automatically populate the text area
- **Context Menu**: Right-click on selected text to get a context menu option (with notification to use the extension)
- **API Key Storage**: Your Groq API key is securely stored in Chrome's sync storage
- **Responsive Design**: Clean, modern interface that works well in the extension popup

## Installation

### Method 1: Developer Mode (Recommended for testing)

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" in the top right corner
3. Click "Load unpacked"
4. Select the `chrome-extension` folder from this project
5. The extension should now appear in your extensions list

### Method 2: Pack and Install

1. Go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Pack extension"
4. Select the `chrome-extension` folder
5. Install the generated `.crx` file

## Setup

1. Get a Groq API key from [Groq Console](https://console.groq.com/)
2. Click the extension icon in Chrome
3. Enter your API key in the "Groq API Key" field
4. The API key will be automatically saved for future use

## Usage

### Method 1: Using the Popup
1. Click the extension icon
2. Either paste text directly or use "Get Selected Text" after selecting text on the page
3. Click "Summarize" to generate a summary

### Method 2: Using Selected Text
1. Highlight any text on a webpage
2. Click the extension icon
3. Click "Get Selected Text" to populate the text area
4. Click "Summarize"

### Method 3: Context Menu (Future Enhancement)
1. Highlight text on any webpage
2. Right-click and select "Summarize selected text"
3. A notification will prompt you to click the extension icon

## How It Works

The extension uses the Groq API with the Mixtral-8x7b model to generate high-quality summaries. The summarization prompt is designed to:

1. Provide motivation for why the text is important
2. Create a precise summary with introduction
3. Present main points as numbered items
4. Maintain key insights and important details

## Files Structure

```
chrome-extension/
├── manifest.json          # Extension configuration
├── popup.html            # Popup interface HTML
├── popup.js              # Popup functionality
├── content.js            # Content script for page interaction
├── background.js         # Background service worker
├── icons/                # Extension icons (add your own)
└── README.md            # This file
```

## Permissions Explained

- `activeTab`: Access to the currently active tab to get selected text
- `scripting`: Ability to inject scripts to retrieve selected text
- `storage`: Store API key securely
- `contextMenus`: Add right-click context menu options
- `notifications`: Show notifications to user
- `https://api.groq.com/*`: Make API calls to Groq

## Customization

### Adding Icons
Create PNG files in the `icons/` folder:
- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels)
- `icon128.png` (128x128 pixels)

Then add this to `manifest.json`:
```json
"icons": {
  "16": "icons/icon16.png",
  "48": "icons/icon48.png",
  "128": "icons/icon128.png"
}
```

### Changing the AI Model
In `popup.js`, modify the `model` field in the API request:
```javascript
model: 'mixtral-8x7b-32768', // Change this to other Groq models
```

### Customizing the Summarization Prompt
Modify the system message in `popup.js` to change how summaries are generated.

## Troubleshooting

1. **Extension not working**: Make sure Developer Mode is enabled and the extension is loaded correctly
2. **API errors**: Check your Groq API key is correct and has sufficient credits
3. **Selected text not working**: Make sure you've granted the extension permissions to access the current tab
4. **CORS errors**: The extension handles CORS automatically by making direct API calls

## Security

- API keys are stored securely using Chrome's sync storage
- The extension only requests necessary permissions
- No data is stored on external servers except for API calls to Groq

## Development

To modify the extension:
1. Make changes to the files
2. Go to `chrome://extensions/`
3. Click the refresh icon on your extension card
4. Test the changes

## License

This project is open source and available under the MIT License.
