#!/usr/bin/env python3
"""
Simple test to verify PostgreSQL testcontainer setup works
"""
import pytest
import sys
import os

# Add project paths
project_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(project_dir, 'app')
sys.path.insert(0, project_dir)
sys.path.insert(0, app_dir)

from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def test_postgres_container_basic():
    """Test that we can start a PostgreSQL container and run a basic query"""
    print("🔄 Starting PostgreSQL container test...")
    
    # Try with a simpler postgres image first to see if it's a PostGIS issue
    with PostgresContainer(
        image="postgres:16",  # Use basic postgres first
        driver="psycopg2", 
        username="test",
        password="test",
        dbname="testdb"
    ) as postgres:
        print("✅ Container started successfully")
        
        # Get connection URL
        connection_url = postgres.get_connection_url()
        print(f"Connection URL: {connection_url}")
        
        # Create engine and test connection
        engine = create_engine(connection_url, echo=False)
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"PostgreSQL version: {version[:50]}...")
            
        print("✅ Basic PostgreSQL container test passed!")


def test_postgis_container():
    """Test that we can start a PostGIS container"""
    print("🔄 Starting PostGIS container test...")
    
    with PostgresContainer(
        image="postgis/postgis:16-3.4",
        driver="psycopg2",
        username="test", 
        password="test",
        dbname="testdb"
    ) as postgres:
        print("✅ PostGIS container started successfully")
        
        # Get connection URL
        connection_url = postgres.get_connection_url()
        print(f"Connection URL: {connection_url}")
        
        # Create engine and test connection
        engine = create_engine(connection_url, echo=False)
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"PostgreSQL version: {version[:50]}...")
            
            # Test PostGIS extension
            result = conn.execute(text("SELECT PostGIS_Version()"))
            postgis_version = result.fetchone()[0]
            print(f"PostGIS version: {postgis_version}")
            
        print("✅ PostGIS container test passed!")


if __name__ == "__main__":
    # Run the basic test first
    print("Testing basic PostgreSQL container...")
    test_postgres_container_basic()
    
    print("\nTesting PostGIS container...")
    test_postgis_container()
