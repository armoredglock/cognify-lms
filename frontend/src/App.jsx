import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import CourseCatalog from './pages/CourseCatalog';
import StudentDashboard from './pages/StudentDashboard';

function App() {
    return (
        <AuthProvider>
            <Router>
                <div style={{ fontFamily: 'system-ui, -apple-system, sans-serif', backgroundColor: '#f8fafc', minHeight: '100vh', color: '#0f172a' }}>
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        <Route 
                            path="/courses" 
                            element={
                                <ProtectedRoute>
                                    <CourseCatalog />
                                </ProtectedRoute>
                            } 
                        />
                        <Route 
                            path="/lesson/:lessonId" 
                            element={
                                <ProtectedRoute>
                                    <StudentDashboard />
                                </ProtectedRoute>
                            } 
                        />
                        {/* Redirect root to courses dashboard (protected route will handle unauth) */}
                        <Route path="/" element={<Navigate to="/courses" replace />} />
                        <Route path="*" element={<Navigate to="/courses" replace />} />
                    </Routes>
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App;
