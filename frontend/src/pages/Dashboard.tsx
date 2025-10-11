import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  PlusIcon, 
  UserGroupIcon, 
  BriefcaseIcon, 
  VideoCameraIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';

interface DashboardStats {
  totalJobs: number;
  totalCandidates: number;
  totalInterviews: number;
  completedInterviews: number;
  averageMatchScore: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalJobs: 0,
    totalCandidates: 0,
    totalInterviews: 0,
    completedInterviews: 0,
    averageMatchScore: 0
  });

  const [recentActivity, setRecentActivity] = useState<any[]>([]);

  useEffect(() => {
    // Fetch dashboard data
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Mock data for demo
      setStats({
        totalJobs: 12,
        totalCandidates: 45,
        totalInterviews: 8,
        completedInterviews: 5,
        averageMatchScore: 78.5
      });

      setRecentActivity([
        {
          id: 1,
          type: 'interview_completed',
          candidate: 'John Doe',
          job: 'Senior Developer',
          score: 85,
          timestamp: '2 hours ago'
        },
        {
          id: 2,
          type: 'resume_uploaded',
          candidate: 'Jane Smith',
          job: 'Product Manager',
          timestamp: '4 hours ago'
        },
        {
          id: 3,
          type: 'job_created',
          job: 'UX Designer',
          timestamp: '1 day ago'
        }
      ]);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const statCards = [
    {
      name: 'Active Jobs',
      value: stats.totalJobs,
      icon: BriefcaseIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      name: 'Total Candidates',
      value: stats.totalCandidates,
      icon: UserGroupIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      name: 'Interviews Scheduled',
      value: stats.totalInterviews,
      icon: VideoCameraIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      name: 'Avg Match Score',
      value: `${stats.averageMatchScore}%`,
      icon: ArrowTrendingUpIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Dashboard</h1>
          <p className="text-secondary-600 mt-2">
            Welcome to your AI-powered recruitment platform
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

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card"
          >
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">
                  {stat.name}
                </p>
                <p className="text-2xl font-bold text-secondary-900">
                  {stat.value}
                </p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">
            Recent Activity
          </h3>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-secondary-900">
                    {activity.type === 'interview_completed' && (
                      <>Interview completed for <strong>{activity.candidate}</strong> - {activity.job} (Score: {activity.score}%)</>
                    )}
                    {activity.type === 'resume_uploaded' && (
                      <>New resume uploaded by <strong>{activity.candidate}</strong> for {activity.job}</>
                    )}
                    {activity.type === 'job_created' && (
                      <>New job posted: <strong>{activity.job}</strong></>
                    )}
                  </p>
                  <p className="text-xs text-secondary-500">{activity.timestamp}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">
            Quick Actions
          </h3>
          <div className="space-y-3">
            <Link
              to="/jobs/create"
              className="flex items-center p-3 rounded-lg bg-primary-50 hover:bg-primary-100 transition-colors"
            >
              <BriefcaseIcon className="h-5 w-5 text-primary-600 mr-3" />
              <span className="text-primary-700 font-medium">Post New Job</span>
            </Link>
            <Link
              to="/candidates"
              className="flex items-center p-3 rounded-lg bg-secondary-50 hover:bg-secondary-100 transition-colors"
            >
              <UserGroupIcon className="h-5 w-5 text-secondary-600 mr-3" />
              <span className="text-secondary-700 font-medium">View Candidates</span>
            </Link>
            <Link
              to="/interviews"
              className="flex items-center p-3 rounded-lg bg-secondary-50 hover:bg-secondary-100 transition-colors"
            >
              <VideoCameraIcon className="h-5 w-5 text-secondary-600 mr-3" />
              <span className="text-secondary-700 font-medium">Schedule Interview</span>
            </Link>
          </div>
        </motion.div>
      </div>

      {/* Performance Chart Placeholder */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">
          Recruitment Performance
        </h3>
        <div className="h-64 bg-secondary-50 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <ChartBarIcon className="h-12 w-12 text-secondary-400 mx-auto mb-2" />
            <p className="text-secondary-600">Performance charts will be displayed here</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
