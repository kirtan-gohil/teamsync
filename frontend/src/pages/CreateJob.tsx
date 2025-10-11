import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

const CreateJob: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    location: '',
    description: '',
    requirements: '',
    skills_required: '',
    experience_required: 0,
    salary_min: '',
    salary_max: ''
  });
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSkillsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const skills = e.target.value.split(',').map(skill => skill.trim()).filter(skill => skill);
    setFormData(prev => ({
      ...prev,
      skills_required: skills.join(', ')
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success('Job posted successfully!');
      navigate('/jobs');
    } catch (error) {
      toast.error('Failed to post job. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Post New Job</h1>
          <p className="text-secondary-600 mt-2">
            Create a new job posting and let AI find the best candidates
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Basic Information</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="label">Job Title *</label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="e.g., Senior Software Engineer"
                  required
                />
              </div>
              
              <div>
                <label className="label">Company *</label>
                <input
                  type="text"
                  name="company"
                  value={formData.company}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="e.g., Tech Corp"
                  required
                />
              </div>
              
              <div>
                <label className="label">Location *</label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="e.g., San Francisco, CA or Remote"
                  required
                />
              </div>
              
              <div>
                <label className="label">Experience Required (years)</label>
                <select
                  name="experience_required"
                  value={formData.experience_required}
                  onChange={handleInputChange}
                  className="input-field"
                >
                  <option value={0}>Entry Level (0-1 years)</option>
                  <option value={2}>Junior (2-3 years)</option>
                  <option value={4}>Mid Level (4-6 years)</option>
                  <option value={7}>Senior (7-10 years)</option>
                  <option value={10}>Lead (10+ years)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Job Description</h3>
            
            <div>
              <label className="label">Description *</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                className="input-field"
                rows={6}
                placeholder="Describe the role, responsibilities, and what makes this position exciting..."
                required
              />
            </div>
            
            <div className="mt-6">
              <label className="label">Requirements</label>
              <textarea
                name="requirements"
                value={formData.requirements}
                onChange={handleInputChange}
                className="input-field"
                rows={4}
                placeholder="List the key requirements for this position..."
              />
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Skills & Compensation</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="label">Required Skills</label>
                <input
                  type="text"
                  name="skills_required"
                  value={formData.skills_required}
                  onChange={handleSkillsChange}
                  className="input-field"
                  placeholder="e.g., Python, React, AWS, Machine Learning"
                />
                <p className="text-sm text-secondary-500 mt-1">
                  Separate skills with commas
                </p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Min Salary</label>
                  <input
                    type="number"
                    name="salary_min"
                    value={formData.salary_min}
                    onChange={handleInputChange}
                    className="input-field"
                    placeholder="e.g., 80000"
                  />
                </div>
                
                <div>
                  <label className="label">Max Salary</label>
                  <input
                    type="number"
                    name="salary_max"
                    value={formData.salary_max}
                    onChange={handleInputChange}
                    className="input-field"
                    placeholder="e.g., 120000"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/jobs')}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex items-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Posting Job...
                </>
              ) : (
                'Post Job'
              )}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

export default CreateJob;
