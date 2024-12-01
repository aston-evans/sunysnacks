# menu blueprint
from flask import Blueprint, render_template

bp = Blueprint("menu", __name__)


@bp.route("/menu")
def menu():
    return render_template("menu.html")
