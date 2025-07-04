// API endpoints configuration
export const API_ENDPOINTS = {
  // Search endpoints
  SEARCH: '/api/search',
  SEARCH_WITH_PROGRESS: '/api/search_with_progress',
  
  // RAG QA endpoints
  RAG_QA: '/api/rag_qa',
  RAG_QA_WITH_PROGRESS: '/api/rag_qa_with_progress',
  
  // Translation endpoint
  TRANSLATE: '/api/translate',
  
  // Utility endpoints
  STATS: '/api/stats',
  HEALTH: '/api/health'
};

// Development vs Production API base URL
const isDevelopment = process.env.NODE_ENV === 'development';
const API_BASE_URL = isDevelopment 
  ? 'http://localhost:5000'  // Local development
  : 'https://hirag.up.railway.app'; // Production - your actual Railway URL

// Export the full API URLs
export const getApiUrl = (endpoint) => {
  return `${API_BASE_URL}${endpoint}`;
};

// Default configuration
export const DEFAULT_CONFIG = {
  SEARCH_TOP_K: 10,
  RAG_TOP_K: 20,
  MAX_QUERY_LENGTH: 1000,
  REQUEST_TIMEOUT: 30000, // 30 seconds
}; 