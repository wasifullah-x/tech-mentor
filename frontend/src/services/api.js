import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // You can add auth tokens here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export const chatAPI = {
  /**
   * Send a chat message
   */
  sendMessage: async (message, sessionId = null, deviceInfo = null, conversationHistory = [], technicalLevel = 'beginner') => {
    try {
      const response = await apiClient.post('/chat', {
        message,
        session_id: sessionId,
        device_info: deviceInfo,
        conversation_history: conversationHistory,
        technical_level: technicalLevel
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Analyze a problem
   */
  analyzeProblem: async (problemDescription, deviceInfo = null) => {
    try {
      const response = await apiClient.post('/analyze', {
        problem_description: problemDescription,
        device_info: deviceInfo
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Search for solutions
   */
  searchSolutions: async (query, category = null, deviceType = null, limit = 10) => {
    try {
      const response = await apiClient.post('/solutions/search', {
        query,
        problem_category: category,
        device_type: deviceType,
        limit
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Submit feedback
   */
  submitFeedback: async (sessionId, rating, solved, comment = null) => {
    try {
      const response = await apiClient.post('/feedback', {
        session_id: sessionId,
        rating,
        solved,
        comment
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get session history
   */
  getSessionHistory: async (sessionId) => {
    try {
      const response = await apiClient.get(`/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Clear session
   */
  clearSession: async (sessionId) => {
    try {
      const response = await apiClient.delete(`/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export const healthAPI = {
  /**
   * Check API health
   */
  checkHealth: async () => {
    try {
      const response = await apiClient.get('/health', {
        baseURL: 'http://localhost:8000'
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default apiClient;
