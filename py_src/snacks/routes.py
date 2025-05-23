# adding user info in the future
import urllib.parse

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from snacks.db import (
    LocationHours,
    LocationLinks,
    Locations,
    Reviews,
    get_session,
    templates,
)

router = APIRouter()


def generate_map_url(lat: float, lng: float, name: str = "") -> str:
    """Generate a Google Maps embed URL from coordinates"""
    encoded_name = urllib.parse.quote(name)
    return (
        f"https://www.google.com/maps/embed"
        f"?pb=!1m18!1m12!1m3!1d734!2d{lng}!3d{lat}"
        f"!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1"
        f"!3m3!1m2!1s!2s{encoded_name}!5e0!3m2!1sen!2sus!4v1!5m2!1sen!2sus"
    )


def get_locations(db: Session):
    """Helper function to get all locations with their data"""
    locations = db.exec(select(Locations)).all()
    location_data = []

    for location in locations:
        location_data.append({"id": location.location_id, "name": location.name})

    return location_data


@router.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_session)):
    # Query to fetch reviews and associated location information

    review_locations = db.exec(
        select(Reviews, Locations).join(
            Locations, Reviews.location_id == Locations.location_id
        )
    ).all()

    allreviews = []
    for review, location in review_locations:
        allreviews.append(
            {
                "title": review.title,
                "body": review.body,
                "rating": review.rating,
                "location": location.name,
                "nickname": review.nickname,
            }
        )

    locations = get_locations(db)
    return templates.TemplateResponse(
        "menu.html", {"request": request, "reviews": allreviews, "locations": locations}
    )


@router.get("/menu", response_class=HTMLResponse)
async def menu(request: Request, db: Session = Depends(get_session)):
    return await root(request, db)


@router.get("/campus-map", response_class=HTMLResponse)
async def campus_map(request: Request, db: Session = Depends(get_session)):
    # Get all locations with their hours and links
    locations = db.exec(select(Locations)).all()
    location_data = []

    for location in locations:
        # Get location hours
        hours = db.exec(
            select(LocationHours).where(
                LocationHours.location_id == location.location_id
            )
        ).all()

        # Get location links
        links = db.exec(
            select(LocationLinks).where(
                LocationLinks.location_id == location.location_id
            )
        ).all()

        location_data.append(
            {
                "id": location.location_id,
                "name": location.name,
                "description": location.description,
                "coordinates": {"lat": location.latitude, "lng": location.longitude},
                "hours": {h.day_type: h.hours for h in hours},
                "links": {l.link_type: l.url for l in links},  # noqa: E741
                "image": location.image_filename,
            }
        )

    nav_locations = get_locations(db)
    return templates.TemplateResponse(
        "campus_map.html",
        {
            "request": request,
            "locations": location_data,
            "nav_locations": nav_locations,
        },
    )


@router.get("/reviews/{location_id}", response_class=HTMLResponse)
async def location_reviews(
    location_id: int, request: Request, db: Session = Depends(get_session)
):
    # Get location info
    location = db.exec(
        select(Locations).where(Locations.location_id == location_id)
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Get location hours and links
    hours = db.exec(
        select(LocationHours).where(LocationHours.location_id == location.location_id)
    ).all()

    links = db.exec(
        select(LocationLinks).where(LocationLinks.location_id == location.location_id)
    ).all()

    # Get reviews for this location
    reviews = db.exec(
        select(Reviews).where(Reviews.location_id == location.location_id)
    ).all()

    # Restructure links to match template expectations
    link_data = {}
    for link in links:
        if link.link_type == "menu":
            link_data["menu"] = link.url
        elif link.link_type == "instagram":
            link_data["instagram"] = link.url
        elif link.link_type == "getApp_android":
            if "getApp" not in link_data:
                link_data["getApp"] = {}
            link_data["getApp"]["android"] = link.url
        elif link.link_type == "getApp_ios":
            if "getApp" not in link_data:
                link_data["getApp"] = {}
            link_data["getApp"]["ios"] = link.url

    location_data = {
        "id": location.location_id,
        "name": location.name,
        "description": location.description,
        "coordinates": {"lat": location.latitude, "lng": location.longitude},
        "hours": {h.day_type: h.hours for h in hours},
        "links": link_data,
        "image": location.image_filename,
        "map": generate_map_url(location.latitude, location.longitude, location.name),
    }

    nav_locations = get_locations(db)
    return templates.TemplateResponse(
        "reviews.html",
        {
            "request": request,
            "location": location_data,
            "reviews": reviews,
            "locations": nav_locations,
        },
    )


@router.get("/create-review/{location_id}", response_class=HTMLResponse)
async def leave_review_pages(
    location_id: int, request: Request, db: Session = Depends(get_session)
):
    # Get location info
    location = db.exec(
        select(Locations).where(Locations.location_id == location_id)
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Get location hours and links
    hours = db.exec(
        select(LocationHours).where(LocationHours.location_id == location.location_id)
    ).all()

    links = db.exec(
        select(LocationLinks).where(LocationLinks.location_id == location.location_id)
    ).all()

    # Restructure links to match template expectations
    link_data = {}
    for link in links:
        if link.link_type == "menu":
            link_data["menu"] = link.url
        elif link.link_type == "instagram":
            link_data["instagram"] = link.url
        elif link.link_type == "getApp_android":
            if "getApp" not in link_data:
                link_data["getApp"] = {}
            link_data["getApp"]["android"] = link.url
        elif link.link_type == "getApp_ios":
            if "getApp" not in link_data:
                link_data["getApp"] = {}
            link_data["getApp"]["ios"] = link.url

    location_data = {
        "id": location.location_id,
        "name": location.name,
        "description": location.description,
        "coordinates": {"lat": location.latitude, "lng": location.longitude},
        "hours": {h.day_type: h.hours for h in hours},
        "links": link_data,
        "image": location.image_filename,
        "map": generate_map_url(location.latitude, location.longitude, location.name),
    }

    nav_locations = get_locations(db)
    return templates.TemplateResponse(
        "create_review.html",
        {"request": request, "location": location_data, "locations": nav_locations},
    )


@router.post("/reviewcreate")
async def create_review(
    title: str = Form(...),
    rating: int = Form(...),
    body: str = Form(...),
    location_id: int = Form(...),
    nickname: str = Form(...),
    db: Session = Depends(get_session),
):
    print(f"Creating review for location {location_id} with title '{title}'")

    # Validate rating
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=422, detail="Rating must be between 1 and 5")

    # Get location from database
    location = db.exec(
        select(Locations).where(Locations.location_id == location_id)
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    review = Reviews(
        title=title,
        rating=rating,
        body=body,
        location_id=location.location_id,
        nickname=nickname,
    )
    db.add(review)
    db.commit()

    return RedirectResponse(url=f"/reviews/{location_id}", status_code=303)


@router.on_event("startup")
async def startup_event():
    _ = next(get_session())
