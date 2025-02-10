import os #noqa
from sqlmodel import SQLModel, Field, create_engine, Session, Relationship, select
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI()

@app.on_event("startup")
def startup():
    create_db_and_tables()
    # Insert default locations if they don’t exist
    with Session(engine) as session:
        location_exists = session.exec(select(Location)).first()
        if not location_exists:
            create_locations()





app.mount("/static", StaticFiles(directory="py_src/static"), name="static")
templates = Jinja2Templates(directory="py_src/templates")


# to be used in future versions
"""class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password: str = Field(nullable=False)
    reviews: list["Review"] = Relationship(back_populates="author")
"""


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    review_id: int | None = Field(default=None, primary_key=True)
    # author_id: int = Field(nullable=False, foreign_key="users.user_id")
    location_id: int = Field(nullable=False, foreign_key="locations.location_id")
    title: str = Field(nullable=False)
    body: str = Field(nullable=False)
    rating: int = Field(nullable=False)
    # timestamps
    # created: datetime = Field(nullable=False) Field(sa_column=Column(TIMESTAMP(timezone=True),
    # nullable=False, server_default=text("now()")))
    # link values
    # author: "User" = Relationship(back_populates="reviews") future for linking
    location: "Location" = Relationship(back_populates="reviews")
    nickname: str = Field(nullable=False)


class Location(SQLModel, table=True):
    __tablename__ = "locations"

    location_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None, nullable=False, index=True)
    reviews: list["Review"] = Relationship(back_populates="location")


sqlite_db_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_db_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_locations():
    location_1 = Location(name="Argo Tea")
    location_2 = Location(name="Mills Marketplace")
    location_3 = Location(name="Mills Dining Hall")
    location_4 = Location(name="Seasons")
    location_5 = Location(name="Wilsbach Dining Hall")

    with Session(engine) as session:
        session.add(location_1)
        session.add(location_2)
        session.add(location_3)
        session.add(location_4)
        session.add(location_5)
        session.commit()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
