# Bite Map

A web application that organizes food videos from social media by location. One tap → URL in, pin on a map + sortable list out. Think "Google Maps layer generated from your TikTok/YouTube food likes."

## Branch Strategy

This project follows a trunk-based development model:

- `main`: Production-ready code, deployed to production
- `dev`: Development branch, merged to main when stable
- Feature branches: Created from dev, merged back via PR

## Tech Stack

### Backend
- FastAPI (Python)
- PostgreSQL with PostGIS for geospatial data
- SQLAlchemy + Alembic for ORM and migrations
- Docker and docker-compose for containerization

### Frontend
- React with TypeScript
- Vite for build system
- Mapbox GL JS for maps
- TanStack Query for data fetching

## Getting Started

Documentation coming soon.

## License

Apache License 2.0