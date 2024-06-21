from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    admin = db.Column(db.Boolean, default=False)

class Execution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folder = db.Column(db.String(120))
    date = db.Column(db.DateTime)
    progress = db.Column(db.Integer, default=0)
    result_filename = db.Column(db.String(200))