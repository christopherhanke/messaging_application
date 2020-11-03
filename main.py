import uuid
import hashlib

from flask import Flask, render_template, redirect, url_for, request, flash, session
from datetime import datetime
from models import db, User, Messages


# runtime environment
app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
db.create_all()


# index page
@app.route("/")
def index():
    user = get_logged_in_user()
    if user:
        flash(f"Hello {user.name}")
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # check if user is logged in, if user is logged in redirect to profile
    user = get_logged_in_user()
    if user:
        flash("You are logged in.", "info")
        return redirect(url_for("profile"))

    # get-request to register site
    if request.method == "GET":
        return render_template("register.html")

    # handle for post request on register
    # handling form-data from user and checking user-db
    elif request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # checking user db and initializing new user if name is new/unique
        user = db.query(User).filter_by(name=name).first()
        if not user:
            user = User(
                name=name,
                email=email,
                password=hashed_password,
                location="",
                deleted=False
            )

            # setting up session token
            session_token = str(uuid.uuid4())
            user.session_token = session_token
            session["session_token"] = session_token

            # commit user to db
            db.add(user)
            db.commit()

            flash("Registration successfully!", "info")
            return redirect(url_for("index"))

        else:
            flash("User exists, please use unique username.", "info")
            return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    user = get_logged_in_user()
    if user:
        flash("You are logged in.", "info")
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(name=name).first()
        if not user:
            flash("Username does not exist!", "info")
            return redirect(url_for("login"))

        if hashed_password != user.password:
            flash("Wrong password!", "info")
            return redirect(url_for("login"))

        session_token = str(uuid.uuid4())
        user.session_token = session_token
        session["session_token"] = session_token
        db.add(user)
        db.commit()

        flash("Login successful.", "info")
        return redirect(url_for("index"))


@app.route("/logout", methods=["GET"])
def logout():
    user = get_logged_in_user()
    if not user:
        flash("You are not logged in.", "info")
        return redirect(url_for("index"))
    user.session_token = None
    db.add(user)
    db.commit()

    session.pop("session_token", None)
    flash("You have been logged out.")
    return redirect(url_for("index"))


# view for user profile
@app.route("/profile")
def profile():
    user = get_logged_in_user()
    if user:
        return render_template("profile.html", user=user)

    flash("You are not logged in.", "info")
    return redirect(url_for("index"))


@app.route("/users", methods=["GET"])
def all_users():
    user = get_logged_in_user()
    if not user:
        flash("You are not logged in.", "info")
        return redirect(url_for("index"))

    users = db.query(User).filter_by(deleted=False).all()
    return render_template("users.html", users=users)


@app.route("/users/<user_id>", methods=["GET"])
def users_details(user_id):
    user = get_logged_in_user()
    if not user:
        flash("You are not logged in.", "info")
        return redirect(url_for("index"))
    user_profile = db.query(User).get(int(user_id))
    return render_template("users_details.html", user=user_profile)


@app.route("/messages/<user_id>", methods=["GET"])
def messages(user_id):
    user = get_logged_in_user()
    if not user:
        flash("You are not logged in.", "info")
        return redirect(url_for("index"))
    user_partner = db.query(User).get(int(user_id))

    return render_template("messages.html", messages=["You are not alone.", "I'll be here with you", "Test 3"])


# helping function for sites under construction
def page_under_construction():
    # flashing info to user and redirect to index-page
    flash("Page is under construction", "info")
    return redirect(url_for("index"))


# helping function getting logged in user
def get_logged_in_user():
    user = None
    if "session_token" in session:
        user = db.query(User).filter_by(session_token=session["session_token"], deleted=False).first()
    return user


if __name__ == "__main__":
    app.run(debug=True)
