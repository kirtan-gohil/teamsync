import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  EyeIcon, 
  VideoCameraIcon,
  UserIcon,
  StarIcon,
  MapPinIcon,
  BriefcaseIcon
} from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';

interface Candidate {
  id: number;
  name: string;
  email: string;
  skills: string[];
  experience_years: number;
  location: string;
  score: number;
  resume_url: string;
  created_at: string;
}

const Candidates: React.FC = () => {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      // Mock data for demo
      const mockCandidates: Candidate[] = [
        {
          id: 1,
          name: 'John Doe',
          email: 'john.doe@email.com',
          skills: ['Python', 'React', 'AWS', 'Machine Learning'],
          experience_years: 5,
          location: 'San Francisco, CA',
          score: 85,
          resume_url: '/resumes/john_doe.pdf',
          created_at: '2024-01-15'
        },
        {
          id: 2,
          name: 'Jane Smith',
          email: 'jane.smith@email.com',
          skills: ['JavaScript', 'Node.js', 'MongoDB', 'Docker'],
          experience_years: 3,
          location: 'New York, NY',
          score: 78,
          resume_url: '/resumes/jane_smith.pdf',
          created_at: '2024-01-14'
        },
        {
          id: 3,
          name: 'Mike Johnson',
          email: 'mike.johnson@email.com',
          skills: ['Java', 'Spring Boot', 'PostgreSQL', 'Kubernetes'],
          experience_years: 7,
          location: 'Seattle, WA',
          score: 92,
          resume_url: '/resumes/mike_johnson.pdf',
          created_at: '2024-01-13'
        }
      ];
      
      setCandidates(mockCandidates);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching candidates:', error);
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const filteredCandidates = candidates.filter(candidate => {
    if (filter === 'high') return candidate.score >= 80;
    if (filter === 'medium') return candidate.score >= 60 && candidate.score < 80;
    if (filter === 'low') return candidate.score < 60;
    return true;
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
          <h1 className="text-3xl font-bold text-secondary-900">Candidates</h1>
          <p className="text-secondary-600 mt-2">
            Browse and manage candidate profiles
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
          All ({candidates.length})
        </button>
        <button
          onClick={() => setFilter('high')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'high' 
              ? 'bg-primary-100 text-primary-700' 
              : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
          }`}
        >
          High Score ({candidates.filter(c => c.score >= 80).length})
        </button>
        <button
          onClick={() => setFilter('medium')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'medium' 
              ? 'bg-primary-100 text-primary-700' 
              : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
          }`}
        >
          Medium Score ({candidates.filter(c => c.score >= 60 && c.score < 80).length})
        </button>
        <button
          onClick={() => setFilter('low')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'low' 
              ? 'bg-primary-100 text-primary-700' 
              : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
          }`}
        >
          Low Score ({candidates.filter(c => c.score < 60).length})
        </button>
      </div>

      {/* Candidates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCandidates.map((candidate, index) => (
          <motion.div
            key={candidate.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <UserIcon className="h-6 w-6 text-primary-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-secondary-900">{candidate.name}</h3>
                  <p className="text-sm text-secondary-600">{candidate.email}</p>
                </div>
              </div>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${getScoreColor(candidate.score)}`}>
                {candidate.score}%
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center text-sm text-secondary-600">
                <MapPinIcon className="h-4 w-4 mr-2" />
                {candidate.location}
              </div>
              <div className="flex items-center text-sm text-secondary-600">
                <BriefcaseIcon className="h-4 w-4 mr-2" />
                {candidate.experience_years} years experience
              </div>
            </div>

            <div className="mt-4">
              <h4 className="text-sm font-medium text-secondary-700 mb-2">Skills</h4>
              <div className="flex flex-wrap gap-1">
                {candidate.skills.slice(0, 4).map((skill, skillIndex) => (
                  <span
                    key={skillIndex}
                    className="px-2 py-1 bg-secondary-100 text-secondary-700 text-xs rounded-md"
                  >
                    {skill}
                  </span>
                ))}
                {candidate.skills.length > 4 && (
                  <span className="px-2 py-1 bg-secondary-100 text-secondary-700 text-xs rounded-md">
                    +{candidate.skills.length - 4} more
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between mt-6">
              <span className="text-xs text-secondary-500">
                Added {new Date(candidate.created_at).toLocaleDateString()}
              </span>
              <div className="flex space-x-2">
                <Link
                  to={`/candidates/${candidate.id}`}
                  className="p-2 text-secondary-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                  title="View Profile"
                >
                  <EyeIcon className="h-4 w-4" />
                </Link>
                <button
                  className="p-2 text-secondary-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                  title="Schedule Interview"
                >
                  <VideoCameraIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {filteredCandidates.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <div className="mx-auto h-24 w-24 text-secondary-400">
            <UserIcon className="h-24 w-24" />
          </div>
          <h3 className="mt-4 text-lg font-medium text-secondary-900">No candidates found</h3>
          <p className="mt-2 text-secondary-600">
            {filter === 'all' 
              ? 'No candidates have been added yet.' 
              : `No candidates match the ${filter} score filter.`
            }
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default Candidates;
