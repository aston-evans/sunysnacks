import json
import os
import urllib.parse
from typing import Optional
from fastapi import HTTPException
import typer
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Locations(SQLModel, table=True):
    __tablename__ = "Locations"
    location_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: str
    latitude: float
    longitude: float
    image_filename: str


class LocationHours(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="Locations.location_id")
    day_type: str  # 'weekdays', 'friday', 'saturday', 'sunday'
    hours: str


class LocationLinks(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="Locations.location_id")
    link_type: str  # 'menu', 'instagram', 'android_app', 'ios_app'
    url: str


class Reviews(SQLModel, table=True):
    __tablename__ = "Reviews"
    review_id: Optional[int] = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="Locations.location_id")
    title: str
    body: str
    rating: int
    nickname: str


# Database setup
database_url = os.getenv("DATABASE_URL", "sqlite:///database.db")
engine = create_engine(database_url, echo=True)


'''def create_db_and_tables():
    """Create database tables if they don't exist"""
    SQLModel.metadata.create_all(engine)
'''


def get_session():
    """Get a database session"""
    with Session(engine) as session:
        yield session


app = FastAPI()

app.mount("/static", StaticFiles(directory="py_src/static"), name="static")
templates = Jinja2Templates(directory="py_src/templates")


def create_db(
    db_path: str = ":memory:",
    schema_path: str = "py_src/create_schema.sql",
    json_path: str = None,
):
    """Create a test database with schema and optionally populate it with data from JSON.

    Args:
        db_path: Path to SQLite database (use ":memory:" for in-memory DB)
        schema_path: Path to SQL schema file
        json_path: Optional path to JSON data file for populating the DB

    Returns:
        SQLModel engine for the test database
    """
    import sqlite3

    from sqlmodel import create_engine

    # Create database from schema
    if db_path != ":memory:":
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    # Create DB and apply schema
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()

    # Create SQLModel engine
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )

    # Optionally populate with data
    if json_path:
        with Session(engine) as session:
            with open(json_path, "r") as f:
                data = json.load(f)

            # Process locations
            # print(f"Populating database with {len(data)} locations from {json_path}")
            for loc_id, loc_data in data.items():
                # Create location
                location = Locations(
                    name=loc_data["name"],
                    description=loc_data["description"],
                    latitude=loc_data["coordinates"]["lat"],
                    longitude=loc_data["coordinates"]["lng"],
                    image_filename=loc_data["image"],
                )
                session.add(location)
                session.flush()  # Get the newly assigned ID

                # Add hours
                for day_type, hours in loc_data["hours"].items():
                    session.add(
                        LocationHours(
                            location_id=location.location_id,
                            day_type=day_type,
                            hours=hours,
                        )
                    )

                # Add links
                for link_type, url in loc_data["links"].items():
                    if link_type == "getApp":
                        # Handle nested app links
                        if "android" in url:
                            session.add(
                                LocationLinks(
                                    location_id=location.location_id,
                                    link_type="getApp_android",
                                    url=url["android"],
                                )
                            )
                        if "ios" in url:
                            session.add(
                                LocationLinks(
                                    location_id=location.location_id,
                                    link_type="getApp_ios",
                                    url=url["ios"],
                                )
                            )
                    else:
                        session.add(
                            LocationLinks(
                                location_id=location.location_id,
                                link_type=link_type,
                                url=url,
                            )
                        )

            session.commit()

    return engine


def init_locations(db: Session):
    """Initialize the database with default location data"""
    # Default location data
    locations_data = {
        "argo": {
            "name": "Argo Tea",
            "description": "Argo Tea offers a selection of specialty teas, coffee, and light snacks. Perfect for a quick beverage or study break.",
            "latitude": 42.467861,
            "longitude": -75.062069,
            "image_filename": "ArgoTea.jpg",
            "hours": {
                "weekdays": "7:30 AM - 8:00 PM",
                "friday": "7:30 AM - 7:00 PM",
                "saturday": "Closed",
                "sunday": "Closed",
            },
            "links": {
                "menu": "https://oneonta.sodexomyway.com/en-us/locations/argo-tea",
                "instagram": "https://www.instagram.com/SUNYONEYDINING/",
                "getApp": {
                    "android": "https://play.google.com/store/apps/details?id=com.cbord.get",
                    "ios": "https://apps.apple.com/us/app/get-mobile/id844091049",
                },
            },
        },
        "marketplace": {
            "name": "Mills Marketplace",
            "description": "The Marketplace is a place where you can get your groceries. It has a variety of snacks, canned goods, and beverages available. The marketplace has a sweet pizza place, sandwich spot, and fresh sushi rolls available if you need to get a quick bite.",
            "latitude": 42.468741,
            "longitude": -75.060596,
            "image_filename": "millsmarketplace.jpg",
            "hours": {
                "weekdays": "11:00 AM - 1:00 AM",
                "friday": "11:00 AM - 1:00 AM",
                "saturday": "11:00 AM - 1:00 AM",
                "sunday": "11:00 AM - 1:00 AM",
            },
            "links": {
                "menu": "https://oneonta.sodexomyway.com/en-us/locations/mills-marketplace",
                "instagram": "https://www.instagram.com/SUNYONEYDINING/",
                "getApp": {
                    "android": "https://play.google.com/store/apps/details?id=com.cbord.get",
                    "ios": "https://apps.apple.com/us/app/get-mobile/id844091049",
                },
            },
        },
        "mills": {
            "name": "Mills Dining Hall",
            "description": "Mills Dining Hall offers a range of meal options including hot entrees, salad bar, and made-to-order stations. The hall provides a comfortable dining environment for students with diverse dietary needs.",
            "latitude": 42.468741,
            "longitude": -75.060596,
            "image_filename": "millsmarketplace.jpg",
            "hours": {
                "weekdays": "7:30 AM - 8:00 PM",
                "friday": "7:30 AM - 7:00 PM",
                "saturday": "10:00 AM - 7:00 PM",
                "sunday": "10:00 AM - 8:00 PM",
            },
            "links": {
                "menu": "https://oneonta.sodexomyway.com/en-us/locations/mills",
                "instagram": "https://www.instagram.com/SUNYONEYDINING/",
                "getApp": {
                    "android": "https://play.google.com/store/apps/details?id=com.cbord.get",
                    "ios": "https://apps.apple.com/us/app/get-mobile/id844091049",
                },
            },
        },
        "wilsbach": {
            "name": "Wilsbach Dining Hall",
            "description": "Wilsbach Dining Hall contains more of the breakfast foods, from cereal to omelets to waffles. For dinner the option of pasta, pizza, vegan food, or an organic meal.",
            "latitude": 42.468781,
            "longitude": -75.060411,
            "image_filename": "wilsbachdininghall.jpg",
            "hours": {
                "weekdays": "7:30 AM - 8:00 PM",
                "friday": "7:30 AM - 7:00 PM",
                "saturday": "9:00 AM - 7:00 PM",
                "sunday": "9:00 AM - 8:00 PM",
            },
            "links": {
                "menu": "https://oneonta.sodexomyway.com/en-us/locations/wilsbach",
                "instagram": "https://www.instagram.com/SUNYONEYDINING/",
                "getApp": {
                    "android": "https://play.google.com/store/apps/details?id=com.cbord.get",
                    "ios": "https://apps.apple.com/us/app/get-mobile/id844091049",
                },
            },
        },
        "seasons": {
            "name": "Seasons",
            "description": "Seasons offers a diverse menu with rotating options throughout the week. Features include a salad bar, grill station, and daily specials.",
            "latitude": 42.470332,
            "longitude": -75.062667,
            "image_filename": "seasons.jpg",
            "hours": {
                "weekdays": "7:30 AM - 8:00 PM",
                "friday": "7:30 AM - 7:00 PM",
                "saturday": "10:00 AM - 7:00 PM",
                "sunday": "10:00 AM - 8:00 PM",
            },
            "links": {
                "menu": "https://oneonta.sodexomyway.com/en-us/locations/seasons",
                "instagram": "https://www.instagram.com/SUNYONEYDINING/",
                "getApp": {
                    "android": "https://play.google.com/store/apps/details?id=com.cbord.get",
                    "ios": "https://apps.apple.com/us/app/get-mobile/id844091049",
                },
            },
        },
    }

    for location_id, data in locations_data.items():
        existing = db.exec(
            select(Locations).where(Locations.name == data["name"])
        ).first()

        if existing:
            continue

        # Create new location
        location = Locations(
            name=data["name"],
            description=data["description"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            image_filename=data["image_filename"],
        )
        db.add(location)
        db.commit()
        db.refresh(location)

        # Add hours
        for day_type, hours in data["hours"].items():
            hours_record = LocationHours(
                location_id=location.location_id, day_type=day_type, hours=hours
            )
            db.add(hours_record)

        # Add links
        for link_type, url in data["links"].items():
            if isinstance(url, dict):  # Handle nested getApp links
                for app_type, app_url in url.items():
                    link_record = LocationLinks(
                        location_id=location.location_id,
                        link_type=f"{link_type}_{app_type}",
                        url=app_url,
                    )
                    db.add(link_record)
            else:
                link_record = LocationLinks(
                    location_id=location.location_id, link_type=link_type, url=url
                )
                db.add(link_record)

        db.commit()

# Data access and formatting utilities for retrieving and preparing
# location, hours, links, and reviews for use in route logic

def get_location(db: Session, location_id: int):
    location = db.exec(select(Locations).where(Locations.location_id == location_id)).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

def get_location_hours(db: Session, location_id: int):
    return db.exec(select(LocationHours).where(LocationHours.location_id == location_id)).all()

def get_location_links(db: Session, location_id: int):
    return db.exec(select(LocationLinks).where(LocationLinks.location_id == location_id)).all()

def get_reviews_for_location(db: Session, location_id: int):
    return db.exec(select(Reviews).where(Reviews.location_id == location_id)).all()

def format_links(links):
    link_data = {}
    for link in links:
        if link.link_type == "menu":
            link_data["menu"] = link.url
        elif link.link_type == "instagram":
            link_data["instagram"] = link.url
        elif link.link_type == "getApp_android":
            link_data.setdefault("getApp", {})["android"] = link.url
        elif link.link_type == "getApp_ios":
            link_data.setdefault("getApp", {})["ios"] = link.url
    return link_data

def build_location_data(location, hours, links, map_url=None):
    data = {
        "id": location.location_id,
        "name": location.name,
        "description": location.description,
        "coordinates": {"lat": location.latitude, "lng": location.longitude},
        "hours": {h.day_type: h.hours for h in hours},
        "links": format_links(links),
        "image": location.image_filename,
    }
    if map_url:
        data["map_url"] = map_url
    return data

def get_all_locations(db: Session):
    return db.exec(select(Locations)).all()

# Logic to retrieve all locations and their summaries
def get_full_location_summaries(db: Session):
    locations = get_all_locations(db)
    summaries = []

    for location in locations:
        hours = get_location_hours(db, location.location_id)
        links = get_location_links(db, location.location_id)
        summaries.append(build_location_data(location, hours, links))

    return summaries


#logic to create a review
def validate_rating(rating: int):
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=422, detail="Rating must be between 1 and 5")

def verify_location_exists(db: Session, location_id: int):
    location = db.exec(select(Locations).where(Locations.location_id == location_id)).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

def create_review_in_db(
    db: Session,
    title: str,
    rating: int,
    body: str,
    location_id: int,
    nickname: str,
):
    review = Reviews(
        title=title,
        rating=rating,
        body=body,
        location_id=location_id,
        nickname=nickname,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review



# Create the CLI app
cli = typer.Typer(help="SunySnacks database management CLI")


@cli.command()
def init_db(
    db_path: str = typer.Option("database.db", help="Path to SQLite database"),
    schema_path: str = typer.Option(
        "py_src/create_schema.sql", help="Path to SQL schema file"
    ),
    json_path: str = typer.Option(
        "locations_init.json", help="Path to locations JSON file"
    ),
):
    """Initialize the database with schema and data."""
    _ = create_db(db_path, schema_path, json_path)
    print(f"Database initialized at {db_path}")


@cli.command()
def reset_db(
    db_path: str = typer.Option("database.db", help="Path to SQLite database"),
    schema_path: str = typer.Option(
        "py_src/create_schema.sql", help="Path to SQL schema file"
    ),
):
    """Reset the database by deleting it and recreating the schema without data."""
    # Delete existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted existing database at {db_path}")

    # Create new database with schema only
    # _ = create_db(db_path, schema_path, json_path=None)
    # print(f"Database reset with empty schema at {db_path}")


@cli.command()
def export_db(
    db_path: str = typer.Option("database.db", help="Path to SQLite database"),
    output_path: str = typer.Option(
        "locations_export.json", help="Path to output JSON file"
    ),
):
    """Export locations data from database to JSON."""
    from sqlmodel import Session, create_engine, select

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        # Get all locations with their hours and links
        locations_data = {}

        locations = session.exec(select(Locations)).all()

        for location in locations:
            # Get hours and links
            hours = session.exec(
                select(LocationHours).where(
                    LocationHours.location_id == location.location_id
                )
            ).all()

            links = session.exec(
                select(LocationLinks).where(
                    LocationLinks.location_id == location.location_id
                )
            ).all()

            # Build hours dict
            hours_dict = {}
            for h in hours:
                hours_dict[h.day_type] = h.hours

            # Build links dict with special handling for app links
            links_dict = {}
            for link in links:
                if link.link_type == "getApp_android" or link.link_type == "getApp_ios":
                    if "getApp" not in links_dict:
                        links_dict["getApp"] = {}

                    if link.link_type == "getApp_android":
                        links_dict["getApp"]["android"] = link.url
                    else:
                        links_dict["getApp"]["ios"] = link.url
                else:
                    links_dict[link.link_type] = link.url

            # Create location entry
            location_key = f"loc_{location.location_id}"  # Create a string key
            locations_data[location_key] = {
                "name": location.name,
                "description": location.description,
                "coordinates": {"lat": location.latitude, "lng": location.longitude},
                "hours": hours_dict,
                "links": links_dict,
                "image": location.image_filename,
            }

        # Write to JSON file
        with open(output_path, "w") as f:
            json.dump(locations_data, f, indent=2)

        print(f"Exported {len(locations_data)} locations to {output_path}")


if __name__ == "__main__":
    cli()
