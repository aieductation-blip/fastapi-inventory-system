# ARCHITECTURE.md: fastapi-inventory-system

## Overview

The **fastapi-inventory-system** is a web API built with **FastAPI**, leveraging **PostgreSQL** for persistent storage and **Redis** for caching, messaging, and rate limiting. It adopts complex architectural patterns such as CQRS with Event Sourcing, Domain-Driven Design (DDD), Hexagonal Architecture, API Gateway, Saga Pattern, and Cache-Aside caching to manage inventory data efficiently, reliably, and scalably.

## Architecture Diagram

+------------------------+                   +----------------------+
|     External Clients   |                   |     External APIs    |
|  (Web, Mobile Apps)    |                   | Payment or Shipping  |
+-----------+------------+                   +------------+---------+
            | Endpoint Calls                                  |
            | (e.g., GET /inventory/123, POST /inventory/add)|
            v                                                 v
+------------------------------+                +------------------------------+
|        FastAPI Gateway       |                |     FastAPI Inventory API   |
| (Request Throttling, Rate Limiting, API Gateway Layer)             |
+--------------+---------------+                +--------------+--------------+
               |                                            |
   +-----------+-----------+                +--------------+--------------+
   | HTTP Requests (e.g.,  |                | Application Services Layer  |
   | GET /inventory/123)   |                | (Commands/Queries)          |
   +-----------+-----------+                +--------------+--------------+
               |                                            |
        +------+-------+                            +-------+--------+
        | Domain Layer |                            | Infrastructure |
        | (Entities,   |                            | Repositories,  |
        | Business Logic) |                          | Event Sourcing |
        +------+--------+                            +--------+-------+
               |                                              |
           +---+---+                                   +------+-------+
           | Repositories (Postgres tables: inventory_items, inventory_events) |
           +---+---+                                   +--------------+
               |                                              |
      +--------+-------+                              +--------+-------+
      | Postgres Database |                          | Redis Cache   |
      | (Write Model,     |                          | (Read Model, |
      | Tables: inventory_items,|                     | Caching, PubSub) |
      | inventory_events)  |                         +--------------+
      +--------+--------+
               |
     +---------+---------+
     | Event Sourcing   |
     | (Append-only,    |
     | Inventory Events)|
     +------------------+

## Technologies and Rationales

- **FastAPI**: Chosen over Flask because of native async support, superior performance, and automatic OpenAPI documentation, aligning with our API Gateway requirements and high concurrency needs.
- **PostgreSQL**: Selected over alternatives like MySQL for its advanced features (e.g., JSONB, native support for complex queries, and robust transactional capabilities) which are essential for event sourcing and CQRS.
- **Redis**: Used over Memcached for caching because of its rich data structures (pub/sub, sorted sets) facilitating event-driven updates and rate limiting with an atomic, in-memory store.
  
## Data Flow and API Endpoints

### Inventory Query (Read Model with Cache-Aside Pattern)

- **GET** `/inventory/{item_id}`

1. FastAPI receives the request.
2. Checks Redis cache for `inventory:{item_id}`.
3. If cache hit, returns cached data.
4. If cache miss:
   - Sends SQL query: `SELECT * FROM inventory_items WHERE item_id = %s`.
   - Results fetched from Postgres.
   - Cache updated with new data in Redis with TTL.
5. Response: JSON object representing inventory item.

### Inventory Update (Command with CQRS and Event Sourcing)

- **POST** `/inventory/{item_id}/update`

1. FastAPI receives the request with update payload.
2. Sends a command to Application Service layer.
3. Application Service:
   - Validates data.
   - Creates an `InventoryUpdatedEvent`.
   - Stores event in `inventory_events` table within a transaction.
   - Publishes event via Redis Pub/Sub.
4. Event Sourcing mechanism appends event to event stream.
5. Materialized read models in Redis listen to Pub/Sub channel, update cached data.
6. Responds with success or error.

### Distributed Transaction Coordination (Saga Pattern)

- Coordinate inventory reservation and payment processing across multiple services.
- FastAPI calls `POST /reservations` which initiates a distributed saga.
- Saga orchestrator manages compensating transactions if any step fails.
- Final state committed if all steps succeed, stored as an inventory event.

## Components and Responsibilities

### API Gateway (FastAPI)

- Acts as the single entry point.
- Implements rate limiting and request throttling via Redis (e.g., using Redis-based token bucket).
- Routes requests to specific endpoints.
- Handles authentication, logging, and request validation.

### HTTP Handlers (FastAPI Controllers)

- Map HTTP methods to application commands and queries.
- Examples:
  - `GET /inventory/{item_id}`
  - `POST /inventory/{item_id}/update`
  - `POST /reservations`

### Application Services (Python Modules)

- Encapsulate business logic.
- Handle commands, generate events, coordinate workflows.
- Use dependency injection for repositories and event handlers.

### Repositories (Postgres)

- **inventory_items**:
  - `item_id UUID PRIMARY KEY`
  - `name TEXT`
  - `description TEXT`
  - `quantity INT`
  - `last_updated TIMESTAMPTZ`
- **inventory_events**:
  - `event_id SERIAL PRIMARY KEY`
  - `item_id UUID`
  - `event_type TEXT` (e.g., 'UPDATE', 'RESERVATION')
  - `payload JSONB`
  - `created_at TIMESTAMPTZ`

### Read Model Caching (Redis)

- Stores:
  - `inventory:{item_id}` as JSON string.
- Updates via Redis Pub/Sub subscribers listening to `inventory_events` channel.
- Implements the Cache-Aside pattern:
  - Read from Redis first, fallback to Postgres.
  - Update Redis after write or event.

### Event Sourcing

- Events appended to `inventory_events`.
- Used to reconstruct current state or generate projections.
- Supports CQRS by separating writes (events) and reads (projections).

## Cross-Cutting Concerns

- **Rate Limiting**: Redis token bucket algorithm applied per IP or API key.
- **Event Delivery**: Redis Pub/Sub channels distribute inventory events to update read models asynchronously.
- **Saga Coordination**: Managed through dedicated Python services or FastAPI endpoints, ensuring eventual consistency and compensating actions if any step fails.

## Conclusion

This architecture leverages specific components to fulfill the requirements:
- **FastAPI** for high-performance API Gateway, with built-in async capabilities.
- **PostgreSQL** for durable, complex event sourcing storage.
- **Redis** for high-speed caching, pub/sub messaging, and rate limiting.

The layered, hexagonal structure facilitates clear separation of concerns and supports scalability of individual parts, with coordinated event sourcing, CQRS, and Saga patterns ensuring consistency and reliability.