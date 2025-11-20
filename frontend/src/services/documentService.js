import api from './api';
import { DOCUMENT_ENDPOINTS } from '@/constants/apiEndpoints';

/**
 * Document Service
 * Handles all document-related API calls
 */
const documentService = {
  /**
   * Get all documents
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getDocuments: (params = {}) => {
    return api.get(DOCUMENT_ENDPOINTS.LIST, { params });
  },

  /**
   * Get document by ID
   * @param {string} id - Document ID
   * @returns {Promise}
   */
  getDocumentById: (id) => {
    return api.get(DOCUMENT_ENDPOINTS.DETAIL(id));
  },

  /**
   * Upload document
   * @param {File} file - File to upload
   * @param {Function} onProgress - Progress callback
   * @returns {Promise}
   */
  uploadDocument: (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    return api.upload(DOCUMENT_ENDPOINTS.UPLOAD, formData, {
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });
  },

  /**
   * Delete document
   * @param {string} id - Document ID
   * @returns {Promise}
   */
  deleteDocument: (id) => {
    return api.delete(DOCUMENT_ENDPOINTS.DETAIL(id));
  },

  /**
   * Extract data from document
   * @param {string} id - Document ID
   * @param {Object} options - Extraction options
   * @returns {Promise}
   */
  extractData: (id, options = {}) => {
    return api.post(DOCUMENT_ENDPOINTS.EXTRACT(id), options);
  },

  /**
   * Search documents
   * @param {string} query - Search query
   * @param {Object} filters - Additional filters
   * @returns {Promise}
   */
  searchDocuments: (query, filters = {}) => {
    return api.post(DOCUMENT_ENDPOINTS.SEARCH, { query, ...filters });
  },

  /**
   * Download document
   * @param {string} id - Document ID
   * @returns {Promise}
   */
  downloadDocument: (id) => {
    return api.download(DOCUMENT_ENDPOINTS.DOWNLOAD(id));
  },

  /**
   * Get document pages
   * @param {string} id - Document ID
   * @returns {Promise}
   */
  getDocumentPages: (id) => {
    return api.get(DOCUMENT_ENDPOINTS.PAGES(id));
  },

  /**
   * Get document preview
   * @param {string} id - Document ID
   * @param {number} page - Page number
   * @returns {Promise}
   */
  getDocumentPreview: (id, page = 1) => {
    return api.get(DOCUMENT_ENDPOINTS.PREVIEW(id), { params: { page } });
  },

  /**
   * Get document embeddings
   * @param {string} id - Document ID
   * @returns {Promise}
   */
  getDocumentEmbeddings: (id) => {
    return api.get(DOCUMENT_ENDPOINTS.EMBEDDINGS(id));
  },

  /**
   * Process document with AI
   * @param {string} id - Document ID
   * @param {Object} options - Processing options
   * @returns {Promise}
   */
  processDocument: (id, options = {}) => {
    return api.post(DOCUMENT_ENDPOINTS.PROCESS(id), options);
  },

  /**
   * Get document metadata
   * @param {string} id - Document ID
   * @returns {Promise}
   */
  getDocumentMetadata: (id) => {
    return api.get(DOCUMENT_ENDPOINTS.METADATA(id));
  },

  /**
   * Update document metadata
   * @param {string} id - Document ID
   * @param {Object} metadata - Metadata to update
   * @returns {Promise}
   */
  updateDocumentMetadata: (id, metadata) => {
    return api.patch(DOCUMENT_ENDPOINTS.METADATA(id), metadata);
  },
};

export default documentService;
