import { createAxiosInstance } from './axiosConfig';

const api = createAxiosInstance();

export const assessmentService = {  
  // Question Management - for ADMIN and TALENT_LEAD
  getQuestions: async (page = 1, perPage = 10, type = 'all', search = '', specialization = '', difficulty = '') => {
    const params = { page, per_page: perPage, search, simple: 'false' };
    
    // Only add question_type filter if not 'all'
    if (type !== 'all') {
      // Map the frontend question types to backend
      const typeMapping = {
        'aptitude': 'multiple_choice',
        'reading_comprehension': 'reading_comprehension',
        'typing': 'typing'
      };
      
      params.question_type = typeMapping[type] || type;
    }
    
    // Add specialization filter if provided
    if (specialization) {
      params.specialization = specialization;
    }
    
    // Add difficulty filter if provided
    if (difficulty) {
      params.difficulty = difficulty;
    }
    
    const response = await api.get('/questions', { params });
    return response.data;
  },
  
  createReadingSet: async (readingSetData) => {
    const response = await api.post('/reading-sets', readingSetData);
    return response.data;
  },
  
  createQuestion: async (questionData) => {
    // Map frontend question type to backend format if using old format
    const typeMapping = {
      'aptitude': 'multiple_choice',
      'reading_comprehension': 'reading_comprehension',
      'typing': 'typing'
    };
    
    const mappedData = { ...questionData };
    
    // Ensure question_type is set properly (for backward compatibility)
    if (mappedData.question_type) {
      mappedData.question_type = typeMapping[mappedData.question_type] || mappedData.question_type;
    }
    
    // Make sure specialization is set properly as subject area
    if (!mappedData.specialization) {
      mappedData.specialization = 'aptitude'; // Default specialization
    }
    
    const response = await api.post('/questions', mappedData);
    return response.data;
  },
  
  getQuestionDetails: async (questionId) => {
    const response = await api.get(`/questions/${questionId}`);
    
    // No need to map backend to frontend question type since we now use the same values
    // Just return the data directly
    return response.data;
  },
    
  updateQuestion: async (questionId, questionData) => {
    // Map frontend question type to backend format
    const typeMapping = {
      'aptitude': 'multiple_choice',
      'reading_comprehension': 'reading_comprehension',
      'typing': 'typing'
    };
    
    const mappedData = { ...questionData };
    if (mappedData.question_type) {
      mappedData.question_type = typeMapping[mappedData.question_type] || mappedData.question_type;
    }
    
    console.log(`Sending PUT request to /questions/${questionId}`, mappedData);
    const response = await api.put(`/questions/${questionId}`, mappedData);
    console.log('Response from server:', response.data);
    return response.data;
  },
  
  // Template Management - for ADMIN and TALENT_LEAD
  createTemplate: async (templateData) => {
    const response = await api.post('/templates', templateData);
    return response.data;
  },
  
  getTemplates: async (page = 1, perPage = 10, search = '') => {
    const response = await api.get('/templates', { 
      params: { page, per_page: perPage, search } 
    });
    return response.data;
  },
  
  getTemplateDetails: async (templateId) => {
    const response = await api.get(`/templates/${templateId}`);
    return response.data;
  },
  
  getTemplateAnalytics: async (templateId) => {
    const response = await api.get(`/templates/${templateId}/analytics`);
    return response.data;
  },
  
  addQuestionsToTemplate: async (templateId, questionIds) => {
    const response = await api.post(`/templates/${templateId}/questions`, { question_ids: questionIds });
    return response.data;
  },
  
  removeQuestionFromTemplate: async (templateId, questionId) => {
    const response = await api.delete(`/templates/${templateId}/questions/${questionId}`);
    return response.data;
  },
  
  cloneTemplate: async (templateId, newName) => {
    const response = await api.post(`/templates/${templateId}/clone`, { name: newName });
    return response.data;
  },
  
  // Assessment Management - for ADMIN and TALENT_LEAD
  getAssessments: async (params = {}) => {
    const response = await api.get('/assessments', { params });
    return response.data;
  },
  
  createAssessment: async (assessmentData) => {
    const response = await api.post('/assessments', assessmentData);
    return response.data;
  },
  
  getAssessmentDetails: async (assessmentId) => {
    const response = await api.get(`/assessments/${assessmentId}`);
    return response.data;
  },
  
  getAssessmentReport: async (assessmentId) => {
    const response = await api.get(`/assessments/${assessmentId}/report`);
    return response.data;
  },
  
  // Assessment Taking - for CANDIDATE
  startAssessment: async (assessmentId) => {
    const response = await api.post(`/assessments/${assessmentId}/start`);
    return response.data;
  },
  
  getCurrentQuestion: async (assessmentId) => {
    const response = await api.get(`/assessments/${assessmentId}/current-question`);
    return response.data;
  },
  
  submitAnswer: async (assessmentId, questionId, answer, typingMetrics = null) => {
    const data = {
      question_id: questionId,
      answer: answer
    };
    
    // Add typing metrics if provided
    if (typingMetrics) {
      data.typing_metrics = typingMetrics;
    }
    
    const response = await api.post(`/assessments/${assessmentId}/submit-answer`, data);
    return response.data;
  },
  
  completeAssessment: async (assessmentId) => {
    const response = await api.post(`/assessments/${assessmentId}/complete`);
    return response.data;
  },
  
  // Assessment Access
  accessAssessment: async (assessmentId, email, token) => {
    const response = await api.get(`/assessments/${assessmentId}/access`, {
      headers: {
        'X-User-Email': email,
        'X-Access-Token': token
      }
    });
    return response.data;
  }
};
