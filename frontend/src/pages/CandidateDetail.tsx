import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeftIcon,
  VideoCameraIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  BriefcaseIcon,
  AcademicCapIcon,
  StarIcon
} from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';

interface Candidate {
  id: number;
  name: string;
  email: string;
  phone: string;
  skills: string[];
  experience_years: number;
  education: string;
  location: string;
  score: number;
  resume_url: string;
  created_at: string;
  work_experience: any[];
}

const CandidateDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchCandidate(parseInt(id));
    }
  }, [id]);

  const fetchCandidate = async (candidateId: number) => {
    try {
      // Mock data for demo
      const mockCandidate: Candidate = {
        id: candidateId,
        name: 'John Doe',
        email: 'john.doe@email.com',
        phone: '+1 (555) 123-4567',
        skills: ['Python', 'React', 'AWS', 'Machine Learning', 'Docker', 'Kubernetes'],
        experience_years: 5,
        education: 'Bachelor of Computer Science, Stanford University',
        location: 'San Francisco, CA',
        score: 85,
        resume_url: '/resumes/john_doe.pdf',
        created_at: '2024-01-15',
        work_experience: [
          {
            company: 'Tech Corp',
            position: 'Senior Software Engineer',
            period: '2021 - Present',
            description: 'Led development of microservices architecture and implemented CI/CD pipelines.'
          },
          {
            company: 'StartupXYZ',
            position: 'Software Engineer',
            period: '2019 - 2021',
            description: 'Developed full-stack applications using React and Node.js.'
          }
        ]
      };
      
      setCandidate(mockCandidate);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching candidate:', error);
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-secondary-900">Candidate not found</h3>
        <p className="text-secondary-600 mt-2">The candidate you're looking for doesn't exist.</p>
        <Link to="/candidates" className="btn-primary mt-4">
          Back to Candidates
        </Link>
      </div>
    );
  }

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
            to="/candidates"
            className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-lg transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-secondary-900">{candidate.name}</h1>
            <p className="text-secondary-600 mt-1">Candidate Profile</p>
          </div>
        </div>
        <div className="flex space-x-3">
          <button className="btn-secondary flex items-center">
            <EnvelopeIcon className="h-4 w-4 mr-2" />
            Contact
          </button>
          <button className="btn-primary flex items-center">
            <VideoCameraIcon className="h-4 w-4 mr-2" />
            Schedule Interview
          </button>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Contact Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-3">
                <EnvelopeIcon className="h-5 w-5 text-secondary-400" />
                <span className="text-secondary-700">{candidate.email}</span>
              </div>
              <div className="flex items-center space-x-3">
                <PhoneIcon className="h-5 w-5 text-secondary-400" />
                <span className="text-secondary-700">{candidate.phone}</span>
              </div>
              <div className="flex items-center space-x-3">
                <MapPinIcon className="h-5 w-5 text-secondary-400" />
                <span className="text-secondary-700">{candidate.location}</span>
              </div>
              <div className="flex items-center space-x-3">
                <BriefcaseIcon className="h-5 w-5 text-secondary-400" />
                <span className="text-secondary-700">{candidate.experience_years} years experience</span>
              </div>
            </div>
          </motion.div>

          {/* Skills */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card"
          >
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Skills</h3>
            <div className="flex flex-wrap gap-2">
              {candidate.skills.map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-primary-100 text-primary-700 text-sm rounded-full"
                >
                  {skill}
                </span>
              ))}
            </div>
          </motion.div>

          {/* Work Experience */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card"
          >
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Work Experience</h3>
            <div className="space-y-4">
              {candidate.work_experience.map((exp, index) => (
                <div key={index} className="border-l-2 border-primary-200 pl-4">
                  <h4 className="font-medium text-secondary-900">{exp.position}</h4>
                  <p className="text-primary-600 font-medium">{exp.company}</p>
                  <p className="text-sm text-secondary-600">{exp.period}</p>
                  <p className="text-secondary-700 mt-2">{exp.description}</p>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Education */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card"
          >
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Education</h3>
            <div className="flex items-start space-x-3">
              <AcademicCapIcon className="h-5 w-5 text-secondary-400 mt-1" />
              <div>
                <p className="text-secondary-700">{candidate.education}</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Score Card */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Match Score</h3>
            <div className="text-center">
              <div className={`inline-flex items-center px-4 py-2 rounded-full text-2xl font-bold ${getScoreColor(candidate.score)}`}>
                {candidate.score}%
              </div>
              <p className="text-sm text-secondary-600 mt-2">
                Overall compatibility score
              </p>
            </div>
          </motion.div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="card"
          >
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full btn-primary flex items-center justify-center">
                <VideoCameraIcon className="h-4 w-4 mr-2" />
                Schedule Interview
              </button>
              <button className="w-full btn-secondary flex items-center justify-center">
                <EnvelopeIcon className="h-4 w-4 mr-2" />
                Send Message
              </button>
              <button className="w-full btn-secondary flex items-center justify-center">
                <StarIcon className="h-4 w-4 mr-2" />
                Add to Favorites
              </button>
            </div>
          </motion.div>

          {/* Resume */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="card"
          >
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Resume</h3>
            <div className="text-center">
              <div className="w-16 h-16 bg-secondary-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="h-8 w-8 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p className="text-sm text-secondary-600 mb-3">Resume.pdf</p>
              <button className="btn-primary text-sm">
                Download Resume
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default CandidateDetail;
