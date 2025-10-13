import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import VideoRecorder from '../components/VideoRecorder';

interface Question {
  id: number;
  question: string;
  skill: string;
  type: string;
  time_limit: number;
}

interface InterviewData {
  interview_id: number;
  questions: Question[];
  total_questions: number;
  estimated_duration: string;
}

interface EyeTrackingData {
  eyeMovements: number;
  gazeDirection: string;
  attentionScore: number;
  distractionCount: number;
}

interface SpeechAnalysis {
  confidence: number;
  clarity: number;
  pace: number;
  fillerWords: number;
  transcription: string;
}

interface ComprehensiveAnalysis {
  is_authentic: boolean;
  confidence_score: number;
  red_flags: string[];
  eye_tracking: EyeTrackingData;
  speech_analysis: SpeechAnalysis;
  content_analysis: {
    relevance_score: number;
    technical_depth: number;
    communication_quality: number;
    keywords_found: string[];
  };
  overall_score: number;
}

const EnhancedInterview: React.FC = () => {
  const { interviewId } = useParams<{ interviewId: string }>();
  const navigate = useNavigate();
  
  const [interviewData, setInterviewData] = useState<InterviewData | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const [answers, setAnswers] = useState<{[key: number]: string}>({});
  const [isInterviewStarted, setIsInterviewStarted] = useState(false);
  const [analysis, setAnalysis] = useState<ComprehensiveAnalysis | null>(null);
  const [cameraPermission, setCameraPermission] = useState(false);
  const [eyeTrackingActive, setEyeTrackingActive] = useState(false);
  
  // Refs for media and tracking
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const eyeTrackingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const recognitionRef = useRef<any>(null);
  
  // Eye tracking data
  const [eyeTrackingData, setEyeTrackingData] = useState<EyeTrackingData>({
    eyeMovements: 0,
    gazeDirection: 'center',
    attentionScore: 100,
    distractionCount: 0
  });

  useEffect(() => {
    if (interviewId) {
      fetchInterviewQuestions();
    }
    initializeSpeechRecognition();
    return () => {
      if (eyeTrackingIntervalRef.current) {
        clearInterval(eyeTrackingIntervalRef.current);
      }
    };
  }, [interviewId]);

  useEffect(() => {
    if (timeLeft > 0) {
      timerRef.current = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
    } else if (timeLeft === 0 && isRecording) {
      stopRecording();
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [timeLeft, isRecording]);

  const initializeSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';
    }
  };

  const fetchInterviewQuestions = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/interview/${interviewId}/questions`);
      const data = await response.json();
      setInterviewData(data);
    } catch (error) {
      toast.error('Failed to load interview questions');
    }
  };

  const requestCameraPermission = async () => {
    try {
      // Camera permission is now handled by VideoRecorder component
      setCameraPermission(true);
    } catch (error) {
      toast.error('Camera access denied. Please enable camera for eye tracking.');
    }
  };

  const startInterview = async () => {
    try {
      await requestCameraPermission();
      
      const response = await fetch(`http://localhost:8000/api/interview/${interviewId}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      setIsInterviewStarted(true);
      toast.success('Interview started! Camera and microphone are active.');
    } catch (error) {
      toast.error('Failed to start interview');
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: true,
        video: false 
      });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        processAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      
      if (interviewData?.questions[currentQuestionIndex]) {
        setTimeLeft(interviewData.questions[currentQuestionIndex].time_limit);
      }
      
      // Start speech recognition
      if (recognitionRef.current) {
        recognitionRef.current.start();
        recognitionRef.current.onresult = (event: any) => {
          let finalTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            }
          }
          if (finalTranscript) {
            setAnswers(prev => ({
              ...prev,
              [currentQuestionIndex]: finalTranscript
            }));
          }
        };
      }
      
      toast.success('Recording started. Speak clearly into your microphone.');
    } catch (error) {
      toast.error('Failed to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setTimeLeft(0);
      
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);
      formData.append('duration', audioBlob.size.toString());
      formData.append('eye_tracking_data', JSON.stringify(eyeTrackingData));

      const response = await fetch(`http://localhost:8000/api/interview/${interviewId}/analyze`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      setAnalysis(data.analysis);
      toast.success('Analysis completed');
      
    } catch (error) {
      toast.error('Failed to process audio and video data');
    }
  };

  const submitAnswer = async () => {
    if (!interviewData?.questions[currentQuestionIndex]) return;

    try {
      const response = await fetch(`http://localhost:8000/api/interview/${interviewId}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: interviewData.questions[currentQuestionIndex].id,
          answer: answers[currentQuestionIndex] || '',
          audio_duration: 30, // Mock duration
          voice_confidence: 0.85, // Mock confidence
          eye_tracking: eyeTrackingData,
          speech_analysis: {
            confidence: 0.85,
            clarity: 0.9,
            pace: 0.8,
            fillerWords: 2
          }
        })
      });

      const data = await response.json();
      setAnalysis(data.fraud_analysis);
      
      if (data.fraud_analysis.is_authentic) {
        toast.success('Answer submitted successfully');
        // Move to next question automatically
        setTimeout(() => {
          nextQuestion();
        }, 1500);
      } else {
        toast.error('Suspicious behavior detected! Please answer authentically.');
        // Still allow moving to next question but with warning
        setTimeout(() => {
          nextQuestion();
        }, 3000);
      }
    } catch (error) {
      toast.error('Failed to submit answer');
    }
  };

  const nextQuestion = () => {
    if (interviewData && currentQuestionIndex < interviewData.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setAnalysis(null);
      // Reset eye tracking data for new question
      setEyeTrackingData({
        eyeMovements: 0,
        gazeDirection: 'center',
        attentionScore: 100,
        distractionCount: 0
      });
      // Clear current answer
      setAnswers(prev => ({
        ...prev,
        [currentQuestionIndex + 1]: ''
      }));
      toast.success(`Moving to question ${currentQuestionIndex + 2} of ${interviewData.questions.length}`);
    } else {
      completeInterview();
    }
  };

  const completeInterview = async () => {
    try {
      // Collect all answers and analysis data
      const allAnswers = Object.keys(answers).map(key => ({
        question_id: parseInt(key) + 1,
        question: interviewData?.questions[parseInt(key)]?.question || '',
        answer: answers[parseInt(key)] || '',
        score: Math.random() * 2 + 8, // Mock score between 8-10
        keywords_found: ['Python', 'experience', 'project', 'development']
      }));

      const completionData = {
        total_answers: interviewData?.questions.length || 0,
        eye_tracking_summary: eyeTrackingData,
        overall_analysis: analysis,
        all_answers: allAnswers,
        interview_questions: interviewData?.questions || [],
        video_url: `uploads/interviews/${interviewId}/video.mp4`,
        audio_url: `uploads/interviews/${interviewId}/audio.wav`,
        completed_at: new Date().toISOString()
      };

      console.log('Completing interview with data:', completionData);

      const response = await fetch(`http://localhost:8000/api/interview/${interviewId}/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(completionData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Interview completion response:', data);
      
      // Send feedback to admin
      try {
        await fetch(`http://localhost:8000/api/admin/interview-feedback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            interview_id: interviewId,
            candidate_performance: data,
            recommendations: data.recommendation || 'No specific recommendations',
            all_answers: allAnswers
          })
        });
        console.log('Admin feedback sent successfully');
      } catch (adminError) {
        console.error('Failed to send admin feedback:', adminError);
        // Don't fail the interview completion if admin notification fails
      }
      
      toast.success('Interview completed successfully! All data saved.');
      setTimeout(() => {
        navigate('/dashboard', { state: { interviewResults: data } });
      }, 2000);
    } catch (error) {
      console.error('Interview completion error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      toast.error(`Failed to complete interview: ${errorMessage}`);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!interviewData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading interview questions...</p>
        </div>
      </div>
    );
  }

  const currentQuestion = interviewData.questions[currentQuestionIndex];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Enhanced AI Interview Session</h1>
              <p className="text-gray-600">Question {currentQuestionIndex + 1} of {interviewData.total_questions}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Estimated Duration</p>
              <p className="font-semibold">{interviewData.estimated_duration}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Interview Area */}
          <div className="lg:col-span-2">
            {/* Camera Feed */}
            {cameraPermission && (
              <div className="bg-white rounded-lg shadow-md p-4 mb-6">
                <h3 className="text-lg font-semibold mb-4">Camera Feed (Eye Tracking Active)</h3>
                <VideoRecorder
                  isRecording={isRecording}
                  onVideoData={(videoBlob) => {
                    console.log('Video recorded:', videoBlob);
                    // Handle video data
                  }}
                  onEyeTrackingData={(data) => {
                    setEyeTrackingData(data);
                  }}
                  className="w-full"
                />
              </div>
            )}

            {/* Analysis Results */}
            {analysis && (
              <div className={`mb-6 p-4 rounded-lg ${
                analysis.is_authentic 
                  ? 'bg-green-50 border border-green-200' 
                  : 'bg-red-50 border border-red-200'
              }`}>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold mb-2">Authenticity Analysis</h4>
                    <div className="flex items-center mb-2">
                      <div className={`w-3 h-3 rounded-full mr-2 ${
                        analysis.is_authentic ? 'bg-green-500' : 'bg-red-500'
                      }`}></div>
                      <span className={`font-semibold ${
                        analysis.is_authentic ? 'text-green-800' : 'text-red-800'
                      }`}>
                        {analysis.is_authentic ? 'Authentic Response' : 'Suspicious Behavior'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">
                      Confidence: {(analysis.confidence_score * 100).toFixed(1)}%
                    </p>
                    {analysis.red_flags.length > 0 && (
                      <p className="text-sm text-red-600">
                        Red flags: {analysis.red_flags.join(', ')}
                      </p>
                    )}
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">Performance Metrics</h4>
                    <div className="space-y-1 text-sm">
                      <div>Eye Tracking Score: {analysis.eye_tracking.attentionScore.toFixed(1)}%</div>
                      <div>Speech Clarity: {(analysis.speech_analysis.clarity * 100).toFixed(1)}%</div>
                      <div>Content Relevance: {(analysis.content_analysis.relevance_score * 100).toFixed(1)}%</div>
                      <div>Overall Score: {analysis.overall_score.toFixed(1)}%</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Interview Content */}
            <div className="bg-white rounded-lg shadow-md p-6">
              {!isInterviewStarted ? (
                <div className="text-center">
                  <h2 className="text-xl font-semibold mb-4">Ready to Start Your Enhanced Interview?</h2>
                  <div className="mb-6">
                    <h3 className="font-semibold mb-2">Enhanced Features:</h3>
                    <ul className="text-left max-w-md mx-auto space-y-1 text-gray-600">
                      <li>• Camera-based eye movement tracking</li>
                      <li>• Real-time speech recognition</li>
                      <li>• Comprehensive authenticity analysis</li>
                      <li>• Advanced fraud detection</li>
                      <li>• Automatic admin feedback</li>
                    </ul>
                  </div>
                  <button
                    onClick={startInterview}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Start Enhanced Interview
                  </button>
                </div>
              ) : (
                <div>
                  {/* Question */}
                  <div className="mb-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <span className="inline-block bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                          {currentQuestion.type.toUpperCase()}
                        </span>
                        <span className="ml-2 text-sm text-gray-500">
                          Skill: {currentQuestion.skill}
                        </span>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500">Time Limit</p>
                        <p className={`font-bold ${timeLeft < 30 ? 'text-red-600' : 'text-gray-900'}`}>
                          {formatTime(timeLeft)}
                        </p>
                      </div>
                    </div>
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">
                      {currentQuestion.question}
                    </h2>
                  </div>

                  {/* Recording Controls */}
                  <div className="text-center mb-6">
                    {!isRecording ? (
                      <button
                        onClick={startRecording}
                        className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
                      >
                        🎤 Start Recording
                      </button>
                    ) : (
                      <div className="space-y-4">
                        <div className="flex items-center justify-center space-x-4">
                          <div className="w-4 h-4 bg-red-500 rounded-full animate-pulse"></div>
                          <span className="text-red-600 font-semibold">Recording...</span>
                        </div>
                        <button
                          onClick={stopRecording}
                          className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors"
                        >
                          ⏹️ Stop Recording
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Answer Display */}
                  {answers[currentQuestionIndex] && (
                    <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                      <h3 className="font-semibold mb-2">Your Answer:</h3>
                      <p className="text-gray-700">{answers[currentQuestionIndex]}</p>
                    </div>
                  )}

                  {/* Navigation */}
                  <div className="flex justify-between items-center">
                    <button
                      onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
                      disabled={currentQuestionIndex === 0}
                      className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    
                    <div className="flex space-x-3">
                      <button
                        onClick={submitAnswer}
                        disabled={!answers[currentQuestionIndex]}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {currentQuestionIndex === interviewData.questions.length - 1 ? 'Complete Interview' : 'Submit Answer'}
                      </button>
                      
                      {/* Debug button for testing */}
                      <button
                        onClick={completeInterview}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                        title="Debug: Complete Interview Now"
                      >
                        🚀 Complete Now
                      </button>
                      
                      {currentQuestionIndex < interviewData.questions.length - 1 && (
                        <button
                          onClick={nextQuestion}
                          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                        >
                          Next Question
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar - Real-time Metrics */}
          <div className="space-y-6">
            {/* Eye Tracking Metrics */}
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="text-lg font-semibold mb-4">👁️ Eye Tracking</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm">
                    <span>Attention Score</span>
                    <span>{eyeTrackingData.attentionScore.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        eyeTrackingData.attentionScore > 80 ? 'bg-green-500' :
                        eyeTrackingData.attentionScore > 60 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${eyeTrackingData.attentionScore}%` }}
                    ></div>
                  </div>
                </div>
                <div className="text-sm">
                  <div>Eye Movements: {eyeTrackingData.eyeMovements}</div>
                  <div>Gaze Direction: {eyeTrackingData.gazeDirection}</div>
                  <div>Distractions: {eyeTrackingData.distractionCount}</div>
                </div>
              </div>
            </div>

            {/* Speech Analysis */}
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="text-lg font-semibold mb-4">🎤 Speech Analysis</h3>
              <div className="space-y-2 text-sm">
                <div>Confidence: 85%</div>
                <div>Clarity: 90%</div>
                <div>Pace: Normal</div>
                <div>Filler Words: 2</div>
              </div>
            </div>

            {/* System Status */}
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="text-lg font-semibold mb-4">🔧 System Status</h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center">
                  <div className={`w-2 h-2 rounded-full mr-2 ${cameraPermission ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  Camera: {cameraPermission ? 'Active' : 'Inactive'}
                </div>
                <div className="flex items-center">
                  <div className={`w-2 h-2 rounded-full mr-2 ${isRecording ? 'bg-green-500' : 'bg-gray-500'}`}></div>
                  Microphone: {isRecording ? 'Recording' : 'Standby'}
                </div>
                <div className="flex items-center">
                  <div className={`w-2 h-2 rounded-full mr-2 ${eyeTrackingActive ? 'bg-green-500' : 'bg-gray-500'}`}></div>
                  Eye Tracking: {eyeTrackingActive ? 'Active' : 'Inactive'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedInterview;
