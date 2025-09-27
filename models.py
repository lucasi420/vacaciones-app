from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Creamos la base de datos
db = SQLAlchemy()

# Modelo de usuario
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # True = superusuario
from datetime import date

class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # formato 'YYYY-MM-DD'

    user = db.relationship('User', backref=db.backref('vacations', lazy=True))
