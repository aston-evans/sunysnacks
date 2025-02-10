# adding user info in the future
import random
from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse
from snacks.db import Review, Location, get_session, templates  # noqa
from sqlmodel import Session, select

from fastapi.responses import RedirectResponse
from fastapi import Depends, HTTPException, status, Form  # noqa
# from snacks.users import pwd_context


router = APIRouter()


# routes! Change each app. to routes
@router.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_session)):
    # Query to fetch reviews and associated location information
    reviews = db.exec(select(Review, Location).join(Location, Review.location_id == Location.location_id)).all()

    allreviews = []
    for review, location in reviews:
        allreviews.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                "location": location.name,
                "nickname": review.nickname,
            }
        )
    random.shuffle(allreviews)

    # Pass the transformed `allreviews` list to the template
    return templates.TemplateResponse("menu.html", {"request": request, "reviews": allreviews})
'''@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request})
'''

"""@router.get("/auth/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})



@router.get("/create", response_class=HTMLResponse)
async def create_account(request: Request, q: None = None):
    return templates.TemplateResponse("auth/create.html", {"request": request, "q": q})
"""


# createR is the route for the leave review pages
@router.get("/createR/argoLeaveReview", response_class=HTMLResponse)
async def argo_leave_review(request: Request):
    return templates.TemplateResponse("createR/argoLeaveReview.html", {"request": request})


@router.get("/createR/marketLeaveReview", response_class=HTMLResponse)
async def market_leave_review(request: Request):
    return templates.TemplateResponse("createR/marketLeaveReview.html", {"request": request})


@router.get("/createR/millsLeaveReview", response_class=HTMLResponse)
async def mills_leave_review(request: Request):
    return templates.TemplateResponse("createR/millsLeaveReview.html", {"request": request})


@router.get("/createR/seasonsLeaveReview", response_class=HTMLResponse)
async def seasons_leave_review(request: Request):
    return templates.TemplateResponse("createR/seasonsLeaveReview.html", {"request": request})


@router.get("/createR/wilsLeaveReview", response_class=HTMLResponse)
async def wils_leave_review(request: Request):
    return templates.TemplateResponse("createR/wilsLeaveReview.html", {"request": request})


@router.get("/menu", response_class=HTMLResponse)
async def menu(request: Request, db: Session = Depends(get_session)):
    # Query to fetch reviews and associated location information
    reviews = db.exec(select(Review, Location).join(Location, Review.location_id == Location.location_id)).all()

    allreviews = []
    for review, location in reviews:
        allreviews.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                "location": location.name,
                "nickname": review.nickname,
            }
        )
    random.shuffle(allreviews)

    # Pass the transformed `allreviews` list to the template
    return templates.TemplateResponse("menu.html", {"request": request, "reviews": allreviews})


@router.get("/reviewP/argoReview", response_class=HTMLResponse)
async def argo_review(request: Request, db: Session = Depends(get_session)):
    reviews = db.exec(
        select(Review)  # select(Review, User)
        # .join(User, Review.author_id == User.user_id)
        .where(Review.location_id == 1)
    ).all()

    newreview = []
    for review in reviews:  # for review, user in reviews
        newreview.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                # "author": user.username,
                "nickname": review.nickname,
            }
        )
    return templates.TemplateResponse("reviewP/argoReviewPage.html", {"request": request, "reviews": newreview})


@router.get("/reviewP/marketReview", response_class=HTMLResponse)
async def market_review(request: Request, db: Session = Depends(get_session)):
    reviews = db.exec(
        select(
            Review,
        )  # select(Review, User)
        # .join(User, Review.author_id == User.user_id)
        .where(Review.location_id == 2)
    ).all()

    newreview = []
    for review in reviews:  # for review, user in reviews
        newreview.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                # "author": user.username,
                "nickname": review.nickname,
            }
        )
    return templates.TemplateResponse("reviewP/marketReviewPage.html", {"request": request, "reviews": newreview})


@router.get("/reviewP/millsReview", response_class=HTMLResponse)
async def mills_review(request: Request, db: Session = Depends(get_session)):
    reviews = db.exec(
        select(Review)  # select(Review, User)
        # .join(User, Review.author_id == User.user_id)
        .where(Review.location_id == 3)
    ).all()

    newreview = []
    for review in reviews:  # for review, user in reviews
        newreview.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                # "author": user.username,
                "nickname": review.nickname,
            }
        )
    return templates.TemplateResponse("reviewP/millsReviewPage.html", {"request": request, "reviews": newreview})


@router.get("/reviewP/seasonsReview", response_class=HTMLResponse)
async def seasons_review(request: Request, db: Session = Depends(get_session)):
    reviews = db.exec(
        select(Review)  # select(Review, User )
        # .join(User, Review.author_id == User.user_id)
        .where(Review.location_id == 4)
    ).all()

    newreview = []
    for review in reviews:  # for review, user in reviews
        newreview.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                # "author": user.username,
                "nickname": review.nickname,
            }
        )
    return templates.TemplateResponse("reviewP/seasonsReviewPage.html", {"request": request, "reviews": newreview})


@router.get("/reviewP/wilsReview", response_class=HTMLResponse)
async def wils_review(request: Request, db: Session = Depends(get_session)):
    reviews = db.exec(
        select(Review)  # select(Review, User)
        # .join(User, Review.author_id == User.user_id)
        .where(Review.location_id == 5)
    ).all()

    newreview = []
    for review in reviews:  # for review, user in reviews:
        newreview.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                # "author": user.username,
                "nickname": review.nickname,
            }
        )
    return templates.TemplateResponse("reviewP/wilsReviewPage.html", {"request": request, "reviews": newreview})


# createss a new user
"""@router.post("/register")
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
"""


# user reviews
@router.post("/reviewcreate")
async def create_review(
    meal: str = Form(...),
    stars: int = Form(...),
    content: str = Form(...),
    location_id: int = Form(...),
    author: str = Form(...),
    db: Session = Depends(get_session),
    # user_id: int = Form(...),
):
    review = Review(
        title=meal,
        rating=stars,
        body=content,
        location_id=location_id,
        nickname=author,
        # author_id=user_id,
    )

    db.add(review)

    db.commit()

    return RedirectResponse(url="/menu", status_code=303)
