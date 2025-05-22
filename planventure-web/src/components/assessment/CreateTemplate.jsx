import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navigation from '../Navigation';
import Button from '../Button';
import Input from '../Input';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import { useAuth } from '../../context/auth-hooks';
import toast from 'react-hot-toast';

const CreateTemplate = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { handleError } = useApiErrorHandler();
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    percentage: 100,
    time_limit: '',
  });
  
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };
  
  const validate = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Template name is required';
    }
    
    if (formData.percentage < 10 || formData.percentage > 100) {
      newErrors.percentage = 'Percentage must be between 10 and 100';
    }
    
    if (formData.time_limit && (isNaN(formData.time_limit) || formData.time_limit <= 0)) {
      newErrors.time_limit = 'Time limit must be a positive number';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    setIsSubmitting(true);
    try {
      const templateData = {
        ...formData,
        creator_id: user.id,
        percentage: Number(formData.percentage),
        time_limit: formData.time_limit ? Number(formData.time_limit) : null
      };
      
      const response = await assessmentService.createTemplate(templateData);
      
      toast.success('Assessment template created successfully');
      navigate(`/assessments/templates/${response.id}/questions`);
    } catch (error) {
      handleError(error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      
      <div className="container py-4">
        <div className="row justify-content-center">
          <div className="col-lg-8">
            <div className="card shadow-sm">
              <div className="card-header bg-white py-3">
                <h5 className="mb-0">Create Assessment Template</h5>
              </div>
              
              <div className="card-body p-4">
                <form onSubmit={handleSubmit}>
                  <Input
                    label="Template Name"
                    name="name"
                    type="text"
                    value={formData.name}
                    onChange={handleChange}
                    error={errors.name}
                    placeholder="Enter a descriptive name for this template"
                    required
                  />
                  
                  <div className="mb-3">
                    <label htmlFor="description" className="form-label">Description</label>
                    <textarea
                      id="description"
                      name="description"
                      className="form-control"
                      rows="3"
                      value={formData.description}
                      onChange={handleChange}
                      placeholder="Enter a description for this assessment template"
                    ></textarea>
                  </div>
                  
                  <div className="row">
                    <div className="col-md-6">
                      <Input
                        label="Question Percentage"
                        name="percentage"
                        type="number"
                        min="10"
                        max="100"
                        value={formData.percentage}
                        onChange={handleChange}
                        error={errors.percentage}
                        info="Percentage of questions to include in assessments (10-100%)"
                      />
                    </div>
                    
                    <div className="col-md-6">
                      <Input
                        label="Time Limit (minutes)"
                        name="time_limit"
                        type="number"
                        min="1"
                        step="1"
                        value={formData.time_limit}
                        onChange={handleChange}
                        error={errors.time_limit}
                        info="Leave empty for no time limit"
                      />
                    </div>
                  </div>
                  
                  <div className="d-flex justify-content-between mt-4">
                    <Button
                      type="button"
                      variant="light"
                      onClick={() => navigate('/assessments')}
                    >
                      Cancel
                    </Button>
                    
                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={isSubmitting}
                    >
                      Create Template
                    </Button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateTemplate;
