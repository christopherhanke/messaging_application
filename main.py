import uuid
import hashlib
import datetime

# flask_session
from flask import Flask, render_template, redirect, url_for, request, flash, session
from models import db, User, Messages
from sqlalchemy import and_

# runtime environment
app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
app.permanent_session_lifetime = datetime.timedelta(minutes=5)
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
    # getting logged in user or redirect
    user = get_logged_in_user()
    if user:
        flash("You are logged in.", "info")
        return redirect(url_for("profile"))

    # show login with GET request
    if request.method == "GET":
        return render_template("login.html")

    # login when POST request
    elif request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # check for username in db
        user = db.query(User).filter_by(name=name).first()
        if not user:
            flash("Username does not exist!", "info")
            return redirect(url_for("login"))

        # check password for login
        if hashed_password != user.password:
            flash("Wrong password!", "info")
            return redirect(url_for("login"))

        # set session token and save to db
        session_token = str(uuid.uuid4())
        user.session_token = session_token
        session["session_token"] = session_token
        session.permanent = True
        db.add(user)
        db.commit()

        flash("Login successful.", "info")
        return redirect(url_for("index"))


@app.route("/logout", methods=["GET"])
def logout():
    # getting logged in user or redirect
    user = get_logged_in_user()
    if not user:
        flash("You are not logged in.", "info")
        return redirect(url_for("index"))

    # delete session_token from user in db
    user.session_token = None
    db.add(user)
    db.commit()

    # delete session token from session
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
    # getting logged in user or redirect
    user = get_logged_in_user()
    if not user:
        flash("You are not logged in.", "info")
        return redirect(url_for("index"))

    # get all users in db that are not deleted or the logged in user
    users = db.query(User).filter(and_(User.deleted == False, User.id != user.id))

    return render_template("users.html", users=users)


@app.route("/users/<user_id>", methods=["GET"])
def users_details(user_id):
    # getting logged in user or redirect
    user = get_logged_in_user()
    if not user:
        flash("You are not logged in.", "info")
        return redirect(url_for("index"))

    # getting the user from db to display his profile
    try:
        user_id = int(user_id)
        user_profile = db.query(User).get(user_id)
    except ValueError:
        flash("Invalid User", "info")
        return redirect(url_for("all_users"))

    return render_template("users_details.html", user=user_profile)


@app.route("/messages/<partner>", methods=["GET", "POST"])
def messages(partner):
    # getting logged in user or redirect
    user = get_logged_in_user()
    if not user:
        flash("You are not logged in.", "info")
        return redirect(url_for("index"))

    # getting entry for partner form db
    try:
        partner_id = int(partner)
        partner = db.query(User).filter(User.id == partner_id).first()
    except ValueError:
        flash("Invalid Chatpartner", "info")
        return redirect(url_for("all_users"))

    # if method post, then take message and create new entry in db
    if request.method == "POST":
        message = request.form.get("message")
        time = datetime.datetime.now()

        msg = Messages(
            message=message,
            time=time,
            sender=user.id,
            receiver=partner.id
        )
        db.add(msg)
        db.commit()

    # get all messages for logged in user and partner
    msgs = db.query(Messages).filter(
            and_(Messages.sender.in_([user.id, partner.id]), Messages.receiver.in_([partner.id, user.id]))
    )

    return render_template("messages.html", messages=msgs, user=user, partner=partner)


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
