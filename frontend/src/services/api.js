import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`Response from ${response.config.url}:`, response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Feed API functions
export const feedAPI = {
  // Get all feed entries with language support
  getFeedEntries: async (limit = 20, language = 'en') => {
    try {
      const response = await apiClient.get(`/feed_entries?limit=${limit}&language=${language}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching feed entries:', error);
      throw error;
    }
  },

  // Get feed entries count
  getFeedCount: async () => {
    try {
      const response = await apiClient.get('/feed_entries/count');
      return response.data;
    } catch (error) {
      console.error('Error fetching feed count:', error);
      throw error;
    }
  },

  // Get translations count
  getTranslationsCount: async () => {
    try {
      const response = await apiClient.get('/translations/count');
      return response.data;
    } catch (error) {
      console.error('Error fetching translations count:', error);
      throw error;
    }
  },

  // Clear all feed entries (for testing)
  clearFeedEntries: async () => {
    try {
      const response = await apiClient.delete('/feed_entries');
      return response.data;
    } catch (error) {
      console.error('Error clearing feed entries:', error);
      throw error;
    }
  },

  // Simulate webhook call (for development only)
  simulateWebhook: async (newsData) => {
    try {
      const response = await apiClient.post('/ai_news_webhook', newsData);
      return response.data;
    } catch (error) {
      console.error('Error simulating webhook:', error);
      throw error;
    }
  }
};

// Status API functions (existing)
export const statusAPI = {
  getStatus: async () => {
    try {
      const response = await apiClient.get('/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching status:', error);
      throw error;
    }
  },

  createStatusCheck: async (clientName) => {
    try {
      const response = await apiClient.post('/status', { client_name: clientName });
      return response.data;
    } catch (error) {
      console.error('Error creating status check:', error);
      throw error;
    }
  }
};

// Root API function (existing)
export const rootAPI = {
  getRoot: async () => {
    try {
      const response = await apiClient.get('/');
      return response.data;
    } catch (error) {
      console.error('Error fetching root:', error);
      throw error;
    }
  }
};

export default apiClient;