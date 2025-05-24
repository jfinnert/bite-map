import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base # Updated import
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure DATABASE_URL uses psycopg2 driver for PostgreSQL
raw_db_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if raw_db_url.startswith("postgresql://"):
    # Ensure the psycopg2 driver is specified for SQLAlchemy < 2.0 if not already
    # For SQLAlchemy 2.0+, just "postgresql" should be fine and it picks psycopg2 if installed.
    # However, being explicit can help in some environments.
    if "+" not in raw_db_url.split("://")[1].split("/")[0]: # Check if driver is already specified
        DATABASE_URL = raw_db_url.replace("postgresql://", "postgresql+psycopg2://")
    else:
        DATABASE_URL = raw_db_url
elif raw_db_url.startswith("postgres://"): # Common alias
    if "+" not in raw_db_url.split("://")[1].split("/")[0]:
        DATABASE_URL = raw_db_url.replace("postgres://", "postgresql+psycopg2://")
    else:
        DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://") # Ensure it's at least postgresql
else:
    DATABASE_URL = raw_db_url


# Create a single declarative base for all models
Base = declarative_base() # Reverted to standard declarative_base

# Store the engine globally or pass it around.
# For simplicity in a small app, a global engine can be fine.
_engine = None

def get_engine(db_url: str = None):
    global _engine
    if _engine is None:
        current_url = db_url or DATABASE_URL
        
        # Ensure correct dialect for postgres
        if current_url.startswith("postgres://"):
            current_url = current_url.replace("postgres://", "postgresql://", 1)
        if current_url.startswith("postgresql://") and "postgresql+psycopg2://" not in current_url:
            # Ensure psycopg2 driver is specified if it's a postgresql URL without a specific driver
            # This helps avoid the 'Can't load plugin: sqlalchemy.dialects:postgres'
            parts = current_url.split("://")
            if "+" not in parts[1].split("/")[0]: # check if driver like +psycopg2 is missing
                 current_url = parts[0] + "+psycopg2://" + parts[1]

        print(f"Database.py: Creating engine with URL: {current_url}") # Diagnostic print
        if "sqlite" in current_url:
            _engine = create_engine(current_url, connect_args={"check_same_thread": False})
        else:
            _engine = create_engine(current_url)
    return _engine

# Default engine for non-test use
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
