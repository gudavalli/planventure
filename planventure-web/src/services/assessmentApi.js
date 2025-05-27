import { createAxiosInstance } from './axiosConfig';

const api = createAxiosInstance();

export const assessmentService = {  // Question Management - for ADMIN and TALENT_LEAD
  getQuestions: async (page = 1, perPage = 10, type = 'all', search = '') => {
    const params = { page, per_page: perPage, search, simple: 'false' };
    
    // Only add type filter if not 'all'
    if (type !== 'all') {
      params.type = type;
    }
    
    const response = await api.get('/questions', { params });
    return response.data;
  },
  
  createReadingSet: async (readingSetData) => {
    const response = await api.post('/reading-sets', readingSetData);
    return response.data;
  },
  
  createQuestion: async (questionData) => {
    const response = await api.post('/questions', questionData);
    return response.data;
  },
  
  getQuestionDetails: async (questionId) => {
    const response = await api.get(`/questions/${questionId}`);
    return response.data;
  },
    updateQuestion: async (questionId, questionData) => {
    console.log(`Sending PUT request to /questions/${questionId}`, questionData);
    const response = await api.put(`/questions/${questionId}`, questionData);
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
