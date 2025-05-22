import { createAxiosInstance } from './axiosConfig';

const api = createAxiosInstance();

export const assessmentService = {  // Question Management - for ADMIN and TALENT_LEAD
  getQuestions: async (page = 1, perPage = 10, type = 'all', search = '') => {
    const response = await api.get('/api/questions', { 
      params: { page, per_page: perPage, type, search } 
    });
    return response.data;
  },
  
  createReadingSet: async (readingSetData) => {
    const response = await api.post('/api/reading-sets', readingSetData);
    return response.data;
  },
  
  createQuestion: async (questionData) => {
    const response = await api.post('/api/questions', questionData);
    return response.data;
  },
  
  getQuestionDetails: async (questionId) => {
    const response = await api.get(`/api/questions/${questionId}`);
    return response.data;
  },
  
  updateQuestion: async (questionId, questionData) => {
    const response = await api.put(`/api/questions/${questionId}`, questionData);
    return response.data;
  },
  
  // Template Management - for ADMIN and TALENT_LEAD
  createTemplate: async (templateData) => {
    const response = await api.post('/api/templates', templateData);
    return response.data;
  },
  
  getTemplates: async (page = 1, perPage = 10, search = '') => {
    const response = await api.get('/api/templates', { 
      params: { page, per_page: perPage, search } 
    });
    return response.data;
  },
  
  getTemplateDetails: async (templateId) => {
    const response = await api.get(`/api/templates/${templateId}`);
    return response.data;
  },
  
  getTemplateAnalytics: async (templateId) => {
    const response = await api.get(`/api/templates/${templateId}/analytics`);
    return response.data;
  },
    addQuestionsToTemplate: async (templateId, questionIds) => {
    const response = await api.post(`/api/templates/${templateId}/questions`, { question_ids: questionIds });
    return response.data;
  },
  
  cloneTemplate: async (templateId, newName) => {
    const response = await api.post(`/api/templates/${templateId}/clone`, { name: newName });
    return response.data;
  },
  
  // Assessment Management - for ADMIN and TALENT_LEAD
  getAssessments: async (params = {}) => {
    const response = await api.get('/api/assessments', { params });
    return response.data;
  },
  
  createAssessment: async (assessmentData) => {
    const response = await api.post('/api/assessments', assessmentData);
    return response.data;
  },
  
  getAssessmentDetails: async (assessmentId) => {
    const response = await api.get(`/api/assessments/${assessmentId}`);
    return response.data;
  },
  
  getAssessmentReport: async (assessmentId) => {
    const response = await api.get(`/api/assessments/${assessmentId}/report`);
    return response.data;
  },
  
  // Assessment Taking - for CANDIDATE
  startAssessment: async (assessmentId) => {
    const response = await api.post(`/api/assessments/${assessmentId}/start`);
    return response.data;
  },
  
  getCurrentQuestion: async (assessmentId) => {
    const response = await api.get(`/api/assessments/${assessmentId}/current-question`);
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
    
    const response = await api.post(`/api/assessments/${assessmentId}/submit-answer`, data);
    return response.data;
  },
  
  completeAssessment: async (assessmentId) => {
    const response = await api.post(`/api/assessments/${assessmentId}/complete`);
    return response.data;
  },
  
  // Assessment Access
  accessAssessment: async (assessmentId, email, token) => {
    const response = await api.get(`/api/assessments/${assessmentId}/access`, {
      headers: {
        'X-User-Email': email,
        'X-Access-Token': token
      }
    });
    return response.data;
  }
};
