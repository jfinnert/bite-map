from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Create a separate test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create engine
test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create a test-specific Base
TestBase = declarative_base()

# Create a test sessionmaker
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Initialize all tables
def setup_test_db():
    TestBase.metadata.create_all(bind=test_engine)

# Drop all tables
def teardown_test_db():
    TestBase.metadata.drop_all(bind=test_engine)
