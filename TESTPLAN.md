# TestPLAN.md for fastapi-inventory-system

### 1. Test Strategy
Our testing approach focuses on a layered validation aligned with the architecture:
- **Unit Tests** will verify individual functions like CRUD handlers, domain models, and query filters using pytest-mock with direct function calls.
- **Integration Tests** will validate API endpoints against a test PostgreSQL database using TestClient, ensuring correct request/response payloads, status codes, and interactions with repositories. Redis will be mocked or connected to a dedicated test instance.
- **End-to-End (E2E) Tests** will simulate real user scenarios across multiple components, verifying data consistency and flows via actual API requests with realistic data, ensuring the CQRS, caching, and saga workflows work cohesively.

### 2. Test Levels

#### Unit Tests
- `create_item()` in `item_service.py`; verify it creates items with valid data and raises validation errors for invalid inputs.
- `get_item()` in `item_service.py`; test correct retrieval from in-memory domain models.
- `apply_discount()` in `discount_service.py`; mock data and test discount calculations.

#### Integration Tests
- `GET /items/{item_id}`; confirm response with correct item data, 404 for missing items.
- `POST /items/`; test item creation with valid payload, expect 201 and correct data saved.
- `DELETE /items/{item_id}`; confirm item removal and 204 response.
- Redis cache for `GET /items/{item_id}`; ensure cached data is returned instead of DB on subsequent calls.
- `POST /transactions/saga/start`; test initiation of distributed transaction, verify saga state and coordination with Postgres.

#### E2E Tests
- Complete flow: Create an item via `POST /items/`, retrieve with `GET /items/{id}`, modify via `PUT /items/{id}`, delete via `DELETE /items/{id}`.
- Cache validation: Ensure Redis cache invalidation or updates after different write operations.
- Rate limit test: Simulate multiple requests exceeding Redis rate limit threshold, expect 429 responses.
- Distributed transaction saga flow: Simulate a multi-step purchase process, verify commit/rollback behaviors.
- Data consistency test: Simultaneously modify an item from multiple clients, ensure last write wins or conflict resolution occurs correctly.

### 3. Test Cases Table

| ID   | Test Case                                              | Type           | Priority | Expected Result                                        |
|-------|--------------------------------------------------------|----------------|----------|--------------------------------------------------------|
| TC-001 | GET /items/1 when item exists                         | API Endpoint   | High     | 200 OK, correct item data                              |
| TC-002 | GET /items/9999 when item missing                     | API Endpoint   | High     | 404 Not Found                                          |
| TC-003 | POST /items/ with valid data                           | API Endpoint   | High     | 201 Created, item saved in database                     |
| TC-004 | POST /items/ with missing required fields             | API Endpoint   | Medium   | 422 Unprocessable Entity                                |
| TC-005 | PUT /items/1 to update item data                       | API Endpoint   | High     | 200 OK, item updated                                   |
| TC-006 | DELETE /items/1 when item exists                       | API Endpoint   | High     | 204 No Content                                         |
| TC-007 | GET /items/1 caching via Redis                        | API Endpoint   | Medium   | 200 OK, data served from Redis when cached             |
| TC-008 | Rate limiting test with Redis exceeding limit          | API Endpoint   | Medium   | 429 Too Many Requests                                   |
| TC-009 | Start a saga transaction via POST /transactions/saga/start | API Endpoint | High | 202 Accepted, saga initiated and stored in Redis       |
| TC-010 | End-to-end create, fetch, modify, delete cycle        | Full Flow      | High     | All steps succeed with expected responses             |

### 4. Edge Cases
- Attempt to retrieve an item immediately after deletion (ensure 404).
- Send malformed JSON payloads to POST /items/ (expect validation errors).
- Simultaneously attempt to update the same item from multiple clients; verify conflict handling.
- Trigger cache expiration manually; ensure fresh data is retrieved from Postgres.
- Perform a large bulk insert via POST /items/bulk and verify all items persist correctly.

### 5. Test Data Requirements
- Seed Postgres with multiple test items including edge-case data (empty fields, max length strings).
- Fixtures for creating valid and invalid item payloads.
- Redis preloaded with cache entries for certain items.
- Data for testing saga states, transactions, and message queues.
- Test user data for rate limiting validation.

### 6. Tools & Setup
- **Testing Framework:** `pytest`, `pytest-asyncio`
- **HTTP Client:** FastAPI’s `TestClient` for API testing
- **Mocking:** `pytest-mock` for mocking database or cache calls
- **Database:** PostgreSQL test container, setup with `docker-compose`:
  - `docker run -d --name test-postgres -e POSTGRES_DB=testdb -e POSTGRES_USER=user -e POSTGRES_PASSWORD=pass -p 5432:5432`
- **Redis:** Dedicated Redis instance for testing, setup via Docker:
  - `docker run -d --name test-redis -p 6379:6379 redis`
- **Commands:**
  - Install dependencies: `pip install pytest pytest-asyncio redis pytest-mock`
  - Run tests: `pytest --maxfail=1 --disable-warnings -v`
  - Setup testing database: execute Alembic migrations or SQL seed scripts.
  - Spin up Redis and PostgreSQL containers before tests; teardown after.