# RehabYangu Backend

Multi‑tenant SaaS backend for rehabilitation facility management, built with **Django** and **DRF**.

## Tech Stack
- Python 3.14, Django 6.0
- Django REST Framework + Simple JWT
- PostgreSQL 16 (Docker)
- Redis 7 (cache / future queue)
- Docker Compose

## Quick Start
```bash
cd rehabyangu
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

