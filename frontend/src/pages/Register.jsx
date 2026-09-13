import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

const Register = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        
        try {
            // Depending on the backend setup, registration might be a different endpoint.
            // Using a mock implementation for now until endpoint is fully confirmed.
            const response = await fetch('/api/users/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password }),
            });

            if (!response.ok) {
                throw new Error('Registration failed. Username may already exist.');
            }

            // Immediately login after registration
            const tokenResponse = await fetch('/api/token/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            
            if (tokenResponse.ok) {
                const data = await tokenResponse.json();
                login(data.access || 'mock-token', { username });
                navigate('/courses');
            } else {
                navigate('/login');
            }
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '4rem auto', padding: '2rem', backgroundColor: '#fff', borderRadius: '0.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h2 style={{ textAlign: 'center', marginTop: 0 }}>Create an Account</h2>
            {error && <p style={{ color: '#ef4444', backgroundColor: '#fef2f2', padding: '0.5rem', borderRadius: '0.375rem' }}>{error}</p>}
            
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Username</label>
                    <input 
                        type="text" 
                        value={username} 
                        onChange={(e) => setUsername(e.target.value)} 
                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #cbd5e1' }}
                        required 
                    />
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Email Address</label>
                    <input 
                        type="email" 
                        value={email} 
                        onChange={(e) => setEmail(e.target.value)} 
                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #cbd5e1' }}
                        required 
                    />
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Password</label>
                    <input 
                        type="password" 
                        value={password} 
                        onChange={(e) => setPassword(e.target.value)} 
                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #cbd5e1' }}
                        required 
                    />
                </div>
                <button 
                    type="submit" 
                    style={{ backgroundColor: '#10b981', color: '#fff', padding: '0.75rem', border: 'none', borderRadius: '0.375rem', fontWeight: 600, cursor: 'pointer', marginTop: '1rem' }}
                >
                    Sign Up
                </button>
            </form>
            <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.9rem', color: '#64748b' }}>
                Already have an account? <Link to="/login" style={{ color: '#10b981' }}>Log in</Link>
            </p>
        </div>
    );
};

export default Register;
