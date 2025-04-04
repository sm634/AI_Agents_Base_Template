import { useState } from 'react';
import { askQuery } from './api';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<{ destination: string; response: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    setLoading(true);
    try {
      const res = await askQuery(query);
      setResult(res);
    } catch (err) {
      console.error('Error querying agent:', err);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center px-4">
      <h1 className="text-3xl font-bold mb-6">🧠 Agentic Data Router</h1>
      <textarea
        className="w-full max-w-xl p-4 border border-gray-300 rounded mb-4"
        rows={4}
        placeholder="Ask a question..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button
        onClick={handleAsk}
        disabled={loading || !query}
        className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
      >
        {loading ? 'Thinking...' : 'Ask'}
      </button>

      {result && (
        <div className="mt-6 w-full max-w-xl bg-white p-4 rounded shadow">
          <p className="text-sm text-gray-600">📦 Source: <strong>{result.destination}</strong></p>
          <p className="mt-2 text-lg">{result.response}</p>
        </div>
      )}
    </div>
  );
}

export default App;
