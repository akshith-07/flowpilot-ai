/**
 * Workflow Step Definitions
 * Defines all available workflow step types and their configurations
 */

export const STEP_CATEGORIES = {
  AI: 'ai',
  ACTION: 'action',
  LOGIC: 'logic',
  INTEGRATION: 'integration',
};

export const AI_STEPS = {
  SUMMARIZE: {
    type: 'ai_summarize',
    name: 'Summarize',
    category: STEP_CATEGORIES.AI,
    icon: 'DocumentTextIcon',
    description: 'Summarize text content using AI',
    color: '#8b5cf6',
    config: {
      inputs: ['text'],
      outputs: ['summary'],
      settings: ['prompt', 'temperature', 'maxLength'],
    },
  },
  EXTRACT: {
    type: 'ai_extract',
    name: 'Extract Data',
    category: STEP_CATEGORIES.AI,
    icon: 'ServerIcon',
    description: 'Extract structured data from text',
    color: '#8b5cf6',
    config: {
      inputs: ['text', 'schema'],
      outputs: ['extracted_data'],
      settings: ['prompt', 'temperature', 'schema'],
    },
  },
  CLASSIFY: {
    type: 'ai_classify',
    name: 'Classify',
    category: STEP_CATEGORIES.AI,
    icon: 'TagIcon',
    description: 'Classify content into categories',
    color: '#8b5cf6',
    config: {
      inputs: ['text', 'categories'],
      outputs: ['classification', 'confidence'],
      settings: ['prompt', 'temperature', 'categories'],
    },
  },
  SENTIMENT: {
    type: 'ai_sentiment',
    name: 'Sentiment Analysis',
    category: STEP_CATEGORIES.AI,
    icon: 'FaceSmileIcon',
    description: 'Analyze sentiment of text',
    color: '#8b5cf6',
    config: {
      inputs: ['text'],
      outputs: ['sentiment', 'score'],
      settings: ['prompt', 'temperature'],
    },
  },
  TRANSLATE: {
    type: 'ai_translate',
    name: 'Translate',
    category: STEP_CATEGORIES.AI,
    icon: 'LanguageIcon',
    description: 'Translate text to another language',
    color: '#8b5cf6',
    config: {
      inputs: ['text', 'target_language'],
      outputs: ['translated_text'],
      settings: ['prompt', 'temperature', 'source_language', 'target_language'],
    },
  },
  GENERATE: {
    type: 'ai_generate',
    name: 'Generate Content',
    category: STEP_CATEGORIES.AI,
    icon: 'SparklesIcon',
    description: 'Generate content using AI',
    color: '#8b5cf6',
    config: {
      inputs: ['prompt', 'context'],
      outputs: ['generated_text'],
      settings: ['prompt', 'temperature', 'maxLength'],
    },
  },
};

export const ACTION_STEPS = {
  SEND_EMAIL: {
    type: 'action_send_email',
    name: 'Send Email',
    category: STEP_CATEGORIES.ACTION,
    icon: 'EnvelopeIcon',
    description: 'Send an email',
    color: '#3b82f6',
    config: {
      inputs: ['to', 'subject', 'body'],
      outputs: ['message_id', 'status'],
      settings: ['from', 'cc', 'bcc', 'attachments', 'template'],
    },
  },
  HTTP_REQUEST: {
    type: 'action_http_request',
    name: 'HTTP Request',
    category: STEP_CATEGORIES.ACTION,
    icon: 'GlobeAltIcon',
    description: 'Make an HTTP request',
    color: '#3b82f6',
    config: {
      inputs: ['url', 'method', 'headers', 'body'],
      outputs: ['response', 'status_code'],
      settings: ['method', 'headers', 'auth', 'timeout'],
    },
  },
  SLACK_MESSAGE: {
    type: 'action_slack_message',
    name: 'Send Slack Message',
    category: STEP_CATEGORIES.ACTION,
    icon: 'ChatBubbleLeftRightIcon',
    description: 'Send a message to Slack',
    color: '#3b82f6',
    config: {
      inputs: ['channel', 'message'],
      outputs: ['message_id', 'timestamp'],
      settings: ['channel', 'username', 'icon_emoji', 'attachments'],
    },
  },
  DATABASE_QUERY: {
    type: 'action_database_query',
    name: 'Database Query',
    category: STEP_CATEGORIES.ACTION,
    icon: 'CircleStackIcon',
    description: 'Execute a database query',
    color: '#3b82f6',
    config: {
      inputs: ['query', 'parameters'],
      outputs: ['results', 'row_count'],
      settings: ['connection', 'query', 'timeout'],
    },
  },
  FILE_UPLOAD: {
    type: 'action_file_upload',
    name: 'Upload File',
    category: STEP_CATEGORIES.ACTION,
    icon: 'ArrowUpTrayIcon',
    description: 'Upload a file to storage',
    color: '#3b82f6',
    config: {
      inputs: ['file', 'destination'],
      outputs: ['file_url', 'file_id'],
      settings: ['destination', 'public', 'metadata'],
    },
  },
  WEBHOOK: {
    type: 'action_webhook',
    name: 'Trigger Webhook',
    category: STEP_CATEGORIES.ACTION,
    icon: 'BoltIcon',
    description: 'Trigger a webhook',
    color: '#3b82f6',
    config: {
      inputs: ['url', 'payload'],
      outputs: ['response', 'status'],
      settings: ['url', 'method', 'headers', 'retry'],
    },
  },
};

export const LOGIC_STEPS = {
  CONDITION: {
    type: 'logic_condition',
    name: 'Condition',
    category: STEP_CATEGORIES.LOGIC,
    icon: 'CodeBracketIcon',
    description: 'Branch based on condition',
    color: '#10b981',
    config: {
      inputs: ['condition'],
      outputs: ['true_branch', 'false_branch'],
      settings: ['condition', 'operator'],
    },
  },
  LOOP: {
    type: 'logic_loop',
    name: 'Loop',
    category: STEP_CATEGORIES.LOGIC,
    icon: 'ArrowPathIcon',
    description: 'Iterate over items',
    color: '#10b981',
    config: {
      inputs: ['items'],
      outputs: ['item', 'index'],
      settings: ['max_iterations', 'break_condition'],
    },
  },
  DELAY: {
    type: 'logic_delay',
    name: 'Delay',
    category: STEP_CATEGORIES.LOGIC,
    icon: 'ClockIcon',
    description: 'Wait for a specified time',
    color: '#10b981',
    config: {
      inputs: ['duration'],
      outputs: ['completed_at'],
      settings: ['duration', 'unit'],
    },
  },
  MERGE: {
    type: 'logic_merge',
    name: 'Merge',
    category: STEP_CATEGORIES.LOGIC,
    icon: 'ArrowsPointingInIcon',
    description: 'Merge multiple inputs',
    color: '#10b981',
    config: {
      inputs: ['input1', 'input2'],
      outputs: ['merged'],
      settings: ['strategy'],
    },
  },
  SPLIT: {
    type: 'logic_split',
    name: 'Split',
    category: STEP_CATEGORIES.LOGIC,
    icon: 'ArrowsPointingOutIcon',
    description: 'Split data into parts',
    color: '#10b981',
    config: {
      inputs: ['data'],
      outputs: ['parts'],
      settings: ['delimiter', 'max_parts'],
    },
  },
  VARIABLE: {
    type: 'logic_variable',
    name: 'Set Variable',
    category: STEP_CATEGORIES.LOGIC,
    icon: 'VariableIcon',
    description: 'Set or update a variable',
    color: '#10b981',
    config: {
      inputs: ['value'],
      outputs: ['variable'],
      settings: ['name', 'scope'],
    },
  },
};

export const INTEGRATION_STEPS = {
  GMAIL: {
    type: 'integration_gmail',
    name: 'Gmail',
    category: STEP_CATEGORIES.INTEGRATION,
    icon: 'EnvelopeIcon',
    description: 'Interact with Gmail',
    color: '#f59e0b',
    config: {
      inputs: ['action', 'params'],
      outputs: ['result'],
      settings: ['action', 'connector'],
    },
  },
  SLACK: {
    type: 'integration_slack',
    name: 'Slack',
    category: STEP_CATEGORIES.INTEGRATION,
    icon: 'ChatBubbleLeftRightIcon',
    description: 'Interact with Slack',
    color: '#f59e0b',
    config: {
      inputs: ['action', 'params'],
      outputs: ['result'],
      settings: ['action', 'connector'],
    },
  },
  NOTION: {
    type: 'integration_notion',
    name: 'Notion',
    category: STEP_CATEGORIES.INTEGRATION,
    icon: 'DocumentIcon',
    description: 'Interact with Notion',
    color: '#f59e0b',
    config: {
      inputs: ['action', 'params'],
      outputs: ['result'],
      settings: ['action', 'connector'],
    },
  },
  GOOGLE_DRIVE: {
    type: 'integration_google_drive',
    name: 'Google Drive',
    category: STEP_CATEGORIES.INTEGRATION,
    icon: 'FolderIcon',
    description: 'Interact with Google Drive',
    color: '#f59e0b',
    config: {
      inputs: ['action', 'params'],
      outputs: ['result'],
      settings: ['action', 'connector'],
    },
  },
  SALESFORCE: {
    type: 'integration_salesforce',
    name: 'Salesforce',
    category: STEP_CATEGORIES.INTEGRATION,
    icon: 'CloudIcon',
    description: 'Interact with Salesforce',
    color: '#f59e0b',
    config: {
      inputs: ['action', 'params'],
      outputs: ['result'],
      settings: ['action', 'connector'],
    },
  },
};

export const ALL_STEPS = {
  ...AI_STEPS,
  ...ACTION_STEPS,
  ...LOGIC_STEPS,
  ...INTEGRATION_STEPS,
};

export const STEP_TYPES = Object.keys(ALL_STEPS).reduce((acc, key) => {
  acc[key] = ALL_STEPS[key].type;
  return acc;
}, {});

export const getStepByType = (type) => {
  return Object.values(ALL_STEPS).find((step) => step.type === type);
};

export const getStepsByCategory = (category) => {
  return Object.values(ALL_STEPS).filter((step) => step.category === category);
};
