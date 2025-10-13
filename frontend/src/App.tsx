import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Landing from './pages/Landing';
import Login from './pages/Login';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import CreateJob from './pages/CreateJob';
import Interview from './pages/Interview';
import EnhancedInterview from './pages/EnhancedInterview';
import InterviewAnalytics from './pages/InterviewAnalytics';
import DebugDashboard from './pages/DebugDashboard';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route 
            path="/user/dashboard" 
            element={
              <ProtectedRoute requiredRole="user">
                <UserDashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/debug" 
            element={<DebugDashboard />} 
          />
          <Route 
            path="/admin/dashboard" 
            element={
              <ProtectedRoute requiredRole="admin">
                <AdminDashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin" 
            element={<Navigate to="/admin/dashboard" replace />} 
          />
          <Route 
            path="/create-job" 
            element={
              <ProtectedRoute requiredRole="admin">
                <CreateJob />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/user" 
            element={<Navigate to="/user/dashboard" replace />} 
          />
          <Route 
            path="/interview/:interviewId" 
            element={
              <ProtectedRoute requiredRole="user">
                <Interview />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/enhanced-interview/:interviewId" 
            element={
              <ProtectedRoute requiredRole="user">
                <EnhancedInterview />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/interview-analytics" 
            element={
              <ProtectedRoute requiredRole="admin">
                <InterviewAnalytics />
              </ProtectedRoute>
            } 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toaster position="top-right" />
      </div>
    </Router>
  );
}

export default App;


