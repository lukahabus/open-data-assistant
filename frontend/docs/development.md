# Development Guide

This guide provides detailed information for developers working on the DCAT Metadata Explorer frontend.

## Development Setup

### Prerequisites

1. **Node.js Environment**
   - Node.js 16.x or later
   - npm 7.x or later
   - (Optional) nvm for Node.js version management

2. **IDE Setup**
   - VS Code (recommended)
   - Recommended Extensions:
     - ESLint
     - Prettier
     - TypeScript and JavaScript Language Features
     - Material Icon Theme
     - GitLens

3. **Environment Configuration**
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd dcat-metadata-explorer/frontend

   # Install dependencies
   npm install

   # Create environment file
   cp .env.example .env
   ```

### Development Workflow

1. **Starting Development Server**
   ```bash
   npm start
   ```
   This will:
   - Start the development server on port 3000
   - Enable hot reloading
   - Open the application in your default browser

2. **Running Tests**
   ```bash
   # Run all tests
   npm test

   # Run tests in watch mode
   npm test -- --watch

   # Run tests with coverage
   npm test -- --coverage
   ```

3. **Building for Production**
   ```bash
   npm run build
   ```

## Code Style Guide

### TypeScript Guidelines

1. **Type Definitions**
   ```typescript
   // Use interfaces for objects
   interface User {
     id: string;
     name: string;
     email: string;
   }

   // Use type for unions/intersections
   type Status = 'pending' | 'success' | 'error';
   ```

2. **Component Props**
   ```typescript
   interface ButtonProps {
     label: string;
     onClick: () => void;
     variant?: 'primary' | 'secondary';
     disabled?: boolean;
   }
   ```

3. **Hooks**
   ```typescript
   // Custom hook naming
   function useDatasetQuery(id: string) {
     // Implementation
   }
   ```

### Component Structure

1. **File Organization**
   ```typescript
   // imports
   import React from 'react';
   import { styled } from '@mui/material/styles';

   // types
   interface Props {
     // ...
   }

   // styles
   const StyledComponent = styled('div')(({ theme }) => ({
     // ...
   }));

   // component
   export const Component: React.FC<Props> = ({ ...props }) => {
     // implementation
   };
   ```

2. **Component Naming**
   - Use PascalCase for component names
   - Use camelCase for variables and functions
   - Use UPPER_CASE for constants

### Styling Guidelines

1. **Material-UI Usage**
   ```typescript
   // Use sx prop for one-off styles
   <Box sx={{ mb: 2, p: 1 }}>

   // Use styled for reusable components
   const StyledBox = styled(Box)(({ theme }) => ({
     marginBottom: theme.spacing(2),
     padding: theme.spacing(1),
   }));
   ```

2. **Theme Usage**
   - Use theme values for consistency
   - Follow the design system
   - Maintain responsive design

## Testing Guidelines

### Unit Tests

1. **Component Testing**
   ```typescript
   import { render, screen } from '@testing-library/react';
   import userEvent from '@testing-library/user-event';

   describe('Component', () => {
     it('renders correctly', () => {
       render(<Component />);
       expect(screen.getByText('Title')).toBeInTheDocument();
     });

     it('handles user interaction', async () => {
       render(<Component />);
       await userEvent.click(screen.getByRole('button'));
       expect(screen.getByText('Result')).toBeInTheDocument();
     });
   });
   ```

2. **Hook Testing**
   ```typescript
   import { renderHook, act } from '@testing-library/react-hooks';

   describe('useCustomHook', () => {
     it('returns expected value', () => {
       const { result } = renderHook(() => useCustomHook());
       expect(result.current).toBe(expectedValue);
     });
   });
   ```

### Integration Tests

1. **API Integration**
   ```typescript
   import { rest } from 'msw';
   import { setupServer } from 'msw/node';

   const server = setupServer(
     rest.get('/api/endpoint', (req, res, ctx) => {
       return res(ctx.json({ data: 'mocked' }));
     })
   );

   beforeAll(() => server.listen());
   afterEach(() => server.resetHandlers());
   afterAll(() => server.close());
   ```

## Performance Optimization

### Code Splitting

1. **Route-based Splitting**
   ```typescript
   const Dataset = React.lazy(() => import('./pages/Dataset'));
   ```

2. **Component-based Splitting**
   ```typescript
   const HeavyComponent = React.lazy(() => import('./components/Heavy'));
   ```

### Memoization

1. **Component Memoization**
   ```typescript
   const MemoizedComponent = React.memo(Component);
   ```

2. **Hook Memoization**
   ```typescript
   const memoizedValue = useMemo(() => computeValue(a, b), [a, b]);
   const memoizedCallback = useCallback(() => doSomething(a, b), [a, b]);
   ```

## Deployment

### Build Process

1. **Environment Configuration**
   - Create environment-specific `.env` files
   - Set appropriate API endpoints
   - Configure feature flags

2. **Build Commands**
   ```bash
   # Production build
   npm run build

   # Analyze bundle size
   npm run analyze
   ```

### Continuous Integration

1. **Pre-commit Hooks**
   ```bash
   # Install husky
   npx husky install

   # Add pre-commit hook
   npx husky add .husky/pre-commit "npm test"
   ```

2. **GitHub Actions**
   ```yaml
   name: CI
   on: [push, pull_request]
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - uses: actions/setup-node@v2
         - run: npm ci
         - run: npm test
         - run: npm run build
   ```

## Troubleshooting

### Common Issues

1. **Build Errors**
   - Clear node_modules and package-lock.json
   - Reinstall dependencies
   - Check TypeScript version compatibility

2. **Runtime Errors**
   - Check browser console
   - Verify API endpoints
   - Validate environment variables

### Debugging

1. **React DevTools**
   - Install React Developer Tools extension
   - Use Components tab for component inspection
   - Use Profiler tab for performance analysis

2. **Network Issues**
   - Use Network tab in DevTools
   - Check API response formats
   - Verify CORS configuration

## Contributing

### Pull Request Process

1. Create a feature branch
2. Implement changes
3. Write/update tests
4. Update documentation
5. Create pull request
6. Address review comments
7. Merge after approval

### Code Review Guidelines

1. **What to Look For**
   - Type safety
   - Performance implications
   - Test coverage
   - Documentation updates
   - Accessibility concerns

2. **Review Process**
   - Use GitHub's review features
   - Provide constructive feedback
   - Test changes locally
   - Verify CI/CD pipeline 