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
  - Filing history
- Data persistence using PostgreSQL database
- User Interface

## Prerequisites

- Docker
- Docker Compose

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Start the application using Docker Compose:
```bash
docker-compose up --build
```

This will:
- Start the PostgreSQL database
- Build and start the Python backend
- Install all necessary dependencies

3. Access the application:
- Backend API: http://localhost:8000

4. Access the frontend:
- Open a new terminal and run:
```bash
cd frontend
npm install
npm run dev
```
- Frontend is running on http://localhost:3000


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

- `GET /search/{business_name}`: Search for businesses by playright crawler if not found in database, otherwise return the business from the database
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

## Future Improvements
- Add improved migrations
- Add useful logging
- Error handling can be improved
- Maybe add frontend to the docker compose too for easier setup.
- Allow searching with vaious types of queries like name, filing number, etc.