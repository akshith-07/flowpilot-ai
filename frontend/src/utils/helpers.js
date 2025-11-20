/**
 * Helper Utilities
 * Miscellaneous helper functions
 */

import { clsx } from 'clsx';

/**
 * Combine class names
 * @param {...*} inputs - Class names to combine
 * @returns {string} Combined class names
 */
export const cn = (...inputs) => {
  return clsx(inputs);
};

/**
 * Generate a unique ID
 * @param {string} prefix - Optional prefix for the ID
 * @returns {string} Unique ID
 */
export const generateId = (prefix = 'id') => {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 */
export const debounce = (func, delay = 300) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

/**
 * Throttle function
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
export const throttle = (func, limit = 300) => {
  let inThrottle;
  return (...args) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Deep clone an object
 * @param {*} obj - Object to clone
 * @returns {*} Cloned object
 */
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  try {
    return JSON.parse(JSON.stringify(obj));
  } catch (error) {
    console.error('Error cloning object:', error);
    return obj;
  }
};

/**
 * Check if object is empty
 * @param {object} obj - Object to check
 * @returns {boolean} Whether object is empty
 */
export const isEmpty = (obj) => {
  if (obj === null || obj === undefined) return true;
  if (typeof obj === 'string') return obj.trim().length === 0;
  if (Array.isArray(obj)) return obj.length === 0;
  if (typeof obj === 'object') return Object.keys(obj).length === 0;
  return false;
};

/**
 * Get nested property from object
 * @param {object} obj - Object to search
 * @param {string} path - Path to property (e.g., 'user.profile.name')
 * @param {*} defaultValue - Default value if property doesn't exist
 * @returns {*} Property value or default value
 */
export const getNestedProperty = (obj, path, defaultValue = undefined) => {
  const keys = path.split('.');
  let result = obj;

  for (const key of keys) {
    if (result === null || result === undefined) {
      return defaultValue;
    }
    result = result[key];
  }

  return result !== undefined ? result : defaultValue;
};

/**
 * Set nested property in object
 * @param {object} obj - Object to modify
 * @param {string} path - Path to property (e.g., 'user.profile.name')
 * @param {*} value - Value to set
 * @returns {object} Modified object
 */
export const setNestedProperty = (obj, path, value) => {
  const keys = path.split('.');
  const lastKey = keys.pop();
  let current = obj;

  for (const key of keys) {
    if (!current[key] || typeof current[key] !== 'object') {
      current[key] = {};
    }
    current = current[key];
  }

  current[lastKey] = value;
  return obj;
};

/**
 * Remove duplicates from array
 * @param {Array} array - Array to process
 * @param {string} key - Optional key for object arrays
 * @returns {Array} Array without duplicates
 */
export const removeDuplicates = (array, key = null) => {
  if (!Array.isArray(array)) return [];

  if (key) {
    const seen = new Set();
    return array.filter((item) => {
      const value = item[key];
      if (seen.has(value)) return false;
      seen.add(value);
      return true;
    });
  }

  return [...new Set(array)];
};

/**
 * Group array of objects by key
 * @param {Array} array - Array to group
 * @param {string} key - Key to group by
 * @returns {object} Grouped object
 */
export const groupBy = (array, key) => {
  if (!Array.isArray(array)) return {};

  return array.reduce((result, item) => {
    const groupKey = item[key];
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {});
};

/**
 * Sort array of objects by key
 * @param {Array} array - Array to sort
 * @param {string} key - Key to sort by
 * @param {string} order - Sort order ('asc' or 'desc')
 * @returns {Array} Sorted array
 */
export const sortBy = (array, key, order = 'asc') => {
  if (!Array.isArray(array)) return [];

  return [...array].sort((a, b) => {
    const aValue = getNestedProperty(a, key);
    const bValue = getNestedProperty(b, key);

    if (aValue === bValue) return 0;

    const comparison = aValue > bValue ? 1 : -1;
    return order === 'asc' ? comparison : -comparison;
  });
};

/**
 * Filter array of objects
 * @param {Array} array - Array to filter
 * @param {string} searchTerm - Search term
 * @param {string[]} keys - Keys to search in
 * @returns {Array} Filtered array
 */
export const filterBySearch = (array, searchTerm, keys) => {
  if (!Array.isArray(array)) return [];
  if (!searchTerm) return array;

  const lowerSearchTerm = searchTerm.toLowerCase();

  return array.filter((item) => {
    return keys.some((key) => {
      const value = getNestedProperty(item, key);
      if (!value) return false;
      return value.toString().toLowerCase().includes(lowerSearchTerm);
    });
  });
};

/**
 * Download file from blob
 * @param {Blob} blob - Blob to download
 * @param {string} filename - Filename for download
 */
export const downloadBlob = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
export const copyToClipboard = async (text) => {
  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      return true;
    }
  } catch (error) {
    console.error('Error copying to clipboard:', error);
    return false;
  }
};

/**
 * Sleep for specified milliseconds
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise} Promise that resolves after sleep
 */
export const sleep = (ms) => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Retry function with exponential backoff
 * @param {Function} fn - Function to retry
 * @param {number} maxRetries - Maximum number of retries
 * @param {number} delay - Initial delay in milliseconds
 * @returns {Promise} Promise that resolves with function result
 */
export const retryWithBackoff = async (fn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(delay * Math.pow(2, i));
    }
  }
};

/**
 * Parse query string to object
 * @param {string} queryString - Query string to parse
 * @returns {object} Parsed query parameters
 */
export const parseQueryString = (queryString) => {
  const params = new URLSearchParams(queryString);
  const result = {};
  for (const [key, value] of params) {
    result[key] = value;
  }
  return result;
};

/**
 * Build query string from object
 * @param {object} params - Parameters object
 * @returns {string} Query string
 */
export const buildQueryString = (params) => {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      searchParams.append(key, value);
    }
  });
  return searchParams.toString();
};

/**
 * Get initials from name
 * @param {string} name - Full name
 * @returns {string} Initials
 */
export const getInitials = (name) => {
  if (!name) return '';
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};

/**
 * Generate random color
 * @param {string} seed - Optional seed for consistent color
 * @returns {string} Hex color code
 */
export const generateColor = (seed = '') => {
  if (seed) {
    let hash = 0;
    for (let i = 0; i < seed.length; i++) {
      hash = seed.charCodeAt(i) + ((hash << 5) - hash);
    }
    const color = Math.abs(hash).toString(16).slice(0, 6).padEnd(6, '0');
    return `#${color}`;
  }

  return `#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')}`;
};

/**
 * Check if device is mobile
 * @returns {boolean} Whether device is mobile
 */
export const isMobile = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
};

/**
 * Check if device is touch enabled
 * @returns {boolean} Whether device supports touch
 */
export const isTouchDevice = () => {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
};
