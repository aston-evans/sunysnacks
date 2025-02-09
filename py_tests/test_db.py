import pytest
from sqlmodel import inspect, SQLModel, Session, select
from snacks.db import create_db_and_tables, engine, Location, create_locations


@pytest.fixture(name="session")
def session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


def test_create_db_and_tables(session):
    create_db_and_tables()
    check = inspect(engine)
    tables = check.get_table_names()
    # assert "users" in tables
    assert "locations" in tables
    assert "reviews" in tables


def test_create_locations(session):
    create_locations()
    check = inspect(engine)
    table = check.get_table_names()
    assert "locations" in table
    with session as db:
        col1 = db.exec(select(Location).where(Location.name == "Argo Tea")).first()
        col2 = db.exec(select(Location).where(Location.name == "Mills Marketplace")).first()
        col3 = db.exec(select(Location).where(Location.name == "Mills Dining Hall")).first()
        col4 = db.exec(select(Location).where(Location.name == "Seasons")).first()
        col5 = db.exec(select(Location).where(Location.name == "Wilsbach Dining Hall")).first()

        assert col1.name == "Argo Tea"
        assert col2.name == "Mills Marketplace"
        assert col3.name == "Mills Dining Hall"
        assert col4.name == "Seasons"
        assert col5.name == "Wilsbach Dining Hall"
