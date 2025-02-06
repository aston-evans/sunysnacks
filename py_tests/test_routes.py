import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from snacks.db import get_session, User, Review, Location #noqa 
from fastapi import Depends 
from snacks.main import app
from sqlmodel.pool import StaticPool

client = TestClient(app)
#login pages
def test_root(): 
    response = client.get("/")
    assert response.status_code == 200
    
    
def test_login():
    response = client.get("/auth/login")
    assert response.status_code == 200
    
#create an account page
def test_create_account():
    response = client.get("/create")
    assert response.status_code == 200
    
#create review pages 
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

#create user
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


#function did not pass. 
def test_register(client: TestClient):
    response = client.post(
        "/register", data={"username": "aston", 
                           "password": "test"}
    )
    assert response.status_code == 202
    assert response.headers["location"] == "auth/login"
    
    


#create review



#Home menu page

def test_all_reviews(db: Session = Depends(get_session)):
    response = client.get("/menu")
    assert response.status_code == 200 


#Review Pages



