# Deployment Guide

This guide details how to deploy the AI Storytelling Workspace using Docker Compose for production or staging environments.

## Prerequisites
- Docker Engine 24.0+
- Docker Compose v2+
- A Linux host (Ubuntu 22.04 LTS recommended) with at least 4GB RAM and 2 CPUs.
- API keys for Mistral and/or OpenAI.

## Environment Configuration

1. Clone the repository on the target server.
2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
3. Update `.env` with production values:
   - Set `ENVIRONMENT=production`
   - Configure secure `MYSQL_PASSWORD` and `MYSQL_ROOT_PASSWORD`
   - Set `MISTRAL_API_KEY` and `OPENAI_API_KEY`
   - Ensure `CORS_ORIGINS` includes your production domain.

## Building and Running

The project includes 7 Docker services managed via `docker-compose.prod.yml`:
1. `api`: FastAPI backend
2. `worker`: Celery task processor
3. `web`: Angular frontend (served via Nginx)
4. `db`: MySQL database
5. `redis`: Message broker and cache
6. `phpmyadmin`: Database administration (optional in production)
7. `nginx`: Reverse proxy routing traffic

To start the environment:
```bash
docker-compose -f docker/docker-compose.prod.yml up -d --build
```

## Database Migrations

Once the database container is healthy, run the initial migrations to set up the schema:
```bash
docker-compose -f docker/docker-compose.prod.yml exec api alembic upgrade head
```

## Nginx and SSL

The default `docker/nginx/nginx.conf` sets up reverse proxying for the Web UI (`/`) and API (`/api`).
For production, it is highly recommended to place this setup behind an SSL termination proxy (like Traefik, AWS ALB, or an edge Nginx with Certbot).

## Monitoring and Logs

View logs for all services:
```bash
docker-compose -f docker/docker-compose.prod.yml logs -f
```

View specific service logs (e.g., workers):
```bash
docker-compose -f docker/docker-compose.prod.yml logs -f worker
```

## Scaling Workers

If AI tasks are queuing up, you can scale the Celery workers:
```bash
docker-compose -f docker/docker-compose.prod.yml up -d --scale worker=3
```
*Note: Be mindful of your API rate limits when scaling concurrent workers.*

## Backups

Back up the MySQL database using standard `mysqldump`:
```bash
docker exec storytelling-db mysqldump -u root -p${MYSQL_ROOT_PASSWORD} storytelling_db > backup_$(date +%F).sql
```
