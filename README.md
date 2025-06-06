# LynrieScoop

LynrieScoop is a school project for building a cinema web application. The system allows visitors to search for movies, view showings, and reserve tickets. Managers can manage movies and showings through a secure section. Both the backend and frontend are present in this repository.

## Features

- Integration with [The Movie Database](https://www.themoviedb.org/) for movie data
- Management of showings and availability
- Real-time updates via MQTT
- Authentication and authorization with JWT (users and managers)
- Extensive REST API with OpenAPI (Swagger) documentation

## Technologies

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python), SQLAlchemy, Pydantic, PostgreSQL
- **Frontend**: HTML, CSS, and TypeScript (built with [Eleventy](https://www.11ty.dev/))
- **Messaging**: Mosquitto MQTT broker
- **Docker** and **Docker Compose** for development and deployment

## Repository Overview

- `backend/` – FastAPI backend with database models, API routes, and MQTT client
- `frontend/` – Website source files (templates, TypeScript, styles)
- `docs/` – Extensive documentation on architecture, API, and deployment
- `compose.yaml` – Docker Compose configuration to start all services locally

## Quick Start

### Requirements

- Python 3.10+
- Node.js 16+
- PostgreSQL
- MQTT broker (Mosquitto)

### Manual Startup

1. Start the MQTT broker:
   ```bash
   docker-compose up mosquitto
   ```
2. Start the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
3. Start the frontend:
   ```bash
   cd frontend
   npm install
   npm start
   ```
4. Visit <http://localhost:3000> for the web app.

### Using Docker Compose

All services can be started at once with:
```bash
docker compose up --build
```
This will start the database, MQTT broker, backend, and frontend in containers.

## Documentation

Detailed explanations about architecture, API, and deployment can be found in the [`docs/`](docs/README.md) folder. The documentation can be viewed locally using MkDocs:
```bash
mkdocs serve -f config/mkdocs/mkdocs.yaml
```

## License

This project is intended for educational purposes.
