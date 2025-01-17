# trying to incorporate fastapi into the project.

import os  # noqa
import jwt  # noqa
from fastapi import FastAPI, Request, Query, Depends, Form, HTTPException, status  # noqa: F401
from fastapi.responses import HTMLResponse, RedirectResponse  # noqa
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta, timezone  # noqa
from pydantic import BaseModel  # noqa: F401
from sqlmodel import SQLModel, Field, create_engine, Session, Relationship, select  # noqa: F401
from passlib.context import CryptContext  # noqa: F401
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

app = FastAPI()
app.mount("/static", StaticFiles(directory="py_src/static"), name="static")
templates = Jinja2Templates(directory="py_src/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")
SECRET_KEY = "af842c14eb50cd7009202a3cdf0948122a325bed0f8fc4596035f8208fe57d9c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password: str = Field(nullable=False)
    reviews: list["Review"] = Relationship(back_populates="author")


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    review_id: int | None = Field(default=None, primary_key=True)
    author_id: int = Field(nullable=False, foreign_key="users.user_id")
    location_id: int = Field(nullable=False, foreign_key="locations.location_id")
    title: str = Field(nullable=False)
    body: str = Field(nullable=False)
    rating: int = Field(nullable=False)
    # timestamps
    # created: datetime = Field(nullable=False) Field(sa_column=Column(TIMESTAMP(timezone=True),
    # nullable=False, server_default=text("now()")))
    # link values
    author: "User" = Relationship(back_populates="reviews")
    location: "Location" = Relationship(back_populates="reviews")


class Location(SQLModel, table=True):
    __tablename__ = "locations"

    location_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None, nullable=False, index=True)
    reviews: list["Review"] = Relationship(back_populates="location")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# creates the entire db + tables, adds locations values.
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# for has passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# hashed pwd
def get_hashpwd(password):
    return pwd_context.hash(password)


def get_user(db: Session = Depends(get_session), username: str = None):
    return db.exec(select(User).where(User.username == username)).first()


def verify_password(plain_password, hashed_pwd):
    return pwd_context.verify(plain_password, hashed_pwd)


def authenticate_user(
    db: Session = Depends(get_session), username: str = None, password: str = None
):
    user = get_user(db, username)
    if not user:
        return False  # error or something of the sort.
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    encode.update({"exp": expire})
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/signin", response_model=Token)
async def signin(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/menu", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


"""@app.get("/signin", response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request})
"""


@app.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session),
):
    old_user = db.exec(select(User).where(User.username == username)).first()
    # checking if username already exists. -- Figure out how to send this to another page when the user already exists.
    if old_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
        # password with hash
    hashed_pwd = pwd_context.hash(password)
    new_user = User(username=username, password=hashed_pwd)
    # new_user = User(username=username, password=password) #without hash
    db.add(new_user)
    db.commit()

    return RedirectResponse(url="auth/login", status_code=303)


# attempting to create a proper link to the right review page depending on what the user clicks.
# needs an an author parameter as well
# this works need to figure out how to update user_id
@app.post("/reviewcreate")
async def createreview(
    meal: str = Form(...),
    stars: int = Form(...),
    content: str = Form(...),
    location_id: int = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_session),
):
    review = Review(
        title=meal,
        rating=stars,
        body=content,
        location_id=location_id,
        author_id=user_id,
    )

    db.add(review)

    db.commit()

    return RedirectResponse(url="/menu", status_code=303)


# adds location values for the location Table
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


sqlite_db_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_db_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


@app.on_event("startup")
def startup():
    create_db_and_tables()
    # inserts the locations only once.
    with Session(engine) as session:
        location_exists = session.exec(select(Location)).first()
        if not location_exists:
            create_locations()


# routes!
@app.get("/", response_class=HTMLResponse)
async def test(request: Request, q: str = Query(default="No Query")):
    return templates.TemplateResponse("auth/login.html", {"request": request, "q": q})


@app.get("/auth/login", response_class=HTMLResponse)
async def login(request: Request, q: None = None):
    return templates.TemplateResponse("auth/login.html", {"request": request, "q": q})


"""@app.get("/menu", response_class=HTMLResponse)
async def main(request: Request, q: None = None):
    return templates.TemplateResponse("menu.html", {"request": request, "q": q})
"""


@app.get("/create", response_class=HTMLResponse)
async def create(request: Request, q: None = None):
    return templates.TemplateResponse("auth/create.html", {"request": request, "q": q})


@app.get("/map", response_class=HTMLResponse)
async def map(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})


# createR is the route for the leave review pages
@app.get("/createR/argoLeaveReview", response_class=HTMLResponse)
async def argoLeave(request: Request):
    return templates.TemplateResponse(
        "createR/argoLeaveReview.html", {"request": request}
    )


@app.get("/createR/marketLeaveReview", response_class=HTMLResponse)
async def marketLeave(request: Request):
    return templates.TemplateResponse(
        "createR/marketLeaveReview.html", {"request": request}
    )


@app.get("/createR/millsLeaveReview", response_class=HTMLResponse)
async def millsLeave(request: Request):
    return templates.TemplateResponse(
        "createR/millsLeaveReview.html", {"request": request}
    )


@app.get("/createR/seasonsLeaveReview", response_class=HTMLResponse)
async def seasonsLeave(request: Request):
    return templates.TemplateResponse(
        "createR/seasonsLeaveReview.html", {"request": request}
    )


@app.get("/createR/wilsLeaveReview", response_class=HTMLResponse)
async def wilsLeave(request: Request):
    return templates.TemplateResponse(
        "createR/wilsLeaveReview.html", {"request": request}
    )


# reviewP is the route for the entire review pages
@app.get("/menu", response_class=HTMLResponse)
async def allreviews(request: Request, db: Session = Depends(get_session)):
    reviews = db.exec(
        select(Review, User, Location)
        .join(User, Review.author_id == User.user_id)
        .join(Location, Review.location_id == Location.location_id)
    ).all()
    allreviews = []
    for review, user, location in reviews:
        allreviews.append(
            { 
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                "author": user.username,
                "location": location.name,
            }
        )
    return templates.TemplateResponse(
        "menu.html", {"request": request, "reviews": allreviews}
    )


@app.get("/reviewP/argoReview", response_class=HTMLResponse)
async def argoReview(request: Request, db: Session = Depends(get_session)):
    reviews = db.exec(
        select(Review, User)
        .join(User, Review.author_id == User.user_id)
        .where(Review.location_id == 1)
    ).all()

    newreview = []
    for review, user in reviews:
        newreview.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                "author": user.username,
            }
        )
    return templates.TemplateResponse(
        "reviewP/argoReviewPage.html", {"request": request, "reviews": newreview}
    )


@app.get("/reviewP/marketReview", response_class=HTMLResponse)
async def marketReview(request: Request, db: Session = Depends(get_session)):
    reviews = db.exec(
        select(Review, User)
        .join(User, Review.author_id == User.user_id)
        .where(Review.location_id == 2)
    ).all()

    newreview = []
    for review, user in reviews:
        newreview.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                "author": user.username,
            }
        )
    return templates.TemplateResponse(
        "reviewP/marketReviewPage.html", {"request": request, "reviews": newreview}
    )


@app.get("/reviewP/millsReview", response_class=HTMLResponse)
async def millsReview(request: Request, db: Session = Depends(get_session)):
    reviews = db.exec(
        select(Review, User)
        .join(User, Review.author_id == User.user_id)
        .where(Review.location_id == 3)
    ).all()

    newreview = []
    for review, user in reviews:
        newreview.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                "author": user.username,
            }
        )
    return templates.TemplateResponse(
        "reviewP/millsReviewPage.html", {"request": request, "reviews": newreview}
    )


@app.get("/reviewP/seasonsReview", response_class=HTMLResponse)
async def seasonsReview(request: Request, db: Session = Depends(get_session)):
    reviews = db.exec(
        select(Review, User)
        .join(User, Review.author_id == User.user_id)
        .where(Review.location_id == 4)
    ).all()

    newreview = []
    for review, user in reviews:
        newreview.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                "author": user.username,
            }
        )
    return templates.TemplateResponse(
        "reviewP/seasonsReviewPage.html", {"request": request, "reviews": newreview}
    )


@app.get("/reviewP/wilsReview", response_class=HTMLResponse)
async def wilsReview(request: Request, db: Session = Depends(get_session)):
    reviews = db.exec(
        select(Review, User)
        .join(User, Review.author_id == User.user_id)
        .where(Review.location_id == 5)
    ).all()

    newreview = []
    for review, user in reviews:
        newreview.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                "author": user.username,
            }
        )
    return templates.TemplateResponse(
        "reviewP/wilsReviewPage.html", {"request": request, "reviews": newreview}
    )
