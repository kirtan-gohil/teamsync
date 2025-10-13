import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

interface InterviewAnswer {
  question_id: number;
  question: string;
  answer: string;
  score: number;
  keywords_found: string[];
}

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
  interview_answers?: InterviewAnswer[];
  recommendation: string;
  completed_at: string;
  requires_review: boolean;
}

const InterviewAnalytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<InterviewAnalytics[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedInterview, setSelectedInterview] = useState<InterviewAnalytics | null>(null);

  useEffect(() => {
    fetchInterviewAnalytics();
  }, []);

  const fetchInterviewAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/admin/interview-analytics');
      const data = await response.json();
      // Ensure data is an array
      const analyticsData = Array.isArray(data) ? data : [];
      setAnalytics(analyticsData);
      
      // Show notification if there are new interviews
      if (analyticsData.length > 0) {
        const recentCount = analyticsData.filter(interview => {
          const interviewDate = new Date(interview.completed_at);
          const now = new Date();
          const diffHours = (now.getTime() - interviewDate.getTime()) / (1000 * 60 * 60);
          return diffHours < 24; // Interviews completed in last 24 hours
        }).length;
        
        if (recentCount > 0) {
          toast.success(`${recentCount} new interview(s) completed recently!`, {
            duration: 5000,
            style: {
              background: '#10B981',
              color: 'white',
              fontSize: '14px',
              padding: '16px',
            }
          });
        }
      }
    } catch (error) {
      toast.error('Failed to load interview analytics');
      setAnalytics([]);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading interview analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Interview Analytics Dashboard</h1>
              <p className="text-gray-600 mt-2">Comprehensive analysis of candidate interviews with AI-powered insights</p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  setLoading(true);
                  fetchInterviewAnalytics();
                }}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>Refresh</span>
              </button>
              
              <button
                onClick={async () => {
                  try {
                    const response = await fetch('http://localhost:8000/api/admin/test-interview', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' }
                    });
                    const data = await response.json();
                    toast.success(`Test interview added! ID: ${data.interview_id}`);
                    fetchInterviewAnalytics();
                  } catch (error) {
                    toast.error('Failed to add test interview');
                  }
                }}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                <span>Add Test</span>
              </button>
              
              <button
                onClick={async () => {
                  try {
                    const response = await fetch('http://localhost:8000/api/admin/debug-interviews');
                    const data = await response.json();
                    console.log('Debug data:', data);
                    toast.success(`Debug: Global: ${data.global_completed_interviews}, Storage: ${data.storage_class_interviews}`, {
                      duration: 8000
                    });
                  } catch (error) {
                    toast.error('Failed to get debug data');
                  }
                }}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Debug</span>
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Interview List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold">Recent Interviews</h2>
              </div>
              <div className="divide-y divide-gray-200">
                {analytics.map((interview) => (
                  <div
                    key={interview.interview_id}
                    className="p-6 hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedInterview(interview)}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-gray-900">{interview.candidate_name}</h3>
                        <p className="text-sm text-gray-600">{interview.job_title}</p>
                        <p className="text-xs text-gray-500">
                          Completed: {new Date(interview.completed_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          getScoreBgColor(interview.overall_score)
                        } ${getScoreColor(interview.overall_score)}`}>
                          {interview.overall_score.toFixed(1)}%
                        </div>
                        {interview.requires_review && (
                          <div className="mt-1 text-xs text-red-600 font-medium">Requires Review</div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Detailed Analysis */}
          <div className="space-y-6">
            {selectedInterview ? (
              <>
                {/* Overall Score */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold mb-4">Overall Performance</h3>
                  <div className="text-center">
                    <div className={`text-4xl font-bold ${getScoreColor(selectedInterview.overall_score)}`}>
                      {selectedInterview.overall_score.toFixed(1)}%
                    </div>
                    <p className="text-gray-600 mt-2">{selectedInterview.recommendation}</p>
                  </div>
                </div>

                {/* Fraud Detection */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold mb-4">🔒 Fraud Detection</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>Authenticity Score</span>
                      <span className={`font-semibold ${getScoreColor(selectedInterview.fraud_detection.score * 100)}`}>
                        {(selectedInterview.fraud_detection.score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-2 ${
                        selectedInterview.fraud_detection.passed ? 'bg-green-500' : 'bg-red-500'
                      }`}></div>
                      <span className="text-sm">
                        {selectedInterview.fraud_detection.passed ? 'Passed' : 'Failed'}
                      </span>
                    </div>
                    {selectedInterview.fraud_detection.red_flags.length > 0 && (
                      <div className="text-sm text-red-600">
                        <p className="font-medium">Red Flags:</p>
                        <ul className="list-disc list-inside">
                          {selectedInterview.fraud_detection.red_flags.map((flag, index) => (
                            <li key={index}>{flag}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>

                {/* Eye Tracking Analysis */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold mb-4">👁️ Eye Tracking Analysis</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>Attention Score</span>
                      <span className={`font-semibold ${getScoreColor(selectedInterview.eye_tracking_analysis.attention_score * 100)}`}>
                        {(selectedInterview.eye_tracking_analysis.attention_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Eye Movements</span>
                      <span>{selectedInterview.eye_tracking_analysis.eye_movements}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Distractions</span>
                      <span>{selectedInterview.eye_tracking_analysis.distraction_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Focus Quality</span>
                      <span className={`font-medium ${
                        selectedInterview.eye_tracking_analysis.focus_quality === 'Good' ? 'text-green-600' : 'text-yellow-600'
                      }`}>
                        {selectedInterview.eye_tracking_analysis.focus_quality}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Speech Analysis */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold mb-4">🎤 Speech Analysis</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>Confidence</span>
                      <span className={`font-semibold ${getScoreColor(selectedInterview.speech_analysis.confidence * 100)}`}>
                        {(selectedInterview.speech_analysis.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Clarity</span>
                      <span className={`font-semibold ${getScoreColor(selectedInterview.speech_analysis.clarity * 100)}`}>
                        {(selectedInterview.speech_analysis.clarity * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Communication Quality</span>
                      <span className={`font-semibold ${getScoreColor(selectedInterview.speech_analysis.communication_quality * 100)}`}>
                        {(selectedInterview.speech_analysis.communication_quality * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Technical Assessment */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold mb-4">💻 Technical Assessment</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>Technical Score</span>
                      <span className={`font-semibold ${getScoreColor(selectedInterview.technical_assessment.score * 100)}`}>
                        {(selectedInterview.technical_assessment.score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Relevance</span>
                      <span className={`font-semibold ${getScoreColor(selectedInterview.technical_assessment.relevance * 100)}`}>
                        {(selectedInterview.technical_assessment.relevance * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Technical Depth</span>
                      <span className={`font-semibold ${getScoreColor(selectedInterview.technical_assessment.technical_depth * 100)}`}>
                        {(selectedInterview.technical_assessment.technical_depth * 100).toFixed(1)}%
                      </span>
                    </div>
                    
                    {selectedInterview.technical_assessment.keywords_found.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Keywords Found:</p>
                        <div className="flex flex-wrap gap-1">
                          {selectedInterview.technical_assessment.keywords_found.map((keyword, index) => (
                            <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Interview Answers */}
                {selectedInterview.interview_answers && selectedInterview.interview_answers.length > 0 && (
                  <div className="bg-white rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-semibold mb-4">💬 Interview Answers</h3>
                    <div className="space-y-4">
                      {selectedInterview.interview_answers.map((answer, index) => (
                        <div key={answer.question_id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-medium text-gray-900">Question {answer.question_id}</h4>
                            <span className={`px-2 py-1 rounded text-sm font-medium ${
                              answer.score >= 8 ? 'bg-green-100 text-green-800' :
                              answer.score >= 6 ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              Score: {answer.score}/10
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{answer.question}</p>
                          <p className="text-sm text-gray-700 mb-3">{answer.answer}</p>
                          {answer.keywords_found.length > 0 && (
                            <div>
                              <p className="text-xs font-medium text-gray-500 mb-1">Keywords Found:</p>
                              <div className="flex flex-wrap gap-1">
                                {answer.keywords_found.map((keyword, idx) => (
                                  <span key={idx} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                                    {keyword}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Strengths and Improvements */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold mb-4">📊 Assessment Summary</h3>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-green-700 mb-2">Strengths:</h4>
                      <ul className="list-disc list-inside text-sm text-gray-700">
                        {selectedInterview.technical_assessment.strengths.map((strength, index) => (
                          <li key={index}>{strength}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-medium text-orange-700 mb-2">Areas for Improvement:</h4>
                      <ul className="list-disc list-inside text-sm text-gray-700">
                        {selectedInterview.technical_assessment.areas_for_improvement.map((area, index) => (
                          <li key={index}>{area}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <p className="text-gray-500">Select an interview to view detailed analysis</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterviewAnalytics;
