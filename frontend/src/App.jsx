import React, { useState } from 'react'

function App() {
  const [activeTab, setActiveTab] = useState('courses')

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, sans-serif', margin: 0, padding: 0, backgroundColor: '#f8fafc', minHeight: '100vh', color: '#0f172a' }}>
      <header style={{ backgroundColor: '#1e293b', color: '#ffffff', padding: '1rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>🎓</span> Cognify LMS
          </h1>
          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: '#94a3b8' }}>DBMS Course Project — PostgreSQL + Redis + React + AI Engine</p>
        </div>
        <nav style={{ display: 'flex', gap: '1rem' }}>
          {['courses', 'tracking', 'quiz', 'leaderboard', 'ai-summary'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                background: activeTab === tab ? '#3b82f6' : 'transparent',
                color: '#ffffff',
                border: 'none',
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                fontWeight: 600,
                textTransform: 'capitalize',
                transition: 'background 0.2s',
              }}
            >
              {tab.replace('-', ' ')}
            </button>
          ))}
        </nav>
      </header>

      <main style={{ maxWidth: '1200px', margin: '2rem auto', padding: '0 1rem' }}>
        <div style={{ backgroundColor: '#ffffff', borderRadius: '0.5rem', padding: '2rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          {activeTab === 'courses' && (
            <div>
              <h2 style={{ marginTop: 0 }}>📚 Course Catalog [P1 - Saanvi Singhal]</h2>
              <p style={{ color: '#64748b' }}>Relational course, module, and lesson structure backed by PostgreSQL 3NF schema.</p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginTop: '1.5rem' }}>
                <div style={{ border: '1px solid #e2e8f0', borderRadius: '0.5rem', padding: '1rem' }}>
                  <h3 style={{ margin: '0 0 0.5rem 0' }}>Database Systems (DBMS)</h3>
                  <p style={{ fontSize: '0.9rem', color: '#64748b' }}>Learn Relational Algebra, Normalization (1NF-BCNF), Indexing, and ACID Transactions.</p>
                  <span style={{ display: 'inline-block', backgroundColor: '#e0f2fe', color: '#0369a1', fontSize: '0.75rem', padding: '0.2rem 0.6rem', borderRadius: '1rem', fontWeight: 600 }}>Core CS</span>
                </div>
                <div style={{ border: '1px solid #e2e8f0', borderRadius: '0.5rem', padding: '1rem' }}>
                  <h3 style={{ margin: '0 0 0.5rem 0' }}>In-Memory Systems & Caching</h3>
                  <p style={{ fontSize: '0.9rem', color: '#64748b' }}>Master Redis data structures: Hashes, TTLs, and Sorted Sets for high-throughput scaling.</p>
                  <span style={{ display: 'inline-block', backgroundColor: '#fef3c7', color: '#b45309', fontSize: '0.75rem', padding: '0.2rem 0.6rem', borderRadius: '1rem', fontWeight: 600 }}>Advanced Systems</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'tracking' && (
            <div>
              <h2 style={{ marginTop: 0 }}>⏱️ Video Playback & Redis Cache [P2 - Bibek Tripathy]</h2>
              <p style={{ color: '#64748b' }}>High-frequency playback heartbeats are absorbed in Redis and lazily persisted to PostgreSQL.</p>
              <div style={{ backgroundColor: '#0f172a', color: '#38bdf8', padding: '1rem', borderRadius: '0.375rem', fontFamily: 'monospace' }}>
                POST /api/tracking/heartbeat/<br/>
                &#123; "lesson_id": "...", "second": 142 &#125; -&gt; Redis Key: video:user:1:lesson:4
              </div>
            </div>
          )}

          {activeTab === 'quiz' && (
            <div>
              <h2 style={{ marginTop: 0 }}>📝 Timed Assessment Engine [P3 - Swati Saumya]</h2>
              <p style={{ color: '#64748b' }}>Redis TTL key enforces strict exam timeouts; submissions are verified using atomic DB transactions.</p>
              <div style={{ border: '1px solid #cbd5e1', borderRadius: '0.375rem', padding: '1rem', backgroundColor: '#f1f5f9' }}>
                <p><strong>Question 1:</strong> Which ACID property guarantees that all transactions either completely succeed or completely fail?</p>
                <label style={{ display: 'block', margin: '0.5rem 0' }}><input type="radio" name="q1" /> Consistency</label>
                <label style={{ display: 'block', margin: '0.5rem 0' }}><input type="radio" name="q1" defaultChecked /> Atomicity (Correct)</label>
                <label style={{ display: 'block', margin: '0.5rem 0' }}><input type="radio" name="q1" /> Durability</label>
              </div>
            </div>
          )}

          {activeTab === 'leaderboard' && (
            <div>
              <h2 style={{ marginTop: 0 }}>🏆 Real-time Leaderboard [P4 - Meheli Ghosh]</h2>
              <p style={{ color: '#64748b' }}>Powered by Redis Sorted Sets (ZSET) for instant rank and score retrieval.</p>
              <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #cbd5e1', textAlign: 'left' }}>
                    <th style={{ padding: '0.5rem' }}>Rank</th>
                    <th style={{ padding: '0.5rem' }}>Student</th>
                    <th style={{ padding: '0.5rem' }}>Score Points</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #e2e8f0' }}><td style={{ padding: '0.5rem' }}>🥇 #1</td><td style={{ padding: '0.5rem' }}>swatisaumya</td><td style={{ padding: '0.5rem' }}>1450 pts</td></tr>
                  <tr style={{ borderBottom: '1px solid #e2e8f0' }}><td style={{ padding: '0.5rem' }}>🥈 #2</td><td style={{ padding: '0.5rem' }}>armoredglock</td><td style={{ padding: '0.5rem' }}>1380 pts</td></tr>
                  <tr style={{ borderBottom: '1px solid #e2e8f0' }}><td style={{ padding: '0.5rem' }}>🥉 #3</td><td style={{ padding: '0.5rem' }}>saanvi-singhal</td><td style={{ padding: '0.5rem' }}>1290 pts</td></tr>
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'ai-summary' && (
            <div>
              <h2 style={{ marginTop: 0 }}>🤖 AI Study Summaries & Quizzes [P5 - Sagnik Datta]</h2>
              <p style={{ color: '#64748b' }}>Generates MCQs and key concept flashcards from lecture transcripts.</p>
              <div style={{ backgroundColor: '#faf5ff', border: '1px solid #e9d5ff', borderRadius: '0.5rem', padding: '1rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#6b21a8' }}>AI Flashcard Generated</h4>
                <p style={{ margin: 0, fontWeight: 500 }}>Q: What normal form removes partial dependency?</p>
                <p style={{ margin: '0.5rem 0 0 0', color: '#7e22ce' }}>A: Second Normal Form (2NF).</p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
