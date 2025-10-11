import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Jobs from './pages/Jobs';
import Candidates from './pages/Candidates';
import Interviews from './pages/Interviews';
import CreateJob from './pages/CreateJob';
import CandidateDetail from './pages/CandidateDetail';
import InterviewConduct from './pages/InterviewConduct';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-secondary-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/jobs/create" element={<CreateJob />} />
            <Route path="/candidates" element={<Candidates />} />
            <Route path="/candidates/:id" element={<CandidateDetail />} />
            <Route path="/interviews" element={<Interviews />} />
            <Route path="/interviews/:id/conduct" element={<InterviewConduct />} />
          </Routes>
        </main>
        <Toaster position="top-right" />
      </div>
    </Router>
  );
}

export default App;


