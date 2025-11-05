import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

interface InterviewAnalytics {
  interview_id: number;
  candidate_id: string;
  candidate_name: string;
  job_title: string;
  overall_score: number;
  fraud_detection: {
    passed: boolean;
    score: number;
    red_flags: string[];
  };
  eye_tracking_analysis: {
    attention_score: number;
    eye_movements: number;
    distraction_count: number;
    focus_quality: string;
  };
  speech_analysis: {
    confidence: number;
    clarity: number;
    communication_quality: number;
  };
  technical_assessment: {
    score: number;
    relevance: number;
    technical_depth: number;
    keywords_found: string[];
    strengths: string[];
    areas_for_improvement: string[];
  };
  interview_answers?: Array<{
    question_id: number;
    question: string;
    answer: string;
    score: number;
    keywords_found: string[];
  }>;
  recommendation: string;
  completed_at: string;
  requires_review: boolean;
}

const InterviewAnalytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<InterviewAnalytics[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedInterview, setSelectedInterview] = useState<InterviewAnalytics | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/admin/interview-analytics', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      } else {
        toast.error('Failed to fetch analytics data');
      }
    } catch (error) {
      toast.error('Error fetching analytics data');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 90) return 'bg-green-100';
    if (score >= 80) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const calculateAverageScore = (interviews: InterviewAnalytics[]) => {
    if (interviews.length === 0) return 0;
    const total = interviews.reduce((sum, interview) => sum + interview.overall_score, 0);
    return total / interviews.length;
  };

  const getTopPerformers = (interviews: InterviewAnalytics[]) => {
    return [...interviews]
      .sort((a, b) => b.overall_score - a.overall_score)
      .slice(0, 3);
  };

  const getFraudDetectionStats = (interviews: InterviewAnalytics[]) => {
    const passed = interviews.filter(i => i.fraud_detection.passed).length;
    const failed = interviews.length - passed;
    return { passed, failed, total: interviews.length };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  const averageScore = calculateAverageScore(analytics);
  const topPerformers = getTopPerformers(analytics);
  const fraudStats = getFraudDetectionStats(analytics);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Interview Analytics</h1>
              <p className="text-gray-600">Comprehensive analysis of candidate interviews</p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => window.location.href = '/admin/dashboard'}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
              >
                Back to Dashboard
              </button>
              <button
                onClick={logout}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {[
                { id: 'overview', name: 'Overview' },
                { id: 'interviews', name: 'All Interviews' },
                { id: 'performance', name: 'Performance Analysis' },
                { id: 'fraud', name: 'Fraud Detection' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-indigo-100 rounded-lg">
                    <svg className="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Interviews</p>
                    <p className="text-2xl font-semibold text-gray-900">{analytics.length}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Average Score</p>
                    <p className={`text-2xl font-semibold ${getScoreColor(averageScore)}`}>
                      {averageScore.toFixed(1)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Fraud Detection Passed</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {fraudStats.passed}/{fraudStats.total}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <svg className="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Top Performers</p>
                    <p className="text-2xl font-semibold text-gray-900">{topPerformers.length}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Top Performers */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Top Performers</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {topPerformers.map((interview, index) => (
                    <div key={interview.interview_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold ${
                          index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : 'bg-orange-500'
                        }`}>
                          {index + 1}
                        </div>
                        <div>
                          <h4 className="text-lg font-semibold text-gray-900">{interview.candidate_name}</h4>
                          <p className="text-gray-600">{interview.job_title}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${getScoreColor(interview.overall_score)}`}>
                          {interview.overall_score.toFixed(1)}
                        </div>
                        <div className="text-sm text-gray-500">Overall Score</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* All Interviews Tab */}
        {activeTab === 'interviews' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">All Interviews</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {analytics.map((interview) => (
                  <div key={interview.interview_id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                       onClick={() => setSelectedInterview(interview)}>
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="text-lg font-semibold text-gray-900">{interview.candidate_name}</h4>
                        <p className="text-gray-600">{interview.job_title}</p>
                        <div className="mt-2 flex space-x-4 text-sm text-gray-500">
                          <span>Interview #{interview.interview_id}</span>
                          <span>•</span>
                          <span>{new Date(interview.completed_at).toLocaleDateString()}</span>
                          <span>•</span>
                          <span className={interview.fraud_detection.passed ? 'text-green-600' : 'text-red-600'}>
                            Fraud: {interview.fraud_detection.passed ? 'Passed' : 'Failed'}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${getScoreColor(interview.overall_score)}`}>
                          {interview.overall_score.toFixed(1)}
                        </div>
                        <div className="text-sm text-gray-500">Overall Score</div>
                        <div className="mt-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            interview.requires_review ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                          }`}>
                            {interview.requires_review ? 'Review Required' : 'Approved'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Performance Analysis Tab */}
        {activeTab === 'performance' && (
          <div className="space-y-8">
            {/* Score Distribution */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Score Distribution</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {analytics.filter(i => i.overall_score >= 90).length}
                  </div>
                  <div className="text-sm text-gray-500">Excellent (90+)</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-yellow-600">
                    {analytics.filter(i => i.overall_score >= 80 && i.overall_score < 90).length}
                  </div>
                  <div className="text-sm text-gray-500">Good (80-89)</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-red-600">
                    {analytics.filter(i => i.overall_score < 80).length}
                  </div>
                  <div className="text-sm text-gray-500">Needs Improvement (&lt;80)</div>
                </div>
              </div>
            </div>

            {/* Component Analysis */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Eye Tracking Analysis</h3>
                <div className="space-y-3">
                  {analytics.map((interview) => (
                    <div key={interview.interview_id} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">{interview.candidate_name}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${interview.eye_tracking_analysis.attention_score * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">
                          {(interview.eye_tracking_analysis.attention_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Speech Analysis</h3>
                <div className="space-y-3">
                  {analytics.map((interview) => (
                    <div key={interview.interview_id} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">{interview.candidate_name}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full" 
                            style={{ width: `${interview.speech_analysis.confidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">
                          {(interview.speech_analysis.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Fraud Detection Tab */}
        {activeTab === 'fraud' && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Fraud Detection Summary</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">{fraudStats.passed}</div>
                  <div className="text-sm text-gray-500">Passed</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-red-600">{fraudStats.failed}</div>
                  <div className="text-sm text-gray-500">Failed</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {((fraudStats.passed / fraudStats.total) * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-500">Pass Rate</div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Fraud Detection Details</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {analytics.map((interview) => (
                    <div key={interview.interview_id} className="flex justify-between items-center p-4 border border-gray-200 rounded-lg">
                      <div>
                        <h4 className="text-lg font-semibold text-gray-900">{interview.candidate_name}</h4>
                        <p className="text-gray-600">{interview.job_title}</p>
                      </div>
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${
                          interview.fraud_detection.passed ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {(interview.fraud_detection.score * 100).toFixed(1)}%
                        </div>
                        <div className="text-sm text-gray-500">
                          {interview.fraud_detection.passed ? 'Passed' : 'Failed'}
                        </div>
                        {interview.fraud_detection.red_flags.length > 0 && (
                          <div className="mt-2">
                            <span className="text-xs text-red-600">
                              {interview.fraud_detection.red_flags.length} red flags
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Interview Detail Modal */}
      {selectedInterview && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Interview Details - {selectedInterview.candidate_name}
              </h3>
              <button
                onClick={() => setSelectedInterview(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-6">
              {/* Overall Score */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Overall Assessment</h4>
                <div className="flex justify-between items-center">
                  <span>Overall Score:</span>
                  <span className={`text-2xl font-bold ${getScoreColor(selectedInterview.overall_score)}`}>
                    {selectedInterview.overall_score.toFixed(1)}
                  </span>
                </div>
                <div className="mt-2">
                  <span>Recommendation: </span>
                  <span className="font-medium">{selectedInterview.recommendation}</span>
                </div>
              </div>

              {/* Technical Assessment */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Technical Assessment</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Score:</span>
                    <span className="ml-2 font-medium">{(selectedInterview.technical_assessment.score * 100).toFixed(1)}%</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Relevance:</span>
                    <span className="ml-2 font-medium">{(selectedInterview.technical_assessment.relevance * 100).toFixed(1)}%</span>
                  </div>
                </div>
                <div className="mt-2">
                  <span className="text-gray-600">Keywords Found:</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {selectedInterview.technical_assessment.keywords_found.map((keyword, index) => (
                      <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Eye Tracking */}
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Eye Tracking Analysis</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Attention Score:</span>
                    <span className="ml-2 font-medium">{(selectedInterview.eye_tracking_analysis.attention_score * 100).toFixed(1)}%</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Focus Quality:</span>
                    <span className="ml-2 font-medium">{selectedInterview.eye_tracking_analysis.focus_quality}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Eye Movements:</span>
                    <span className="ml-2 font-medium">{selectedInterview.eye_tracking_analysis.eye_movements}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Distractions:</span>
                    <span className="ml-2 font-medium">{selectedInterview.eye_tracking_analysis.distraction_count}</span>
                  </div>
                </div>
              </div>

              {/* Speech Analysis */}
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Speech Analysis</h4>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Confidence:</span>
                    <span className="ml-2 font-medium">{(selectedInterview.speech_analysis.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Clarity:</span>
                    <span className="ml-2 font-medium">{(selectedInterview.speech_analysis.clarity * 100).toFixed(1)}%</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Communication:</span>
                    <span className="ml-2 font-medium">{(selectedInterview.speech_analysis.communication_quality * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>

              {/* Fraud Detection */}
              <div className="bg-red-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Fraud Detection</h4>
                <div className="flex justify-between items-center">
                  <span>Status:</span>
                  <span className={`font-medium ${selectedInterview.fraud_detection.passed ? 'text-green-600' : 'text-red-600'}`}>
                    {selectedInterview.fraud_detection.passed ? 'Passed' : 'Failed'}
                  </span>
                </div>
                <div className="mt-2">
                  <span className="text-gray-600">Score:</span>
                  <span className="ml-2 font-medium">{(selectedInterview.fraud_detection.score * 100).toFixed(1)}%</span>
                </div>
                {selectedInterview.fraud_detection.red_flags.length > 0 && (
                  <div className="mt-2">
                    <span className="text-gray-600">Red Flags:</span>
                    <ul className="mt-1 list-disc list-inside text-sm text-red-600">
                      {selectedInterview.fraud_detection.red_flags.map((flag, index) => (
                        <li key={index}>{flag}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InterviewAnalytics;




