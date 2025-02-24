import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel, select
from fastapi import Depends  # noqa
from snacks.main import app
from sqlmodel.pool import StaticPool
from snacks.db import Review, Location, get_session

client = TestClient(app)

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
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


"""def test_register(client: TestClient, session: Session):
    response = client.post(
        "/register", data={"username": "aston", 
                           "password": "test"},
                           follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "auth/login"

    user = session.exec(select(User).where(User.username == "aston")).first()
    assert user is not None 
    """

# login pages
def test_root(session: Session, client: TestClient):
    """user1_data = {"username": "test", "password": "test password"}
    user1 = User(**user1_data)

    user2_data = {"username": "aston", "password": "test"}
    user2 = User(**user2_data)

    session.add(user1)
    session.add(user2)
    session.commit()
    """
    # locations
    location1 = Location(name="test lo")
    location2 = Location(name="dining hall")
    session.add(location1)
    session.add(location2)
    session.commit()

    # reviews
    review1_data = {
        # "author_id": user1.user_id,
        "location_id": location1.location_id,
        "rating": 3,
        "title": "Food",
        "body": "Great food",
        "nickname": "test",
    }
    review2_data = {
        # "author_id": user2.user_id,
        "location_id": location2.location_id,
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

    assert "Food" in response.text
    assert "chicken" in response.text
    assert "test" in response.text
    assert "test2" in response.text
    # assert "test" in response.text
    # assert "aston" in response.text



"""def test_login():
    response = client.get("/auth/login")
    assert response.status_code == 200
"""
# create an account page
"""def test_create_account():
    response = client.get("/create")
    assert response.status_code == 200
"""


# create review pages
def test_argo_leave_review():
    response = client.get("/createR/argoLeaveReview")
    assert response.status_code == 200


def test_market_leave_review():
    response = client.get("/createR/marketLeaveReview")
    assert response.status_code == 200


def test_mills_leave_review():
    response = client.get("/createR/millsLeaveReview")
    assert response.status_code == 200


def test_seasons_leave_review():
    response = client.get("/createR/seasonsLeaveReview")
    assert response.status_code == 200


def test_wils_leave_review():
    response = client.get("createR/wilsLeaveReview")
    assert response.status_code == 200


# create user


# create review


def test_create_review(client: TestClient, session: Session):
    # Create user

    location = Location(name="Dining Hall")
    session.add(location)
    session.commit()
    session.refresh(location)
    location_id = location.location_id

    # Prepare review data
    review_data = {"meal": "lunch", "stars": 3, "content": "body", "location_id": location_id, "author": "test"}

    response = client.post("/reviewcreate", data=review_data, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/menu"

    # Check if review was created
    # review = session.exec(select(Review).where(Review.author_id == user_id)).first()

    review = session.exec(select(Review).where(Review.location_id == location_id)).first()
    # Validate review details
    assert review is not None  # and review.review_id is not None
    assert review.title == "lunch"
    assert review.rating == 3
    assert review.body == "body"
    assert review.location_id == location_id
    assert review.nickname == "test"


# Home menu page


def test_all_reviews(session: Session, client: TestClient):
    # users
    """user1_data = {"username": "test", "password": "test password"}
    user1 = User(**user1_data)

    user2_data = {"username": "aston", "password": "test"}
    user2 = User(**user2_data)

    session.add(user1)
    session.add(user2)
    session.commit()
    """
    # locations
    location1 = Location(name="test lo")
    location2 = Location(name="dining hall")
    session.add(location1)
    session.add(location2)
    session.commit()

    # reviews
    review1_data = {
        # "author_id": user1.user_id,
        "location_id": location1.location_id,
        "rating": 3,
        "title": "Food",
        "body": "Great food",
        "nickname": "test",
    }
    review2_data = {
        # "author_id": user2.user_id,
        "location_id": location2.location_id,
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

    assert "Food" in response.text
    assert "chicken" in response.text
    assert "test" in response.text
    assert "test2" in response.text
    # assert "test" in response.text
    # assert "aston" in response.text


# Review Pages
def test_argo_review(client: TestClient, session: Session):
    """user_data = {"username": "test", "password": "testp"}
    user = User(**user_data)

    session.add(user)
    session.commit()"""

    location = Location(location_id=1, name="Argo Tea")
    session.add(location)
    session.commit()

    review_data = {  # "author_id": user.user_id,
        "location_id": location.location_id,
        "rating": 5,
        "title": "Croissant",
        "body": "Fantastic food",
        "nickname": "test",
    }

    review = Review(**review_data)
    session.add(review)
    session.commit()

    response = client.get("/reviewP/argoReview")

    assert response.status_code == 200
    assert "Croissant" in response.text
    assert "test" in response.text
    assert "Fantastic food" in response.text


def test_market_review(client: TestClient, session: Session):
    """user_data = {"username": "test", "password": "testp"}
    user = User(**user_data)

    session.add(user)
    session.commit()"""

    location = Location(location_id=2, name="Mills Marketplace")
    session.add(location)
    session.commit()

    review_data = {  # "author_id": user.user_id,
        "location_id": location.location_id,
        "rating": 5,
        "title": "Croissant",
        "body": "Fantastic food",
        "nickname": "test",
    }

    review = Review(**review_data)
    session.add(review)
    session.commit()

    response = client.get("/reviewP/marketReview")

    assert response.status_code == 200
    assert "Croissant" in response.text
    assert "test" in response.text
    assert "Fantastic food" in response.text


def test_mills_review(client: TestClient, session: Session):
    """user_data = {"username": "test", "password": "testp"}
    user = User(**user_data)

    session.add(user)
    session.commit()"""

    location = Location(location_id=3, name="Mills Dining Hall")
    session.add(location)
    session.commit()

    review_data = {  # "author_id": user.user_id,
        "location_id": location.location_id,
        "rating": 5,
        "title": "Croissant",
        "body": "Fantastic food",
        "nickname": "test",
    }

    review = Review(**review_data)
    session.add(review)
    session.commit()

    response = client.get("/reviewP/millsReview")

    assert response.status_code == 200
    assert "Croissant" in response.text
    assert "test" in response.text
    assert "Fantastic food" in response.text


def test_seasons_review(client: TestClient, session: Session):
    """user_data = {"username": "test", "password": "testp"}
    user = User(**user_data)

    session.add(user)
    session.commit()
    """
    location = Location(location_id=4, name="Seasons")
    session.add(location)
    session.commit()

    review_data = {  # "author_id": user.user_id,
        "location_id": location.location_id,
        "rating": 5,
        "title": "Croissant",
        "body": "Fantastic food",
        "nickname": "test",
    }

    review = Review(**review_data)
    session.add(review)
    session.commit()

    response = client.get("/reviewP/seasonsReview")

    assert response.status_code == 200
    assert "Croissant" in response.text
    assert "test" in response.text
    assert "Fantastic food" in response.text


def test_wils_review(client: TestClient, session: Session):
    """user_data = {"username": "test", "password": "testp"}
    user = User(**user_data)

    session.add(user)
    session.commit()
    """
    location = Location(location_id=5, name="Wilsbach Dining Hall")
    session.add(location)
    session.commit()

    review_data = {  # "author_id": user.user_id, using this in the future
        "location_id": location.location_id,
        "rating": 5,
        "title": "Croissant",
        "body": "Fantastic food",
        "nickname": "test",
    }

    review = Review(**review_data)
    session.add(review)
    session.commit()

    response = client.get("/reviewP/wilsReview")

    assert response.status_code == 200
    assert "Croissant" in response.text
    assert "test" in response.text
    assert "Fantastic food" in response.text
