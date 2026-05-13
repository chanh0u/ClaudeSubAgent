# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a fullstack To-Do application with deadline management, built as a demonstration of multi-agent AI development workflow. The project includes a Node.js/Express backend, React frontend, and SQLite database.

## Architecture

The project follows a layered architecture with automatic validation between layers:

```
Planner (spec.md) → DBA (schema.sql) → Backend (API) → Frontend (UI)
         ↓               ↓                  ↓              ↓
    Requirements    Database Schema    REST API      React Components
```

### Multi-Agent System

This project uses specialized AI agents defined in `.claude/agents/`:

- **Planner**: Creates service specifications (spec.md)
- **DBA**: Designs database schema (schema.sql)
- **Backend**: Implements REST API (app/backend/)
- **Frontend**: Builds React UI (app/frontend/)
- **Controller**: Orchestrates agents and validates consistency across layers
- **Reviewer**: Performs cross-layer validation

## Project Structure

```
ClaudeAgent/
├── spec.md                    # Service specification
├── schema.sql                 # Database schema
├── todos.db                   # SQLite database (auto-generated)
├── app/
│   ├── backend/              # Node.js + Express backend
│   │   ├── server.js         # Server entry point
│   │   ├── routes/           # API route definitions
│   │   ├── controllers/      # Business logic
│   │   └── models/           # Data models & DB access
│   └── frontend/             # React frontend
│       ├── src/
│       │   ├── App.jsx       # Main app component
│       │   ├── components/   # React components
│       │   └── services/     # API service layer
│       └── public/
└── .claude/agents/           # AI agent role definitions
```

## Development Commands

### Backend

```bash
# Navigate to backend directory
cd app/backend

# Install dependencies
npm install

# Start server (port 3000)
npm start

# Development mode with auto-reload
npm run dev
```

### Frontend

```bash
# Navigate to frontend directory
cd app/frontend

# Install dependencies
npm install

# Start development server (port 3001)
npm start

# Build for production
npm build
```

### Database

The SQLite database (`todos.db`) is automatically created on first backend run. To reset the database, delete `todos.db` and restart the backend server.

## API Endpoints

All endpoints are prefixed with `/api/todos`:

- `GET /api/todos` - List all todos
- `POST /api/todos` - Create new todo
- `PUT /api/todos/:id` - Update todo
- `DELETE /api/todos/:id` - Delete todo
- `PATCH /api/todos/:id/toggle` - Toggle completion status

## Technology Stack

- **Backend**: Node.js, Express.js, SQLite3, CORS
- **Frontend**: React 18, React Scripts, Fetch API
- **Database**: SQLite with indexed queries

## Key Design Principles

### Agent Responsibilities

When working on this project, respect the separation of concerns:

- **Planner**: Only defines requirements, no code or DB schema
- **DBA**: Only creates schema, no API or business logic
- **Backend**: Implements APIs exactly as specified, no schema changes
- **Frontend**: Implements UI/UX, no API changes or new features

### Validation Protocol

When making changes, validate consistency between layers:

1. Spec ↔ DB: Schema matches data requirements
2. DB ↔ API: API operations align with schema
3. API ↔ Frontend: Frontend calls match API contracts

### Development Workflow

1. Modify spec.md if requirements change
2. Update schema.sql if data model changes
3. Update backend API to match schema changes
4. Update frontend to match API changes
5. Validate each transition

## Running the Application

1. Start backend server (port 3000)
2. Start frontend dev server (port 3001)
3. Access application at http://localhost:3001
4. Backend API available at http://localhost:3000

## Notes

- The frontend expects the backend to run on port 3000
- CORS is enabled for local development
- All timestamps are in ISO 8601 format
- Deadline dates use YYYY-MM-DD format
- Overdue todos are visually highlighted in red
