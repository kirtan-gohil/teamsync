import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  VideoCameraIcon,
  PlayIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  UserIcon,
  BriefcaseIcon
} from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';

interface Interview {
  id: number;
  candidate_name: string;
  job_title: string;
  status: string;
  scheduled_at: string;
  score: number;
  duration: number;
}

const Interviews: React.FC = () => {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchInterviews();
  }, []);

  const fetchInterviews = async () => {
    try {
      // Mock data for demo
      const mockInterviews: Interview[] = [
        {
          id: 1,
          candidate_name: 'John Doe',
          job_title: 'Senior Software Engineer',
          status: 'completed',
          scheduled_at: '2024-01-15T10:00:00Z',
          score: 85,
          duration: 45
        },
        {
          id: 2,
          candidate_name: 'Jane Smith',
          job_title: 'Product Manager',
          status: 'scheduled',
          scheduled_at: '2024-01-16T14:00:00Z',
          score: 0,
          duration: 0
        },
        {
          id: 3,
          candidate_name: 'Mike Johnson',
          job_title: 'UX Designer',
          status: 'in_progress',
          scheduled_at: '2024-01-15T16:00:00Z',
          score: 0,
          duration: 0
        }
      ];
      
      setInterviews(mockInterviews);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching interviews:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'scheduled':
        return 'text-blue-600 bg-blue-100';
      case 'in_progress':
        return 'text-yellow-600 bg-yellow-100';
      case 'cancelled':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-secondary-600 bg-secondary-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5" />;
      case 'scheduled':
        return <ClockIcon className="h-5 w-5" />;
      case 'in_progress':
        return <PlayIcon className="h-5 w-5" />;
      case 'cancelled':
        return <XCircleIcon className="h-5 w-5" />;
      default:
        return <ClockIcon className="h-5 w-5" />;
    }
  };

  const filteredInterviews = interviews.filter(interview => {
    if (filter === 'all') return true;
    return interview.status === filter;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Interviews</h1>
          <p className="text-secondary-600 mt-2">
            Manage and conduct AI-powered interviews
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex space-x-4">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'all' 
              ? 'bg-primary-100 text-primary-700' 
              : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
          }`}
        >
          All ({interviews.length})
        </button>
        <button
          onClick={() => setFilter('scheduled')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'scheduled' 
              ? 'bg-primary-100 text-primary-700' 
              : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
          }`}
        >
          Scheduled ({interviews.filter(i => i.status === 'scheduled').length})
        </button>
        <button
          onClick={() => setFilter('in_progress')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'in_progress' 
              ? 'bg-primary-100 text-primary-700' 
              : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
          }`}
        >
          In Progress ({interviews.filter(i => i.status === 'in_progress').length})
        </button>
        <button
          onClick={() => setFilter('completed')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'completed' 
              ? 'bg-primary-100 text-primary-700' 
              : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
          }`}
        >
          Completed ({interviews.filter(i => i.status === 'completed').length})
        </button>
      </div>

      {/* Interviews List */}
      <div className="space-y-4">
        {filteredInterviews.map((interview, index) => (
          <motion.div
            key={interview.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <VideoCameraIcon className="h-6 w-6 text-primary-600" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-semibold text-secondary-900">
                      {interview.candidate_name}
                    </h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full flex items-center space-x-1 ${getStatusColor(interview.status)}`}>
                      {getStatusIcon(interview.status)}
                      <span className="capitalize">{interview.status.replace('_', ' ')}</span>
                    </span>
                  </div>
                  <p className="text-secondary-600 mt-1">{interview.job_title}</p>
                  
                  <div className="flex items-center space-x-6 mt-2">
                    <div className="flex items-center text-sm text-secondary-600">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      {new Date(interview.scheduled_at).toLocaleDateString()} at {new Date(interview.scheduled_at).toLocaleTimeString()}
                    </div>
                    {interview.status === 'completed' && (
                      <div className="text-sm">
                        <span className="text-secondary-600">Score: </span>
                        <span className="font-medium text-primary-600">{interview.score}%</span>
                      </div>
                    )}
                    {interview.duration > 0 && (
                      <div className="text-sm text-secondary-600">
                        Duration: {interview.duration} min
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {interview.status === 'scheduled' && (
                  <Link
                    to={`/interviews/${interview.id}/conduct`}
                    className="btn-primary flex items-center"
                  >
                    <PlayIcon className="h-4 w-4 mr-2" />
                    Start Interview
                  </Link>
                )}
                {interview.status === 'in_progress' && (
                  <Link
                    to={`/interviews/${interview.id}/conduct`}
                    className="btn-primary flex items-center"
                  >
                    <PlayIcon className="h-4 w-4 mr-2" />
                    Continue
                  </Link>
                )}
                {interview.status === 'completed' && (
                  <Link
                    to={`/interviews/${interview.id}/results`}
                    className="btn-secondary flex items-center"
                  >
                    View Results
                  </Link>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {filteredInterviews.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <div className="mx-auto h-24 w-24 text-secondary-400">
            <VideoCameraIcon className="h-24 w-24" />
          </div>
          <h3 className="mt-4 text-lg font-medium text-secondary-900">No interviews found</h3>
          <p className="mt-2 text-secondary-600">
            {filter === 'all' 
              ? 'No interviews have been scheduled yet.' 
              : `No interviews match the ${filter} filter.`
            }
          </p>
          <div className="mt-6">
            <Link
              to="/candidates"
              className="btn-primary"
            >
              <UserIcon className="h-5 w-5 mr-2" />
              Browse Candidates
            </Link>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Interviews;
