"""
Factory functions for creating test data.
"""
from app.core.auth import get_password_hash
import factory
from app.models import Place, User
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
import random

NYC_BBOX = (-74.25909, 40.477399, -73.700272, 40.916178)
SF_BBOX = (-123.173825, 37.63983, -122.28178, 37.929824)
WORLD_BBOX = (-180, -90, 180, 90)

def random_point(bbox):
    min_lng, min_lat, max_lng, max_lat = bbox
    lng = random.uniform(min_lng, max_lng)
    lat = random.uniform(min_lat, max_lat)
    return Point(lng, lat)

def create_user(db, username="testuser", email="test@example.com", password="testpassword", 
               full_name=None, is_active=True, commit=True):
    """
    Create a test user with sane defaults.
    
    Args:
        db: SQLAlchemy session
        username: User's username
        email: User's email
        password: Plain text password (will be hashed)
        full_name: User's full name (optional)
        is_active: Whether user is active
        commit: Whether to commit the transaction (set False if using in a test with transaction rollback)
        
    Returns:
        User object
    """
    # Import here to avoid circular imports
    from app.models import User
    
    # Hash the password
    hashed_password = get_password_hash(password)
    
    # Create user object with proper defaults
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        is_active=is_active
    )
    
    # Add and optionally commit
    db.add(user)
    if commit:
        db.commit()
        db.refresh(user)
        
    return user

def get_token_for_user(client, username="testuser", password="testpassword"):
    """
    Helper to get a valid JWT token for a user.
    
    Args:
        client: TestClient instance
        username: Username to authenticate
        password: Password to authenticate
        
    Returns:
        JWT token string
    """
    response = client.post(
        "/api/auth/token",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200, f"Failed to get token: {response.json()}"
    return response.json()["access_token"]

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = 'commit'

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    hashed_password = factory.LazyAttribute(lambda o: get_password_hash('testpassword'))
    is_active = True
    is_superuser = False


class PlaceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Place
        sqlalchemy_session_persistence = 'commit'

    name = factory.Faker('company')
    address = factory.Faker('address')
    geom = factory.LazyAttribute(lambda o: from_shape(random_point(NYC_BBOX), srid=4326))
    source_id = None

    @classmethod
    def _create(cls, model_class, *args, global_random=False, **kwargs):
        if global_random:
            kwargs['geom'] = from_shape(random_point(WORLD_BBOX), srid=4326)
        return super()._create(model_class, *args, **kwargs)

    @classmethod
    def create_nyc(cls, session, **kwargs):
        return cls.create(session=session, geom=from_shape(random_point(NYC_BBOX), srid=4326), **kwargs)

    @classmethod
    def create_sf(cls, session, **kwargs):
        return cls.create(session=session, geom=from_shape(random_point(SF_BBOX), srid=4326), **kwargs)
