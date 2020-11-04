import os
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    location = db.Column(db.String)
    password = db.Column(db.String)
    session_token = db.Column(db.String)
    deleted = db.Column(db.Boolean)


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String)
    time = db.Column(db.DateTime)
    sender = db.Column(db.Integer)
    receiver = db.Column(db.Integer)
