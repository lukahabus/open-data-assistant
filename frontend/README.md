# DCAT Metadata Explorer Frontend

A modern web interface for exploring and analyzing DCAT metadata using advanced semantic analysis and natural language processing.

## Features

- 🔍 Natural Language Search: Search datasets using plain language queries
- 📊 Semantic Analysis: Advanced metadata analysis with insights and relationships
- 🔗 Dataset Clustering: Discover related datasets through semantic clustering
- 📈 Quality Assessment: Automated metadata quality analysis and suggestions

## Technology Stack

- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI v5
- **State Management**: React Query for server state
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Development Tools**: React Scripts, ESLint, TypeScript

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API client and endpoints
│   ├── components/    # Reusable UI components
│   ├── config/        # Configuration files
│   ├── pages/         # Page components
│   ├── services/      # Service utilities
│   ├── theme/         # Theme configuration
│   ├── types/         # TypeScript type definitions
│   ├── App.tsx        # Main application component
│   └── index.tsx      # Application entry point
├── public/            # Static assets
└── package.json       # Project dependencies
```

## Getting Started

### Prerequisites

- Node.js 16.x or later
- npm 7.x or later

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd open-data-assistant/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the frontend directory:
```env
REACT_APP_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`.

## Available Scripts

- `npm start`: Runs the app in development mode
- `npm test`: Launches the test runner
- `npm run build`: Builds the app for production
- `npm run eject`: Ejects from Create React App

## Components

### Pages

- **Home**: Landing page with search and featured datasets
- **Search**: Advanced dataset search with filters
- **Dataset**: Detailed dataset view with metadata insights
- **Clusters**: Dataset clustering visualization
- **About**: System information and documentation

### Core Components

- **Layout**: Main application layout with navigation
- **SearchBar**: Reusable search component
- **DatasetCard**: Dataset display component
- **MetadataInsights**: Metadata analysis display

## API Integration

The frontend communicates with the FastAPI backend through a RESTful API. Key endpoints:

- `/query`: Natural language dataset queries
- `/suggest`: Dataset suggestions
- `/analyze`: Metadata analysis
- `/clusters`: Dataset clustering
- `/similar`: Similar dataset discovery

## Theme Customization

The application uses a customized Material-UI theme with:

- Custom color palette
- Typography scale
- Component style overrides
- Responsive design utilities

## State Management

- **Server State**: Managed by React Query
- **Query Cache**: 5-minute stale time, 30-minute cache
- **Error Handling**: Automatic retries with exponential backoff
- **Real-time Updates**: Configurable refetch intervals

## Development Guidelines

1. **Code Style**
   - Follow TypeScript best practices
   - Use functional components with hooks
   - Implement proper error boundaries
   - Write descriptive component documentation

2. **Component Structure**
   - Keep components focused and reusable
   - Implement proper prop typing
   - Use composition over inheritance
   - Follow Material-UI patterns

3. **Performance**
   - Implement proper memoization
   - Use lazy loading for routes
   - Optimize bundle size
   - Monitor React Query cache

4. **Testing**
   - Write unit tests for components
   - Test API integration
   - Verify error handling
   - Check responsive design

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Material-UI team for the component library
- React Query team for the excellent data-fetching library
- FastAPI team for the backend framework 