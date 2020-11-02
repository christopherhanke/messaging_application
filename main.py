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
    if "session_token" in session:
        user = db.query(User).filter_by(session_token=session["session_token"], deleted=False).first()
        flash(f"Hello {user.name}")
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if "user" in session:
            flash(f"Your are logged in, {session['user']}", "info")
            return redirect(url_for("index"))
        return render_template("register.html")

    elif request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(name=name).first()
        if not user:
            user = User(
                name=name,
                email=email,
                password=hashed_password,
                location="",
                deleted=False
            )

            session_token = str(uuid.uuid4())
            user.session_token = session_token
            db.add(user)
            db.commit()

            session["session_token"] = session_token

            flash("Registration successfully!", "info")
            return redirect(url_for("index"))

        else:
            flash("User exists, please use unique username.", "info")
            return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
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
        db.add(user)
        db.commit()

        flash("Login successful.", "info")
        return redirect(url_for("index"))


@app.route("/logout", methods=["GET"])
def logout():

    return page_under_construction()


@app.route("/profile")
def profile():
    return page_under_construction()


@app.route("/users", methods=["GET"])
def all_users():
    users = db.query(User).filter_by(deleted=False).all()

    return render_template("users.html", users=users)


def page_under_construction():
    flash("Page is under construction", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
