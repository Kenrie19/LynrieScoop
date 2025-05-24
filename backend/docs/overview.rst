========
Overview
========

LynrieScoop is a comprehensive cinema management system that provides APIs for managing cinema operations including:

* Movie listings and details
* Cinema and screening room management
* Seat booking and reservation
* User authentication and profiles
* Admin operations

Architecture
===========

The application is built using:

* **FastAPI**: Modern, fast web framework for building APIs with Python
* **PostgreSQL**: Robust relational database for storing cinema data
* **MQTT**: Message queue for real-time notifications and updates
* **SQLAlchemy**: SQL toolkit and ORM for database interactions
* **Pydantic**: Data validation and settings management

Key Components
=============

1. **API Routes**: RESTful endpoints organized by domain
2. **Data Models**: SQLAlchemy ORM models representing the database schema
3. **Schemas**: Pydantic models for request/response validation
4. **Core Services**: Configuration, security, and MQTT messaging

Getting Started
==============

The API server can be started using Docker:

.. code-block:: bash

   docker-compose up backend

Once running, the API documentation is available at:

* OpenAPI/Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc
