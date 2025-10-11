import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  PlusIcon, 
  EyeIcon, 
  PencilIcon,
  TrashIcon,
  UserGroupIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';

interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  status: string;
  created_at: string;
  candidate_count: number;
  match_score: number;
}

const Jobs: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      // Mock data for demo
      const mockJobs: Job[] = [
        {
          id: 1,
          title: 'Senior Software Engineer',
          company: 'Tech Corp',
          location: 'San Francisco, CA',
          status: 'active',
          created_at: '2024-01-15',
          candidate_count: 12,
          match_score: 85
        },
        {
          id: 2,
          title: 'Product Manager',
          company: 'StartupXYZ',
          location: 'New York, NY',
          status: 'active',
          created_at: '2024-01-14',
          candidate_count: 8,
          match_score: 78
        },
        {
          id: 3,
          title: 'UX Designer',
          company: 'Design Studio',
          location: 'Remote',
          status: 'closed',
          created_at: '2024-01-10',
          candidate_count: 15,
          match_score: 92
        }
      ];
      
      setJobs(mockJobs);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching jobs:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'closed':
        return 'bg-red-100 text-red-800';
      case 'filled':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-secondary-100 text-secondary-800';
    }
  };

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
          <h1 className="text-3xl font-bold text-secondary-900">Job Postings</h1>
          <p className="text-secondary-600 mt-2">
            Manage your job postings and track candidate matches
          </p>
        </div>
        <Link
          to="/jobs/create"
          className="btn-primary flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Post New Job
        </Link>
      </div>

      {/* Jobs List */}
      <div className="space-y-4">
        {jobs.map((job, index) => (
          <motion.div
            key={job.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <h3 className="text-lg font-semibold text-secondary-900">
                    {job.title}
                  </h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(job.status)}`}>
                    {job.status}
                  </span>
                </div>
                <p className="text-secondary-600 mt-1">{job.company} • {job.location}</p>
                
                <div className="flex items-center space-x-6 mt-3">
                  <div className="flex items-center text-sm text-secondary-600">
                    <UserGroupIcon className="h-4 w-4 mr-1" />
                    {job.candidate_count} candidates
                  </div>
                  <div className="flex items-center text-sm text-secondary-600">
                    <CalendarIcon className="h-4 w-4 mr-1" />
                    Posted {new Date(job.created_at).toLocaleDateString()}
                  </div>
                  <div className="text-sm">
                    <span className="text-secondary-600">Avg Match: </span>
                    <span className="font-medium text-primary-600">{job.match_score}%</span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Link
                  to={`/jobs/${job.id}/candidates`}
                  className="p-2 text-secondary-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                  title="View Candidates"
                >
                  <EyeIcon className="h-5 w-5" />
                </Link>
                <button
                  className="p-2 text-secondary-600 hover:text-secondary-800 hover:bg-secondary-100 rounded-lg transition-colors"
                  title="Edit Job"
                >
                  <PencilIcon className="h-5 w-5" />
                </button>
                <button
                  className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
                  title="Delete Job"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {jobs.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <div className="mx-auto h-24 w-24 text-secondary-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2V6" />
            </svg>
          </div>
          <h3 className="mt-4 text-lg font-medium text-secondary-900">No jobs posted yet</h3>
          <p className="mt-2 text-secondary-600">Get started by posting your first job opening.</p>
          <div className="mt-6">
            <Link
              to="/jobs/create"
              className="btn-primary"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Post Your First Job
            </Link>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Jobs;


