# Docker Setup

## Overview
The project uses Docker Compose to manage essential services for the application.

## Services
- **PostgreSQL**: Database service for data storage.
- **Redis**: Caching service for state management.

## Configuration
The `docker-compose.yml` file defines the services and their configurations. Environment variables are used for sensitive data.

## Volumes
- `postgres_data`: Persistent storage for PostgreSQL.
- `redis_data`: Persistent storage for Redis.

## Example Configuration
```yaml
version: "3.9"

services:
  postgres:
    image: postgres:15
    container_name: my_postgres
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:8
    container_name: my_redis
    restart: always
    environment:
      REDIS_PASSWORD: ${REDIS_PASSWORD}
    command: ["redis-server", "--requirepass", "${REDIS_PASSWORD}"]
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```