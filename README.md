# Foundational Backend System (Flask + RBAC + JWT)

A modular backend foundation for a larger platform with secure auth and role-based access control.

## Implemented Scope
- JWT authentication
- Roles: `Admin`, `Doctor`, `Member`
- Admin panel backend:
  - Create department
  - List departments
  - Onboard doctor
  - Assign doctor to department
- Layered architecture:
  - Routes (controllers)
  - Services
  - Repositories
  - Models
  - Core utilities/config

## Project Structure
```text
api/
  auth/
    __init__.py
    models.py
    repository.py
    routes.py
    schemas.py
    services.py
    test_repository.py
    test_service.py
  core/
    config.py
    constants.py
    enum.py
    exceptions.py
    extensions.py
    rbac.py
    security.py
  departments/
    __init__.py
    models.py
    repository.py
    routes.py
    schemas.py
    services.py
    test_repository.py
    test_service.py
  doctors/
    __init__.py
    models.py
    repository.py
    routes.py
    schemas.py
    services.py
    test_repository.py
    test_service.py
  models/
    __init__.py
    base.py
  __init__.py
  conftest.py
  main.py
  seed.py
migrations/
  versions/
    a2818e200f5a_initial_migration.py
    b1c2d3e4f5g6_create_departments_table.py
    c3d4e5f6g7h8_create_doctors_tables.py
    dedeb6d32b44_adding_indices.py
  env.py
  script.py.mako
alembic.ini
Dockerfile
docker-compose.yml
pyproject.toml
README.md
```

## Environment Variables
Create `.env` file in project root:

```env
SECRET_KEY=super-secret-app-key
JWT_SECRET_KEY=super-secret-jwt-key
DATABASE_URL=postgresql+psycopg2://postgres:postgres@host.docker.internal:5432/clinic_db
```

Use `localhost` in `DATABASE_URL` when running app outside Docker.

## Run with Poetry
```bash
poetry install
poetry run flask --app api.main db upgrade
poetry run flask --app api.main seed
poetry run python -m api.main
```

## Run with Docker
```bash
docker compose up -d --build
```

## API Endpoints

### Auth
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me` (any authenticated role)
- `GET /auth/doctor/scope` (Doctor only)
- `GET /auth/member/scope` (Member only)

### Admin Panel
- `POST /admin/departments`
- `GET /admin/departments`
- `POST /admin/doctors`
- `POST /admin/departments/{department_id}/assign-doctor`

## RBAC Rules
- Admin: can manage departments and doctors
- Doctor: access doctor-scoped endpoints only
- Member: access member-scoped endpoints only

## Error Handling
- Custom domain exceptions in `api/core/exceptions.py`
- Explicit `try/except` in all API routes for:
  - validation errors
  - business/domain errors
  - unexpected failures

## Seed Credentials
- Admin: `admin@clinic.local` / `Admin@123`
- Doctor: `doctor@clinic.local` / `Doctor@123`
- Member: `member@clinic.local` / `Member@123`
