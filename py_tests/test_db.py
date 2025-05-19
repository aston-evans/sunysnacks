import pytest
from snacks.db import Location
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


def test_create_db_and_tables(session: Session):
    location = Location(location_id="test", name="Test Location")
    session.add(location)
    session.commit()

    result = session.exec(select(Location)).first()
    assert result is not None
    assert result.name == "Test Location"


def test_create_locations(session: Session):
    # Create locations in the test database
    location_1 = Location(location_id="argo", name="Argo Tea")
    location_2 = Location(location_id="marketplace", name="Mills Marketplace")
    location_3 = Location(location_id="mills", name="Mills Dining Hall")
    location_4 = Location(location_id="seasons", name="Seasons")
    location_5 = Location(location_id="wilsbach", name="Wilsbach Dining Hall")

    session.add(location_1)
    session.add(location_2)
    session.add(location_3)
    session.add(location_4)
    session.add(location_5)
    session.commit()

    # Query all locations
    locations = session.exec(select(Location)).all()

    # Check if all 5 locations were created
    assert len(locations) == 5

    # Verify the names of locations
    location_names = {loc.name for loc in locations}
    expected_names = {
        "Argo Tea",
        "Mills Marketplace",
        "Mills Dining Hall",
        "Seasons",
        "Wilsbach Dining Hall",
    }
    assert location_names == expected_names


def test_init_locations_with_existing(session: Session):
    # First create some locations
    location = Location(location_id="argo", name="Argo Tea")
    session.add(location)
    session.commit()

    # Now try to initialize locations
    init_locations(session)

    # Should still have same location, not duplicated
    locations = session.exec(select(Location).where(Location.name == "Argo Tea")).all()
    assert len(locations) == 1  # No duplicates


def test_engine_session():
    # Create a test engine
    test_engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(test_engine)

    # Import and temporarily replace the engine
    import snacks.db

    old_engine = snacks.db.engine
    snacks.db.engine = test_engine

    try:
        # Run startup
        from snacks.db import startup

        startup()

        # Check if locations were created
        with Session(test_engine) as session:
            locations = session.exec(select(Location)).all()
            assert len(locations) == 5

            # Run startup again (should not create duplicates)
            startup()
            locations = session.exec(select(Location)).all()
            assert len(locations) == 5
    finally:
        # Restore the original engine
        snacks.db.engine = old_engine
        SQLModel.metadata.drop_all(test_engine)


def test_get_session():
    # Import the session generator
    from snacks.db import get_session

    # Test the session generator
    session_gen = get_session()
    session = next(session_gen)

    # Verify we can use the session
    location = Location(location_id="test", name="Test Through Session")
    session.add(location)
    session.commit()

    # Query to verify
    result = session.exec(
        select(Location).where(Location.name == "Test Through Session")
    ).first()
    assert result is not None
    assert result.name == "Test Through Session"

    # Clean up - this would normally be handled by FastAPI
    try:
        next(session_gen)
    except StopIteration:
        pass  # Expected - generator should be done
