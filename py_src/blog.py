from flask import Blueprint, flash, g, redirect, render_template, request, url_for
# from werkzeug.exceptions import abort

from flaskr.auth import login_required #type: ignore
from flaskr.db import get_db #type: ignore

bp = Blueprint("blog", __name__)


@bp.route("/ReviewPage/<int:location_id>")
def index(location_id):
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post AS p JOIN user AS u ON p.author_id = u.id"
        " WHERE p.location_id = ?"
        " ORDER BY created DESC",
        (location_id,),
    ).fetchall()
    return render_template("blog/base_reviews.html", posts=posts)


@bp.route("/LeaveReview/<int:location_id>", methods=("GET", "POST"))
@login_required
def create(location_id):
    if request.method == "POST":
        title = request.form["meal"]
        body = request.form["body"]
        rating = request.form["stars"]
        error = None

        if not title:
            error = "Title is required."
        elif not body:
            error = "Body is required."
        elif not rating:
            error = "Rating is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, location_id, rating,  author_id)"
                " VALUES (?, ?, ?, ?, ?)",
                (title, body, location_id, rating, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.base_reviews.html", location_id=location_id))

    return render_template("blog/base_leaveReviews.html", location_id=location_id)
