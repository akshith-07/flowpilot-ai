/**
 * Validator Utilities
 * Functions for validating data
 */

/**
 * Validate email address
 * @param {string} email - Email address to validate
 * @returns {boolean} Whether email is valid
 */
export const isValidEmail = (email) => {
  if (!email) return false;
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

/**
 * Validate URL
 * @param {string} url - URL to validate
 * @returns {boolean} Whether URL is valid
 */
export const isValidUrl = (url) => {
  if (!url) return false;
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Validate phone number
 * @param {string} phone - Phone number to validate
 * @returns {boolean} Whether phone number is valid
 */
export const isValidPhone = (phone) => {
  if (!phone) return false;
  const cleaned = phone.replace(/\D/g, '');
  return cleaned.length >= 10 && cleaned.length <= 15;
};

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {object} Validation result with score and feedback
 */
export const validatePasswordStrength = (password) => {
  if (!password) {
    return { score: 0, feedback: 'Password is required', isValid: false };
  }

  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  const feedback = [];
  let score = 0;

  if (password.length < minLength) {
    feedback.push(`At least ${minLength} characters`);
  } else {
    score += 1;
  }

  if (!hasUpperCase) {
    feedback.push('At least one uppercase letter');
  } else {
    score += 1;
  }

  if (!hasLowerCase) {
    feedback.push('At least one lowercase letter');
  } else {
    score += 1;
  }

  if (!hasNumber) {
    feedback.push('At least one number');
  } else {
    score += 1;
  }

  if (!hasSpecialChar) {
    feedback.push('At least one special character');
  } else {
    score += 1;
  }

  const isValid = score === 5;

  return {
    score,
    feedback: isValid ? 'Strong password' : feedback.join(', '),
    isValid,
  };
};

/**
 * Validate file type
 * @param {File} file - File to validate
 * @param {string[]} allowedTypes - Array of allowed file extensions
 * @returns {boolean} Whether file type is allowed
 */
export const isValidFileType = (file, allowedTypes) => {
  if (!file || !allowedTypes || allowedTypes.length === 0) return false;

  const fileName = file.name.toLowerCase();
  return allowedTypes.some((type) => fileName.endsWith(type.toLowerCase()));
};

/**
 * Validate file size
 * @param {File} file - File to validate
 * @param {number} maxSize - Maximum file size in bytes
 * @returns {boolean} Whether file size is within limit
 */
export const isValidFileSize = (file, maxSize) => {
  if (!file) return false;
  return file.size <= maxSize;
};

/**
 * Validate JSON string
 * @param {string} jsonString - JSON string to validate
 * @returns {boolean} Whether JSON string is valid
 */
export const isValidJson = (jsonString) => {
  if (!jsonString) return false;
  try {
    JSON.parse(jsonString);
    return true;
  } catch {
    return false;
  }
};

/**
 * Validate required field
 * @param {*} value - Value to validate
 * @returns {boolean} Whether value is present
 */
export const isRequired = (value) => {
  if (value === null || value === undefined) return false;
  if (typeof value === 'string') return value.trim().length > 0;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'object') return Object.keys(value).length > 0;
  return true;
};

/**
 * Validate minimum length
 * @param {string} value - Value to validate
 * @param {number} minLength - Minimum length
 * @returns {boolean} Whether value meets minimum length
 */
export const hasMinLength = (value, minLength) => {
  if (!value) return false;
  return value.length >= minLength;
};

/**
 * Validate maximum length
 * @param {string} value - Value to validate
 * @param {number} maxLength - Maximum length
 * @returns {boolean} Whether value meets maximum length
 */
export const hasMaxLength = (value, maxLength) => {
  if (!value) return true;
  return value.length <= maxLength;
};

/**
 * Validate number range
 * @param {number} value - Value to validate
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {boolean} Whether value is within range
 */
export const isInRange = (value, min, max) => {
  if (value === null || value === undefined) return false;
  const num = Number(value);
  if (isNaN(num)) return false;
  return num >= min && num <= max;
};

/**
 * Validate alphanumeric string
 * @param {string} value - Value to validate
 * @returns {boolean} Whether value is alphanumeric
 */
export const isAlphanumeric = (value) => {
  if (!value) return false;
  const regex = /^[a-zA-Z0-9]+$/;
  return regex.test(value);
};

/**
 * Validate cron expression
 * @param {string} expression - Cron expression to validate
 * @returns {boolean} Whether cron expression is valid
 */
export const isValidCron = (expression) => {
  if (!expression) return false;
  const regex = /^(\*|([0-5]?\d)) (\*|([01]?\d|2[0-3])) (\*|([01]?\d|2\d|3[01])) (\*|([1-9]|1[0-2])) (\*|([0-6]))$/;
  return regex.test(expression);
};
