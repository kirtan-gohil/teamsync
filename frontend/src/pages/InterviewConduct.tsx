import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeftIcon,
  PlayIcon,
  PauseIcon,
  StopIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

interface Question {
  id: number;
  text: string;
  type: string;
  time_limit: number;
}

const InterviewConduct: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [responses, setResponses] = useState<string[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [interviewStatus, setInterviewStatus] = useState<'not_started' | 'in_progress' | 'completed'>('not_started');

  useEffect(() => {
    if (id) {
      fetchInterview(parseInt(id));
    }
  }, [id]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRecording && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(prev => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRecording, timeRemaining]);

  const fetchInterview = async (interviewId: number) => {
    try {
      // Mock questions for demo
      const mockQuestions: Question[] = [
        {
          id: 1,
          text: "Tell me about yourself and your background in software development.",
          type: "behavioral",
          time_limit: 300 // 5 minutes
        },
        {
          id: 2,
          text: "How would you approach designing a scalable microservices architecture?",
          type: "technical",
          time_limit: 600 // 10 minutes
        },
        {
          id: 3,
          text: "Describe a challenging project you worked on and how you overcame obstacles.",
          type: "situational",
          time_limit: 300 // 5 minutes
        },
        {
          id: 4,
          text: "What interests you most about this role and our company?",
          type: "motivational",
          time_limit: 180 // 3 minutes
        },
        {
          id: 5,
          text: "Do you have any questions for us about the role or company?",
          type: "closing",
          time_limit: 300 // 5 minutes
        }
      ];
      
      setQuestions(mockQuestions);
      setResponses(new Array(mockQuestions.length).fill(''));
    } catch (error) {
      console.error('Error fetching interview:', error);
      toast.error('Failed to load interview questions');
    }
  };

  const startInterview = () => {
    setInterviewStatus('in_progress');
    setTimeRemaining(questions[currentQuestionIndex]?.time_limit || 300);
    setIsRecording(true);
    toast.success('Interview started!');
  };

  const stopRecording = () => {
    setIsRecording(false);
    toast.success('Response recorded');
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setTimeRemaining(questions[currentQuestionIndex + 1]?.time_limit || 300);
      setIsRecording(true);
    } else {
      completeInterview();
    }
  };

  const completeInterview = () => {
    setInterviewStatus('completed');
    setIsRecording(false);
    toast.success('Interview completed successfully!');
  };

  const handleResponseChange = (response: string) => {
    const newResponses = [...responses];
    newResponses[currentQuestionIndex] = response;
    setResponses(newResponses);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getQuestionTypeColor = (type: string) => {
    switch (type) {
      case 'technical':
        return 'bg-blue-100 text-blue-800';
      case 'behavioral':
        return 'bg-green-100 text-green-800';
      case 'situational':
        return 'bg-purple-100 text-purple-800';
      case 'motivational':
        return 'bg-orange-100 text-orange-800';
      case 'closing':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-secondary-100 text-secondary-800';
    }
  };

  if (questions.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center space-x-4">
          <Link
            to="/interviews"
            className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-lg transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-secondary-900">AI Interview</h1>
            <p className="text-secondary-600 mt-1">
              Question {currentQuestionIndex + 1} of {questions.length}
            </p>
          </div>
        </div>
        
        {interviewStatus === 'in_progress' && (
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-2xl font-bold text-primary-600">
                {formatTime(timeRemaining)}
              </div>
              <div className="text-sm text-secondary-600">Time Remaining</div>
            </div>
            <div className={`w-3 h-3 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-400'}`}></div>
          </div>
        )}
      </motion.div>

      {/* Progress Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-secondary-900">Interview Progress</h3>
          <span className="text-sm text-secondary-600">
            {Math.round(((currentQuestionIndex + 1) / questions.length) * 100)}% Complete
          </span>
        </div>
        <div className="w-full bg-secondary-200 rounded-full h-2">
          <div 
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
          ></div>
        </div>
        <div className="flex justify-between mt-2">
          {questions.map((_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full ${
                index <= currentQuestionIndex ? 'bg-primary-600' : 'bg-secondary-300'
              }`}
            ></div>
          ))}
        </div>
      </motion.div>

      {/* Question Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getQuestionTypeColor(currentQuestion.type)}`}>
            {currentQuestion.type.charAt(0).toUpperCase() + currentQuestion.type.slice(1)} Question
          </span>
          <div className="flex items-center text-sm text-secondary-600">
            <ClockIcon className="h-4 w-4 mr-1" />
            {Math.floor(currentQuestion.time_limit / 60)} minutes
          </div>
        </div>
        
        <h2 className="text-xl font-semibold text-secondary-900 mb-6">
          {currentQuestion.text}
        </h2>

        {interviewStatus === 'not_started' && (
          <div className="text-center py-8">
            <PlayIcon className="h-16 w-16 text-primary-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-secondary-900 mb-2">Ready to Start?</h3>
            <p className="text-secondary-600 mb-6">
              Click the button below to begin the interview. You'll have time to think and respond to each question.
            </p>
            <button
              onClick={startInterview}
              className="btn-primary flex items-center mx-auto"
            >
              <PlayIcon className="h-5 w-5 mr-2" />
              Start Interview
            </button>
          </div>
        )}

        {interviewStatus === 'in_progress' && (
          <div className="space-y-6">
            <div className="bg-secondary-50 rounded-lg p-4">
              <h4 className="font-medium text-secondary-900 mb-2">Your Response</h4>
              <textarea
                value={responses[currentQuestionIndex]}
                onChange={(e) => handleResponseChange(e.target.value)}
                className="w-full h-32 px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Type your response here..."
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {isRecording && (
                  <div className="flex items-center text-red-600">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse mr-2"></div>
                    Recording...
                  </div>
                )}
              </div>
              
              <div className="flex space-x-3">
                {currentQuestionIndex < questions.length - 1 ? (
                  <button
                    onClick={nextQuestion}
                    className="btn-primary flex items-center"
                  >
                    Next Question
                  </button>
                ) : (
                  <button
                    onClick={completeInterview}
                    className="btn-primary flex items-center"
                  >
                    <CheckCircleIcon className="h-4 w-4 mr-2" />
                    Complete Interview
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {interviewStatus === 'completed' && (
          <div className="text-center py-8">
            <CheckCircleIcon className="h-16 w-16 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-secondary-900 mb-2">Interview Completed!</h3>
            <p className="text-secondary-600 mb-6">
              Thank you for completing the interview. Your responses are being analyzed by our AI system.
            </p>
            <div className="flex space-x-4 justify-center">
              <Link
                to="/interviews"
                className="btn-secondary"
              >
                Back to Interviews
              </Link>
              <button
                onClick={() => window.location.reload()}
                className="btn-primary"
              >
                View Results
              </button>
            </div>
          </div>
        )}
      </motion.div>

      {/* Tips Card */}
      {interviewStatus === 'in_progress' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card bg-blue-50 border-blue-200"
        >
          <h3 className="text-lg font-semibold text-blue-900 mb-2">💡 Interview Tips</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Be specific and provide concrete examples</li>
            <li>• Take your time to think before responding</li>
            <li>• Ask for clarification if needed</li>
            <li>• Be honest about your experience and skills</li>
          </ul>
        </motion.div>
      )}
    </div>
  );
};

export default InterviewConduct;
