import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

interface JobMatch {
  job: {
    id: number;
    title: string;
    description: string;
    company: string;
    location: string;
    salary_min: number;
    salary_max: number;
  };
  match_percentage: number;
  matched_skills: string[];
  missing_skills: string[];
  reasoning: string;
}

interface UserResume {
  id: number;
  resume_url: string;
  skills: string[];
  experience_years: number;
  education: string;
  created_at: string;
}

const UserDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [jobMatches, setJobMatches] = useState<JobMatch[]>([]);
  const [resumes, setResumes] = useState<UserResume[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [applying, setApplying] = useState<number | null>(null);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      };

      // Fetch resumes
      const resumesResponse = await fetch('http://localhost:8000/api/user/resumes', { headers });
      if (resumesResponse.ok) {
        const resumesData = await resumesResponse.json();
        setResumes(resumesData);
      }

      // Fetch job matches
      const matchesResponse = await fetch('http://localhost:8000/api/user/job-matches', { headers });
      if (matchesResponse.ok) {
        const matchesData = await matchesResponse.json();
        setJobMatches(matchesData);
      }
    } catch (error) {
      toast.error('Failed to fetch user data');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/user/upload-resume', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        toast.success('Resume uploaded successfully!');
        fetchUserData(); // Refresh data
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Upload failed');
      }
    } catch (error) {
      toast.error('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleApplyForJob = async (jobId: number) => {
    setApplying(jobId);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/jobs/${jobId}/apply`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          candidate_id: user?.id || 1
        })
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(data.message);
        
        // Show admin notification
        toast.success(data.admin_notification, {
          duration: 5000,
          style: {
            background: '#10B981',
            color: 'white',
            fontSize: '14px',
            padding: '16px',
          }
        });
        
        // Navigate to enhanced interview after a short delay
        setTimeout(() => {
          navigate(`/enhanced-interview/${data.interview.id}`);
        }, 2000);
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Application failed');
      }
    } catch (error) {
      toast.error('Application failed. Please try again.');
    } finally {
      setApplying(null);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Welcome back, {user?.full_name}</h1>
              <p className="text-gray-600">Discover your next career opportunity</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">Job Seeker Dashboard</span>
              <button
                onClick={logout}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Resume Upload Section */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8 border border-gray-100">
          <div className="text-center">
            <div className="mx-auto h-12 w-12 bg-indigo-100 rounded-full flex items-center justify-center mb-4">
              <svg className="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Your Resume</h2>
            <p className="text-gray-600 mb-6">Get matched with the perfect job opportunities</p>
          </div>
          
          <div className="border-2 border-dashed border-indigo-300 rounded-xl p-8 bg-indigo-50/30">
            <div className="text-center">
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleFileUpload}
                disabled={uploading}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-6 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700 transition-colors"
              />
              <p className="text-sm text-gray-500 mt-3">Supports PDF, DOC, and DOCX files</p>
              {uploading && (
                <div className="mt-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
                  <p className="text-sm text-gray-600 mt-2">Processing your resume...</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Current Resume Info */}
        {resumes.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Resume</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-500">Skills</p>
                <p className="text-sm text-gray-900">{resumes[0].skills.join(', ')}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Experience</p>
                <p className="text-sm text-gray-900">{resumes[0].experience_years} years</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Education</p>
                <p className="text-sm text-gray-900">{resumes[0].education || 'Not specified'}</p>
              </div>
            </div>
          </div>
        )}

        {/* Job Matches */}
        <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Your Job Matches</h2>
              <p className="text-gray-600">AI-powered job recommendations based on your resume</p>
            </div>
            <div className="text-sm text-gray-500">
              {jobMatches.length} matches found
            </div>
          </div>
          
          {jobMatches.length === 0 ? (
            <div className="text-center py-12">
              <div className="mx-auto h-16 w-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <svg className="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No matches yet</h3>
              <p className="text-gray-500">Upload your resume to discover personalized job opportunities!</p>
            </div>
          ) : (
            <div className="space-y-6">
              {jobMatches.map((match, index) => (
                <div key={index} className="bg-gradient-to-r from-white to-indigo-50 border border-indigo-200 rounded-xl p-6 hover:shadow-lg transition-all duration-300 hover:border-indigo-300">
                  <div className="flex justify-between items-start mb-6">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-xl font-bold text-gray-900">{match.job.title}</h3>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                          {Math.round(match.match_percentage)}% Match
                        </span>
                      </div>
                      <p className="text-gray-600 text-lg mb-2">{match.job.company} • {match.job.location}</p>
                      <p className="text-gray-500 text-sm">{match.job.description}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-3xl font-bold text-indigo-600">
                        {Math.round(match.match_percentage)}%
                      </div>
                      <div className="text-sm text-gray-500">Compatibility</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div>
                      <h4 className="text-sm font-semibold text-green-700 mb-3 flex items-center">
                        <svg className="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        Your Skills ({match.matched_skills.length})
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {match.matched_skills.map((skill, idx) => (
                          <span key={idx} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 border border-green-200">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-orange-700 mb-3 flex items-center">
                        <svg className="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        Skills to Learn ({match.missing_skills.length})
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {match.missing_skills.map((skill, idx) => (
                          <span key={idx} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800 border border-orange-200">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4 mb-6">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
                      <svg className="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                      AI Analysis
                    </h4>
                    <p className="text-sm text-gray-600">{match.reasoning}</p>
                  </div>

                  <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                    <div className="flex items-center space-x-4">
                      <div className="text-sm text-gray-500">
                        <span className="font-medium">Salary:</span> ${match.job.salary_min?.toLocaleString()} - ${match.job.salary_max?.toLocaleString()}
                      </div>
                    </div>
                    <button 
                      onClick={() => handleApplyForJob(match.job.id)}
                      disabled={applying === match.job.id}
                      className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-indigo-700 hover:to-purple-700 text-sm font-medium transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {applying === match.job.id ? (
                        <div className="flex items-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Applying...
                        </div>
                      ) : (
                        'Apply Now'
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;
