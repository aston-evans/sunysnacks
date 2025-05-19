import pytest
from fastapi import Depends  # noqa
from fastapi.testclient import TestClient
from snacks.db import Location, Review, get_session
from snacks.main import app
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

client = TestClient(app)

# Location ID constants for tests
LOCATION_NAMES = {
    "argo": "Argo Tea",
    "marketplace": "Mills Marketplace",
    "mills": "Mills Dining Hall",
    "seasons": "Seasons",
    "wilsbach": "Wilsbach Dining Hall",
}


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="setup_locations")
def setup_locations_fixture(session: Session):
    for location_id, name in LOCATION_NAMES.items():
        location = Location(location_id=location_id, name=name)
        session.add(location)
    session.commit()


def test_root(session: Session, client: TestClient, setup_locations):
    # Use existing locations
    review1_data = {
        "location_id": "argo",
        "rating": 3,
        "title": "Food",
        "body": "Great food",
        "nickname": "test",
    }
    review2_data = {
        "location_id": "mills",
        "rating": 2,
        "title": "chicken",
        "body": "test body",
        "nickname": "test2",
    }
    review1 = Review(**review1_data)
    review2 = Review(**review2_data)
    session.add(review1)
    session.add(review2)
    session.commit()

    response = client.get("/menu")
    assert response.status_code == 200

    # Check for review content in the response
    assert "Food" in response.text
    assert "chicken" in response.text
    assert "Great food" in response.text
    assert "test body" in response.text

    # Get the location name from the session
    mills_location = session.exec(
        select(Location).where(Location.location_id == "mills")
    ).first()
    assert mills_location.name in response.text


# Test leave review pages
@pytest.mark.parametrize("location", LOCATION_NAMES.keys())
def test_leave_review_pages(client: TestClient, setup_locations, location: str):
    response = client.get(f"/create-review/{location}")
    assert response.status_code == 200


def test_create_review(client: TestClient, session: Session, setup_locations):
    review_data = {
        "title": "lunch",
        "rating": 3,
        "body": "body",
        "location_id": "argo",  # Use route location id
        "nickname": "test",
    }

    response = client.post("/reviewcreate", data=review_data, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/reviews/argo"

    # Get location from database
    location = session.exec(select(Location).where(Location.name == "Argo Tea")).first()
    assert location is not None

    # Check if review was created
    review = session.exec(
        select(Review).where(Review.location_id == location.location_id)
    ).first()
    assert review is not None
    assert review.title == "lunch"
    assert review.rating == 3
    assert review.body == "body"
    assert review.location_id == location.location_id
    assert review.nickname == "test"


def test_all_reviews(session: Session, client: TestClient, setup_locations):
    # Use existing locations instead of creating new ones
    seasons = session.exec(select(Location).where(Location.name == "Seasons")).first()
    marketplace = session.exec(
        select(Location).where(Location.name == "Mills Marketplace")
    ).first()

    review1_data = {
        "location_id": seasons.location_id,
        "rating": 3,
        "title": "Food",
        "body": "Great food",
        "nickname": "test",
    }
    review2_data = {
        "location_id": marketplace.location_id,
        "rating": 2,
        "title": "chicken",
        "body": "test body",
        "nickname": "test2",
    }
    review1 = Review(**review1_data)
    review2 = Review(**review2_data)
    session.add(review1)
    session.add(review2)
    session.commit()

    response = client.get("/menu")
    assert response.status_code == 200

    # Check for review content in the response
    assert "Food" in response.text
    assert "chicken" in response.text
    assert "Great food" in response.text
    assert "test body" in response.text
    assert marketplace.name in response.text
    assert seasons.name in response.text


# Test review pages
@pytest.mark.parametrize("location", LOCATION_NAMES.keys())
def test_location_reviews(
    client: TestClient, session: Session, setup_locations, location: str
):
    # Get the location from database
    location_name = LOCATION_NAMES[location]
    db_location = session.exec(
        select(Location).where(Location.name == location_name)
    ).first()
    assert db_location is not None

    review_data = {
        "location_id": db_location.location_id,
        "rating": 5,
        "title": "Croissant",
        "body": "Fantastic food",
        "nickname": "test",
    }

    review = Review(**review_data)
    session.add(review)
    session.commit()

    response = client.get(f"/reviews/{location}")

    assert response.status_code == 200
    assert "Croissant" in response.text
    assert "test" in response.text
    assert "Fantastic food" in response.text


def test_campus_map(client: TestClient, setup_locations):
    response = client.get("/campus-map")
    assert response.status_code == 200
    # Verify all locations are present in the response
    for name in LOCATION_NAMES.values():
        assert name in response.text


@pytest.mark.parametrize("location_id", ["invalid", "nonexistent"])
def test_invalid_location_reviews(
    client: TestClient, setup_locations, location_id: str
):
    response = client.get(f"/reviews/{location_id}")
    assert response.status_code == 404


@pytest.mark.parametrize("location_id", ["invalid", "nonexistent"])
def test_invalid_create_review(client: TestClient, setup_locations, location_id: str):
    review_data = {
        "title": "lunch",
        "rating": 3,
        "body": "body",
        "location_id": location_id,
        "nickname": "test",
    }

    response = client.post("/reviewcreate", data=review_data, follow_redirects=False)
    assert response.status_code == 404


def test_invalid_rating(client: TestClient, setup_locations):
    review_data = {
        "title": "lunch",
        "rating": 6,  # Invalid rating > 5
        "body": "body",
        "location_id": "argo",
        "nickname": "test",
    }

    response = client.post("/reviewcreate", data=review_data, follow_redirects=False)
    assert response.status_code == 422  # Validation error


def test_root_path(client: TestClient, setup_locations):
    response = client.get("/")
    assert response.status_code == 200
    assert "SunySnacks" in response.text


def test_create_review_missing_fields(client: TestClient, setup_locations):
    # Test missing fields
    response = client.post(
        "/reviewcreate",
        data={
            "title": "lunch",
            # missing rating
            "body": "body",
            "location_id": "argo",
            "nickname": "test",
        },
    )
    assert response.status_code == 422  # Validation error

    # Test invalid rating type
    response = client.post(
        "/reviewcreate",
        data={
            "title": "lunch",
            "rating": "not a number",  # invalid rating
            "body": "body",
            "location_id": "argo",
            "nickname": "test",
        },
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.parametrize("path", ["/reviews/", "/create-review/"])
def test_missing_location_id(client: TestClient, setup_locations, path: str):
    response = client.get(path)
    assert response.status_code == 404  # Not found error


def test_reviews_missing_location_in_db(
    client: TestClient, session: Session, setup_locations
):
    # Delete the location from database but keep it in locations.json
    location = session.exec(select(Location).where(Location.name == "Argo Tea")).first()
    session.delete(location)
    session.commit()

    # Try to create a review - should fail because location isn't in DB
    review_data = {
        "title": "lunch",
        "rating": 3,
        "body": "body",
        "location_id": "argo",
        "nickname": "test",
    }
    response = client.post("/reviewcreate", data=review_data)
    assert response.status_code == 404
    assert "Location not found in database" in response.text

    # Try to view reviews - should fail for same reason
    response = client.get("/reviews/argo")
    assert response.status_code == 404
    assert "Location not found in database" in response.text


def test_empty_reviews(client: TestClient, setup_locations):
    response = client.get("/")
    assert response.status_code == 200
    assert "reviews" in response.text  # Page renders even with no reviews


def test_routes_init_locations(session: Session):
    import json
    import os
    import tempfile
    from pathlib import Path

    from snacks.routes import init_locations

    # Create a temporary locations.json
    test_locations = {
        "test": {
            "id": "test",
            "name": "Test Location",
            "description": "Test Description",
            "coordinates": {"lat": 0, "lng": 0},
            "hours": {
                "weekdays": "9-5",
                "friday": "9-5",
                "saturday": "Closed",
                "sunday": "Closed",
            },
            "links": {},
            "map": "",
            "image": "test.jpg",
        }
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create the directory structure
        os.makedirs(os.path.join(tmpdir, "static", "resources"))
        json_path = os.path.join(tmpdir, "static", "resources", "locations.json")

        # Write test data
        with open(json_path, "w") as f:
            json.dump(test_locations, f)

        # Monkey patch the Path handling temporarily
        original_path = Path
        try:

            def mock_path(*args):
                if len(args) > 1 and args[-1] == "locations.json":
                    return Path(json_path)
                return original_path(*args)

            import snacks.routes

            snacks.routes.Path = mock_path

            # Initialize locations
            init_locations(session)

            # Verify the location was created
            location = session.exec(
                select(Location).where(Location.name == "Test Location")
            ).first()
            assert location is not None

        finally:
            # Restore original Path
            snacks.routes.Path = original_path


def test_create_review_invalid_location(client: TestClient):
    # Test non-existent location
    response = client.get("/create-review/nonexistent")
    assert response.status_code == 404
    assert "Location not found" in response.json()["detail"]


def test_root_no_reviews(session: Session, client: TestClient, setup_locations):
    # Test with locations but no reviews
    response = client.get("/menu")
    assert response.status_code == 200
    # Make sure no review content is shown but locations are listed
    for name in LOCATION_NAMES.values():
        assert name in response.text
    assert "No reviews yet" in response.text


def test_init_locations(session: Session, client: TestClient):
    from snacks.routes import init_locations

    # Clear any existing locations
    session.query(Location).delete()
    session.commit()

    # Run the initialization
    init_locations(session)

    # Verify all locations were created
    locations = session.exec(select(Location)).all()
    assert len(locations) == len(LOCATION_NAMES)

    # Verify each location has correct data
    for location in locations:
        assert location.location_id in LOCATION_NAMES
        assert location.name == LOCATION_NAMES[location.location_id]
