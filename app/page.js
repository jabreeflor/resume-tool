'use client';

import { useState } from 'react';

export default function Home() {
  const [resume, setResume] = useState('');
  const [suggestions, setSuggestions] = useState(null);
  const [improved, setImproved] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('suggestions');

  async function analyze() {
    if (!resume.trim()) return;
    setLoading(true);
    setError('');
    setSuggestions(null);
    setImproved('');

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Analysis failed');
      }

      const data = await res.json();
      setSuggestions(data.suggestions);
      setImproved(data.improved);
      setActiveTab('suggestions');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">📄 Resume Tool</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Paste your resume → get AI-powered suggestions + a cleaned-up version
        </p>
      </div>

      {/* Input */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
            Your Resume
          </label>
          <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            {resume.length} chars
          </span>
        </div>
        <textarea
          value={resume}
          onChange={(e) => setResume(e.target.value)}
          placeholder="Paste your resume here... (plain text or markdown)"
          className="w-full"
          rows={12}
        />
        <div className="flex gap-3 mt-3">
          <button
            onClick={analyze}
            disabled={loading || !resume.trim()}
            className="px-6 py-2.5 rounded-lg font-medium text-white transition-all"
            style={{
              background: loading || !resume.trim() ? '#333' : 'var(--accent)',
              cursor: loading || !resume.trim() ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? '⏳ Analyzing...' : '✨ Analyze Resume'}
          </button>
          <button
            onClick={() => { setResume(''); setSuggestions(null); setImproved(''); }}
            className="px-4 py-2.5 rounded-lg font-medium transition-all"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
          >
            Clear
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg mb-6" style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid var(--error)' }}>
          <p style={{ color: 'var(--error)' }}>✗ {error}</p>
        </div>
      )}

      {/* Results */}
      {suggestions && (
        <div>
          {/* Tabs */}
          <div className="flex gap-1 mb-4 p-1 rounded-lg" style={{ background: 'var(--bg-secondary)' }}>
            <button
              onClick={() => setActiveTab('suggestions')}
              className="px-4 py-2 rounded-md text-sm font-medium transition-all"
              style={{
                background: activeTab === 'suggestions' ? 'var(--bg-card)' : 'transparent',
                color: activeTab === 'suggestions' ? 'var(--text-primary)' : 'var(--text-secondary)',
              }}
            >
              💡 Suggestions ({suggestions.length})
            </button>
            <button
              onClick={() => setActiveTab('improved')}
              className="px-4 py-2 rounded-md text-sm font-medium transition-all"
              style={{
                background: activeTab === 'improved' ? 'var(--bg-card)' : 'transparent',
                color: activeTab === 'improved' ? 'var(--text-primary)' : 'var(--text-secondary)',
              }}
            >
              📄 Improved Version
            </button>
          </div>

          {/* Suggestions Tab */}
          {activeTab === 'suggestions' && (
            <div>
              {suggestions.map((s, i) => (
                <div key={i} className="suggestion-card">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`badge badge-${s.priority}`}>{s.priority}</span>
                    <span className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                      {s.category}
                    </span>
                  </div>
                  <p className="font-medium mb-1">{s.title}</p>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{s.description}</p>
                  {s.example && (
                    <div className="mt-2 p-3 rounded text-sm" style={{ background: 'var(--bg-secondary)' }}>
                      <span style={{ color: 'var(--accent)' }}>Example: </span>
                      {s.example}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Improved Tab */}
          {activeTab === 'improved' && (
            <div>
              <div className="flex justify-end mb-2">
                <button
                  onClick={() => copyToClipboard(improved)}
                  className="px-3 py-1.5 rounded text-sm transition-all"
                  style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
                >
                  📋 Copy
                </button>
              </div>
              <div
                className="p-6 rounded-lg whitespace-pre-wrap text-sm leading-relaxed"
                style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
              >
                {improved}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
