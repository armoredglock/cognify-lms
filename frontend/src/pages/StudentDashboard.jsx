import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';

const StudentDashboard = () => {
    const { lessonId } = useParams();
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [showQuiz, setShowQuiz] = useState(false);
    const [quizTimeLeft, setQuizTimeLeft] = useState(60); // 60 seconds TTL mock
    const [showAIDrawer, setShowAIDrawer] = useState(false);
    const [leaderboard, setLeaderboard] = useState([]);
    const [aiData, setAiData] = useState(null);

    const videoIntervalRef = useRef(null);
    const quizIntervalRef = useRef(null);

    // Simulated Video Heartbeat to /api/tracking/heartbeat/
    useEffect(() => {
        if (isPlaying) {
            videoIntervalRef.current = setInterval(() => {
                setCurrentTime(prev => {
                    const newTime = prev + 5;
                    // Dispatch heartbeat
                    fetch('/api/tracking/heartbeat/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ lesson_id: lessonId || '123', second: newTime })
                    }).catch(() => console.log('Heartbeat sent (mock catch)', newTime));
                    return newTime;
                });
            }, 5000);
        } else {
            clearInterval(videoIntervalRef.current);
        }
        return () => clearInterval(videoIntervalRef.current);
    }, [isPlaying, lessonId]);

    // Fetch Leaderboard (mocking standard response if endpoint fails)
    useEffect(() => {
        fetch(`/api/gamification/leaderboard/${lessonId}/`)
            .then(res => res.json())
            .then(data => setLeaderboard(data))
            .catch(() => {
                setLeaderboard([
                    { rank: 1, user: 'swatisaumya', score: 1450 },
                    { rank: 2, user: 'armoredglock', score: 1380 },
                    { rank: 3, user: 'saanvi-singhal', score: 1290 }
                ]);
            });
    }, [lessonId]);

    // Quiz Timer TTL Sync
    useEffect(() => {
        if (showQuiz && quizTimeLeft > 0) {
            quizIntervalRef.current = setInterval(() => {
                setQuizTimeLeft(prev => prev - 1);
            }, 1000);
        } else if (showQuiz && quizTimeLeft <= 0) {
            clearInterval(quizIntervalRef.current);
            alert("Time's up! Submitting quiz automatically...");
            setShowQuiz(false);
        }
        return () => clearInterval(quizIntervalRef.current);
    }, [showQuiz, quizTimeLeft]);

    // Fetch AI Drawer Data
    const handleToggleAI = () => {
        if (!aiData) {
            fetch(`/api/ai_generator/lessons/${lessonId}/generate/`, { method: 'POST' })
                .then(res => res.json())
                .then(data => setAiData(data.generated_materials))
                .catch(() => {
                    setAiData({
                        summary: "Database Systems rely on ACID properties: Atomicity, Consistency, Isolation, and Durability.",
                        flashcards: [{ front: "What does A stand for in ACID?", back: "Atomicity" }]
                    });
                });
        }
        setShowAIDrawer(!showAIDrawer);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: '#f1f5f9', fontFamily: 'system-ui, sans-serif', color: '#1e293b' }}>
            <header style={{ backgroundColor: '#0f172a', color: '#fff', padding: '1rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1 style={{ margin: 0, fontSize: '1.2rem' }}>🎓 Lesson Dashboard: {lessonId}</h1>
                <Link to="/courses" style={{ color: '#cbd5e1', textDecoration: 'none' }}>&larr; Back to Catalog</Link>
            </header>

            <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
                {/* Main Content Area */}
                <main style={{ flex: 1, padding: '2rem', overflowY: 'auto' }}>
                    
                    {/* Video Player Mock */}
                    <div style={{ backgroundColor: '#000', height: '400px', borderRadius: '0.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', position: 'relative' }}>
                        <div style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '1rem' }}>Video Playback (Simulated)</div>
                        <div style={{ color: '#38bdf8', fontSize: '2rem', marginBottom: '1rem' }}>{Math.floor(currentTime / 60)}:{(currentTime % 60).toString().padStart(2, '0')}</div>
                        <button 
                            onClick={() => setIsPlaying(!isPlaying)}
                            style={{ padding: '0.75rem 2rem', fontSize: '1rem', backgroundColor: isPlaying ? '#ef4444' : '#10b981', color: '#fff', border: 'none', borderRadius: '2rem', cursor: 'pointer', fontWeight: 'bold' }}
                        >
                            {isPlaying ? 'Pause' : 'Play'}
                        </button>
                    </div>

                    <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                        <button 
                            onClick={() => { setShowQuiz(true); setQuizTimeLeft(60); }}
                            style={{ padding: '1rem 2rem', backgroundColor: '#3b82f6', color: '#fff', border: 'none', borderRadius: '0.5rem', cursor: 'pointer', fontWeight: 'bold', fontSize: '1rem' }}
                        >
                            📝 Take Lesson Quiz
                        </button>
                        <button 
                            onClick={handleToggleAI}
                            style={{ padding: '1rem 2rem', backgroundColor: '#8b5cf6', color: '#fff', border: 'none', borderRadius: '0.5rem', cursor: 'pointer', fontWeight: 'bold', fontSize: '1rem' }}
                        >
                            🤖 View AI Study Materials
                        </button>
                    </div>
                </main>

                {/* Right Sidebar (Leaderboard & AI) */}
                <aside style={{ width: '350px', backgroundColor: '#fff', borderLeft: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column' }}>
                    
                    {/* AI Drawer (renders in sidebar if active) */}
                    {showAIDrawer && (
                        <div style={{ padding: '1.5rem', borderBottom: '1px solid #e2e8f0', backgroundColor: '#faf5ff' }}>
                            <h3 style={{ margin: '0 0 1rem 0', color: '#6b21a8' }}>🤖 AI Study Tools</h3>
                            {aiData ? (
                                <div>
                                    <p style={{ fontSize: '0.9rem', lineHeight: '1.5' }}><strong>Summary:</strong> {aiData.summary}</p>
                                    <h4 style={{ margin: '1rem 0 0.5rem 0' }}>Flashcard</h4>
                                    <div style={{ padding: '1rem', backgroundColor: '#fff', border: '1px solid #e9d5ff', borderRadius: '0.5rem' }}>
                                        <p style={{ margin: '0 0 0.5rem 0', fontWeight: 'bold' }}>Q: {aiData.flashcards[0]?.front}</p>
                                        <p style={{ margin: 0, color: '#64748b' }}>A: {aiData.flashcards[0]?.back}</p>
                                    </div>
                                </div>
                            ) : (
                                <p>Loading AI materials...</p>
                            )}
                        </div>
                    )}

                    {/* Leaderboard */}
                    <div style={{ padding: '1.5rem', flex: 1, overflowY: 'auto' }}>
                        <h3 style={{ margin: '0 0 1rem 0' }}>🏆 Leaderboard</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            {leaderboard.map((user, idx) => (
                                <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', backgroundColor: idx === 0 ? '#fef3c7' : '#f8fafc', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                                    <div>
                                        <span style={{ fontWeight: 'bold', marginRight: '0.5rem' }}>#{user.rank}</span>
                                        <span>{user.user}</span>
                                    </div>
                                    <span style={{ fontWeight: 'bold', color: '#3b82f6' }}>{user.score}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </aside>
            </div>

            {/* Quiz Modal */}
            {showQuiz && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 50 }}>
                    <div style={{ backgroundColor: '#fff', padding: '2rem', borderRadius: '0.5rem', width: '500px', maxWidth: '90%' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h2 style={{ margin: 0 }}>Timed Quiz</h2>
                            <div style={{ backgroundColor: quizTimeLeft < 10 ? '#fef2f2' : '#f1f5f9', color: quizTimeLeft < 10 ? '#ef4444' : '#0f172a', padding: '0.5rem 1rem', borderRadius: '2rem', fontWeight: 'bold' }}>
                                ⏱️ {Math.floor(quizTimeLeft / 60)}:{(quizTimeLeft % 60).toString().padStart(2, '0')}
                            </div>
                        </div>
                        
                        <div style={{ marginBottom: '1.5rem' }}>
                            <p style={{ fontWeight: 'bold', marginBottom: '1rem' }}>1. Which ACID property guarantees that all operations within a work unit are completed successfully?</p>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                <label style={{ padding: '0.75rem', border: '1px solid #e2e8f0', borderRadius: '0.5rem', display: 'flex', gap: '0.5rem' }}>
                                    <input type="radio" name="q1" /> Consistency
                                </label>
                                <label style={{ padding: '0.75rem', border: '1px solid #e2e8f0', borderRadius: '0.5rem', display: 'flex', gap: '0.5rem' }}>
                                    <input type="radio" name="q1" /> Atomicity
                                </label>
                            </div>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                            <button onClick={() => setShowQuiz(false)} style={{ padding: '0.5rem 1rem', border: '1px solid #cbd5e1', backgroundColor: 'transparent', borderRadius: '0.25rem', cursor: 'pointer' }}>Cancel</button>
                            <button onClick={() => { alert('Quiz submitted successfully!'); setShowQuiz(false); }} style={{ padding: '0.5rem 1rem', backgroundColor: '#3b82f6', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 'bold' }}>Submit Answers</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default StudentDashboard;
