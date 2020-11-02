import uuid
import hashlib

from flask import Flask, render_template, redirect, url_for, request, flash
from datetime import datetime
from models import db, User, Messages


# runtime environment
app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
db.create_all()


# index page
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        flash("Test")
        return render_template("register.html")

    elif request.method == "POST":
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
