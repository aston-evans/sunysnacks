# trying to incorporate fastapi into the project.

#import os
#from flask import Flask
#from flask import render_template
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated # noqa
from pydantic import BaseModel  # noqa: F401


app = FastAPI()

app.mount("/static", StaticFiles(directory="py_src/flaskr/static"), name="static")

templates = Jinja2Templates(directory="py_src/flaskr/templates")


@app.get("/", response_class=HTMLResponse)
async def test(request: Request, q: str = Query(default="No Query")):
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "q": q
    })
@app.get("/auth/login", response_class=HTMLResponse)
async def login(request: Request, q: None = None):
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "q": q
    })

@app.get("/menu", response_class=HTMLResponse)
async def main(request: Request, q: None = None):
    return templates.TemplateResponse("menu.html", {
        "request": request,
        "q": q
    })
    
@app.get("/create", response_class=HTMLResponse)
async def create(request: Request, q: None = None):
    return templates.TemplateResponse("auth/create.html", {
        "request": request,
        "q": q
    })

@app.get("/map", response_class=HTMLResponse)
async def map(request: Request):
    return templates.TemplateResponse("map.html", {
        "request": request
    })
#createR is the route for the leave review pages 
@app.get("/createR/argoLeaveReview", response_class=HTMLResponse)
async def argoLeave(request: Request): #certain a query's will be needed here later on
    return templates.TemplateResponse("createR/argoLeaveReview.html", {
        "request": request
    })

@app.get("/createR/marketLeaveReview", response_class=HTMLResponse)
async def marketLeave(request: Request): 
    return templates.TemplateResponse("createR/marketLeaveReview.html", {
        "request": request
    })

@app.get("/createR/millsLeaveReview", response_class=HTMLResponse)
async def millsLeave(request: Request): 
    return templates.TemplateResponse("createR/millsLeaveReview.html", {
        "request": request
    })

@app.get("/createR/seasonsLeaveReview", response_class=HTMLResponse)
async def seasonsLeave(request: Request): 
    return templates.TemplateResponse("createR/seasonsLeaveReview.html", {
        "request": request
    })

@app.get("/createR/wilsLeaveReview", response_class=HTMLResponse)
async def wilsLeave(request: Request): 
    return templates.TemplateResponse("createR/wilsLeaveReview.html", {
        "request": request
    })



#reviewP is the route for the entire review pages 
@app.get("/reviewP/argoReview", response_class=HTMLResponse)
async def argoReview(request: Request): #potential queries? Probably more in the dictionary.    
    return templates.TemplateResponse("reviewP/argoReviewPage.html", {
        "request": request
    })
@app.get("/reviewP/marketReview", response_class=HTMLResponse)
async def marketReview(request: Request): #potential queries? Probably more in the dictionary.    
    return templates.TemplateResponse("reviewP/marketReviewPage.html", {
        "request": request
    })
@app.get("/reviewP/millsReview", response_class=HTMLResponse)
async def millsReview(request: Request): #potential queries? Probably more in the dictionary.    
    return templates.TemplateResponse("reviewP/millsReviewPage.html", {
        "request": request
    })

@app.get("/reviewP/seasonsReview", response_class=HTMLResponse)
async def seasonsReview(request: Request): #potential queries? Probably more in the dictionary.    
    return templates.TemplateResponse("reviewP/seasonsReviewPage.html", {
        "request": request
    })

@app.get("/reviewP/wilsReview", response_class=HTMLResponse)
async def wilsReview(request: Request): #potential queries? Probably more in the dictionary.    
    return templates.TemplateResponse("reviewP/wilsReviewPage.html", {
        "request": request
    })



'''
class Response(BaseModel):
    title: str
    body: str
    author: str 
    rating: int
    

@app.get("/")
async def hi():
    return "hello world"

@app.post("/reviews")
async def reviews(review: Response):
    author = review.author
    body = review.body
    title = review.title
    rating = review.rating
    return {"message": "Review Submitted!", "review_info": review.dict()}

p1 = Response(author="aston", body="nice guy", title="life", rating=5)'''


'''
@app.get("/templates/menu")
def main():
    return 
'''

# creating app
'''def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    """@app.route('/menu')
    def home():
        return render_template('menu.html')
       """

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import blog

    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="menu")  # index will be changed/
    from . import menu

    app.register_blueprint(menu.bp)
    app.add_url_rule("/", endpoint="menu.menu")

    return app
'''