# Florida Business Search Application

A web application that allows users to search for business information from the Florida Secretary of State website. The application consists of a Python backend using FastAPI and Playwright for web scraping, and a React frontend for the user interface.

## Features

- Search for businesses by name
- View detailed business information including:
  - Business name and filing number
  - Registration date and status
  - State of formation
  - Principal address
  - Registered agent information
  - Officers and their roles
  - Filing history
- Data persistence using PostgreSQL database
- Modern, responsive user interface

## Prerequisites

- Docker
- Docker Compose

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd florida-business-search
```

2. Start the application using Docker Compose:
```bash
docker-compose up --build
```

This will:
- Start the PostgreSQL database
- Build and start the Python backend
- Build and start the React frontend
- Install all necessary dependencies

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Architecture

### Backend
- FastAPI framework for the REST API
- Playwright for web scraping
- SQLAlchemy for database ORM
- PostgreSQL for data storage

### Frontend
- React with TypeScript
- Material-UI for components and styling
- Axios for API communication

## API Endpoints

- `GET /search/{business_name}`: Search for businesses by name
- `GET /business/{business_id}`: Get detailed information about a specific business

## Development

### Backend Development
The backend code is in the `backend` directory:
- `src/api/`: API endpoints and routing
- `src/crawler/`: Web scraping logic
- `src/models/`: Database models
- `src/database/`: Database connection and configuration

### Frontend Development
The frontend code is in the `frontend` directory:
- `src/components/`: React components
- `src/App.tsx`: Main application component

## Testing

Example business names for testing:
- ACME COMEDY
- Borador, LLC
- Fighters, Inc

## Error Handling

The application includes comprehensive error handling for:
- Invalid search queries
- Web scraping failures
- Database connection issues
- API communication errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 