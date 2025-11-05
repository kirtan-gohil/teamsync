import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

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

interface FraudAnalysis {
  is_authentic: boolean;
  confidence_score: number;
  red_flags: string[];
  analysis: {
    voice_consistency: string;
    response_time: string;
    content_authenticity: string;
    background_noise: string;
  };
}

const Interview: React.FC = () => {
  const { interviewId } = useParams<{ interviewId: string }>();
  const navigate = useNavigate();
  
  const [interviewData, setInterviewData] = useState<InterviewData | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const [answers, setAnswers] = useState<{[key: number]: string}>({});
  const [isInterviewStarted, setIsInterviewStarted] = useState(false);
  const [fraudAnalysis, setFraudAnalysis] = useState<FraudAnalysis | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (interviewId) {
      fetchInterviewQuestions();
    }
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

  const fetchInterviewQuestions = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/interview/${interviewId}/questions`);
      const data = await response.json();
      setInterviewData(data);
    } catch (error) {
      toast.error('Failed to load interview questions');
    }
  };

  const startInterview = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/interview/${interviewId}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      setIsInterviewStarted(true);
      toast.success('Interview started! Please ensure your microphone is working.');
    } catch (error) {
      toast.error('Failed to start interview');
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
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
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);
      formData.append('duration', audioBlob.size.toString());
      formData.append('quality', 'good');

      const response = await fetch(`http://localhost:8000/api/interview/${interviewId}/voice/stop`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      toast.success('Audio processed successfully');
      
      // Mock transcription for demo
      const mockTranscription = `This is a mock transcription of your response to: "${interviewData?.questions[currentQuestionIndex]?.question}"`;
      setAnswers(prev => ({
        ...prev,
        [currentQuestionIndex]: mockTranscription
      }));
    } catch (error) {
      toast.error('Failed to process audio');
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
          voice_confidence: 0.85 // Mock confidence
        })
      });

      const data = await response.json();
      setFraudAnalysis(data.fraud_analysis);
      
      if (data.fraud_analysis.is_authentic) {
        toast.success('Answer submitted successfully');
        nextQuestion();
      } else {
        toast.error('Fraud detected! Please answer authentically.');
      }
    } catch (error) {
      toast.error('Failed to submit answer');
    }
  };

  const nextQuestion = () => {
    if (interviewData && currentQuestionIndex < interviewData.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setFraudAnalysis(null);
    } else {
      completeInterview();
    }
  };

  const completeInterview = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/interview/${interviewId}/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          total_answers: interviewData?.questions.length || 0,
          fraud_score: 0.85,
          technical_score: 0.8
        })
      });

      const data = await response.json();
      toast.success('Interview completed successfully!');
      navigate('/dashboard', { state: { interviewResults: data } });
    } catch (error) {
      toast.error('Failed to complete interview');
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
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Interview Session</h1>
              <p className="text-gray-600">Question {currentQuestionIndex + 1} of {interviewData.total_questions}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Estimated Duration</p>
              <p className="font-semibold">{interviewData.estimated_duration}</p>
            </div>
          </div>
        </div>

        {/* Fraud Detection Status */}
        {fraudAnalysis && (
          <div className={`mb-6 p-4 rounded-lg ${
            fraudAnalysis.is_authentic 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full mr-3 ${
                fraudAnalysis.is_authentic ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <div>
                <p className={`font-semibold ${
                  fraudAnalysis.is_authentic ? 'text-green-800' : 'text-red-800'
                }`}>
                  {fraudAnalysis.is_authentic ? 'Authentic Response' : 'Fraud Detected'}
                </p>
                <p className="text-sm text-gray-600">
                  Confidence: {(fraudAnalysis.confidence_score * 100).toFixed(1)}%
                </p>
                {fraudAnalysis.red_flags.length > 0 && (
                  <p className="text-sm text-red-600">
                    Red flags: {fraudAnalysis.red_flags.join(', ')}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Interview Content */}
        <div className="bg-white rounded-lg shadow-md p-6">
          {!isInterviewStarted ? (
            <div className="text-center">
              <h2 className="text-xl font-semibold mb-4">Ready to Start Your Interview?</h2>
              <div className="mb-6">
                <h3 className="font-semibold mb-2">Instructions:</h3>
                <ul className="text-left max-w-md mx-auto space-y-1 text-gray-600">
                  <li>• Speak clearly and directly into your microphone</li>
                  <li>• Answer each question within the time limit</li>
                  <li>• Be honest and authentic in your responses</li>
                  <li>• The system will detect any suspicious behavior</li>
                </ul>
              </div>
              <button
                onClick={startInterview}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Start Interview
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
              <div className="flex justify-between">
                <button
                  onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
                  disabled={currentQuestionIndex === 0}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                
                <button
                  onClick={submitAnswer}
                  disabled={!answers[currentQuestionIndex]}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {currentQuestionIndex === interviewData.questions.length - 1 ? 'Complete Interview' : 'Submit Answer'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Interview;









