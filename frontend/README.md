# FlowPilot AI - Frontend

Enterprise-grade React frontend for the FlowPilot AI workflow automation platform.

## Tech Stack

- **React 18.2** - Modern React with Hooks
- **Vite 5** - Lightning-fast build tool
- **TailwindCSS 3** - Utility-first CSS framework
- **Redux Toolkit** - State management
- **React Router 6** - Client-side routing
- **React Hook Form** - Form management
- **Axios** - HTTP client with interceptors
- **Headless UI** - Accessible UI components
- **Heroicons** - Beautiful icon set
- **React Hot Toast** - Toast notifications
- **Recharts** - Data visualization
- **React Flow** - Workflow builder
- **Date-fns** - Date utility library

## Project Structure

```
frontend/
├── public/               # Static assets
├── src/
│   ├── assets/          # Images, fonts, etc.
│   ├── components/      # Reusable components
│   │   ├── ui/         # UI components (Button, Input, Modal, etc.)
│   │   ├── forms/      # Form components
│   │   ├── layout/     # Layout components
│   │   ├── workflow/   # Workflow-specific components
│   │   ├── charts/     # Chart components
│   │   └── tables/     # Table components
│   ├── constants/       # Constants and configuration
│   │   ├── config.js         # App configuration
│   │   ├── apiEndpoints.js   # API endpoint definitions
│   │   ├── routes.js         # Route constants
│   │   ├── workflowSteps.js  # Workflow step definitions
│   │   └── index.js          # Centralized exports
│   ├── features/        # Feature-based modules
│   │   ├── auth/       # Authentication feature
│   │   ├── workflows/  # Workflows feature
│   │   ├── executions/ # Executions feature
│   │   ├── connectors/ # Connectors feature
│   │   ├── documents/  # Documents feature
│   │   ├── analytics/  # Analytics feature
│   │   └── settings/   # Settings feature
│   ├── hooks/           # Custom React hooks
│   ├── layouts/         # Page layouts
│   │   ├── AuthLayout.jsx      # Auth pages layout
│   │   └── DashboardLayout.jsx # Dashboard layout
│   ├── pages/           # Page components
│   │   ├── auth/             # Authentication pages
│   │   ├── workflows/        # Workflow pages
│   │   ├── executions/       # Execution pages
│   │   ├── connectors/       # Connector pages
│   │   ├── documents/        # Document pages
│   │   ├── analytics/        # Analytics pages
│   │   ├── organization/     # Organization pages
│   │   ├── settings/         # Settings pages
│   │   ├── DashboardPage.jsx # Main dashboard
│   │   └── NotFoundPage.jsx  # 404 page
│   ├── services/        # API services
│   │   ├── api.js            # Axios instance
│   │   ├── authService.js    # Auth API calls
│   │   ├── workflowService.js # Workflow API calls
│   │   └── index.js          # Centralized exports
│   ├── store/           # Redux store
│   │   ├── slices/           # Redux slices
│   │   │   └── authSlice.js  # Auth state
│   │   └── index.js          # Store configuration
│   ├── utils/           # Utility functions
│   │   ├── storage.js        # Local storage utilities
│   │   ├── formatters.js     # Data formatters
│   │   ├── validators.js     # Validation functions
│   │   ├── helpers.js        # Helper functions
│   │   └── index.js          # Centralized exports
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # App entry point
│   └── index.css        # Global styles
├── .env                 # Environment variables
├── .env.example         # Environment variables template
├── .eslintrc.cjs        # ESLint configuration
├── .gitignore           # Git ignore rules
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── postcss.config.js    # PostCSS configuration
├── tailwind.config.js   # Tailwind configuration
└── vite.config.js       # Vite configuration
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Update `.env` with your configuration:
```env
VITE_API_URL=http://localhost:8000
VITE_API_VERSION=v1
VITE_APP_NAME=FlowPilot AI
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at http://localhost:3000

### Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

### Linting

Run ESLint:
```bash
npm run lint
```

Fix linting issues:
```bash
npm run lint:fix
```

## Key Features

### Authentication
- Login / Register
- Password Reset
- Multi-Factor Authentication (MFA)
- JWT token management with auto-refresh
- Protected routes

### Dashboard
- Overview metrics
- Recent activity
- Quick actions
- Real-time updates

### Workflows
- Visual workflow builder with drag-and-drop
- Workflow templates
- Version control
- Test and validate workflows
- Import/export workflows

### Executions
- Real-time execution monitoring
- Step-by-step logs
- Retry failed executions
- Cancel running executions

### Connectors
- OAuth2 integration flow
- Manage credentials
- Test connections
- Configure webhooks

### Documents
- Upload and process documents
- View extractions
- Search documents
- Batch processing

### Analytics
- Performance metrics
- Usage statistics
- Error tracking
- Custom reports

### Organization
- Manage members
- Role-based access control
- API key management
- Billing and usage

## UI Components

The app includes a comprehensive design system with the following components:

- **Button** - Multiple variants (primary, secondary, success, danger, etc.)
- **Input** - Text inputs with validation support
- **Modal** - Accessible modal dialogs
- **Card** - Container components
- **Badge** - Status indicators
- **Loading** - Spinners and skeleton loaders
- **Avatar** - User avatars with fallback
- **Form** components - Complete form system with React Hook Form

## State Management

- **Redux Toolkit** - Global state management
- **RTK Query** - Server state caching (optional)
- **React Hook Form** - Form state management
- **React Router** - Navigation state

## API Integration

The app uses Axios with the following features:

- Automatic JWT token attachment
- Token refresh on 401 errors
- Request/response interceptors
- Centralized error handling
- Request/response transformations

## Routing

Protected routes require authentication:
- Dashboard
- Workflows
- Executions
- Connectors
- Documents
- Analytics
- Settings

Public routes (redirects to dashboard if authenticated):
- Login
- Register
- Forgot Password
- Reset Password

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_API_URL | Backend API URL | http://localhost:8000 |
| VITE_API_VERSION | API version | v1 |
| VITE_APP_NAME | Application name | FlowPilot AI |
| VITE_WS_URL | WebSocket URL | ws://localhost:8000 |
| VITE_MAX_FILE_SIZE | Max file upload size (bytes) | 10485760 |
| VITE_SESSION_TIMEOUT | Session timeout (ms) | 3600000 |

## Code Style

- **ESLint** - Code linting
- **Prettier** - Code formatting (via ESLint)
- **React conventions** - Functional components with hooks
- **File naming** - PascalCase for components, camelCase for utilities
- **Import order** - External imports → Internal imports → Styles

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Optimizations

- Code splitting with React.lazy and Suspense
- Route-based code splitting
- Optimized bundle sizes with vendor chunking
- Image optimization
- CSS purging with Tailwind
- Tree shaking

## Accessibility

- ARIA labels
- Keyboard navigation
- Focus management
- Screen reader support
- Color contrast compliance

## Security

- XSS protection
- CSRF token handling
- Secure token storage
- Content Security Policy ready
- Input sanitization

## Contributing

1. Follow the established folder structure
2. Use the existing UI components
3. Follow the code style guidelines
4. Add JSDoc comments to functions
5. Test your changes before committing

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.
