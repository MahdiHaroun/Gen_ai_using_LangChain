import React, { useState } from 'react';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!text.trim() || !apiKey.trim()) {
      setError('Please provide both text and API key');
      return;
    }

    setLoading(true);
    setError('');
    setSummary('');

    try {
      const response = await fetch('http://localhost:8000/summarizing/summarize_text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          api_key: apiKey
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSummary(data.summary);
    } catch (err) {
      setError('Failed to generate summary. Please check your API key and try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Text Summarization Tool</h1>
        <p>Enter your text and API key to generate a summary</p>
      </header>
      
      <main className="App-main">
        <form onSubmit={handleSubmit} className="summarize-form">
          <div className="form-group">
            <label htmlFor="apiKey">Groq API Key:</label>
            <input
              type="password"
              id="apiKey"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your Groq API key"
              className="api-input"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="text">Text to Summarize:</label>
            <textarea
              id="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter the text you want to summarize..."
              rows={10}
              className="text-input"
            />
          </div>
          
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Generating Summary...' : 'Generate Summary'}
          </button>
        </form>
        
        {error && <div className="error-message">{error}</div>}
        
        {summary && (
          <div className="summary-result">
            <h2>Summary:</h2>
            <div className="summary-content">{summary}</div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
