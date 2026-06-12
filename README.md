# fastapi-inventory-system

## Description
An inventory management system built with FastAPI utilizing Postgres for persistent data storage and Redis for caching, messaging, and request rate limiting. Implements advanced architectural patterns including CQRS with Event Sourcing, Domain-Driven Design with Hexagonal Architecture, API Gateway, Saga Pattern for distributed transactions, and Cache-Aside caching strategy to ensure high scalability, maintainability, and efficient data handling.

## Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Caching & Messaging:** Redis
- **Language:** Python

## Folder Structure
fastapi-inventory-system/
│
├── app/
│   ├── controllers/            # FastAPI route handlers
│   ├── services/               # Application services implementing business logic
│   ├── repositories/           # Data access layer for Postgres and Redis
│   ├── models/                 # Pydantic models and database schemas
│   ├── events/                 # Event sourcing components
│   ├── config.py               # Configuration and environment settings
│   └── main.py                 # Application entry point (API Gateway)
│
├── alembic/                    # Database migration scripts
│
├── tests/                      # Test suite
│
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Orchestrates multi-container setup
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
└── .env.example                # Sample environment variables

## How to Run Locally
1. Clone the repository:
   `git clone https://github.com/yourusername/fastapi-inventory-system.git`
2. Change directory:
   `cd fastapi-inventory-system`
3. Copy the environment variables file:
   `cp .env.example .env`
4. Start Docker containers:
   `docker-compose up -d --build`
5. Install Python dependencies:
   `pip install -r requirements.txt`
6. Run database migrations:
   `alembic upgrade head`
7. Start the FastAPI server:
   `uvicorn app.main:app --reload`

Access the API documentation at `http://localhost:8000/docs`.

## Environment Variables
Create a `.env` file with the following variables:
- `DATABASE_URL=postgresql://user:password@localhost:5432/inventory_db`
- `REDIS_URL=redis://localhost:6379/0`
- `RATELIMIT_ENABLED=true`
- `RATELIMIT_PER_MINUTE=100`
- `SECRET_KEY=your_secret_key`
- `API_GATEWAY_HOST=0.0.0.0`
- `API_GATEWAY_PORT=8000`

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new feature branch:
   `git checkout -b feature/your-feature`
3. Commit your changes:
   `git commit -am "Add your feature"`
4. Push to the branch:
   `git push origin feature/your-feature`
5. Create a Pull Request.

Please ensure code adheres to the project’s coding standards and includes appropriate tests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.