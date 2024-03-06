from app import db, bcrypt, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Gebruiker.query.get(user_id)

class Gebruiker(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    wachtwoord_hash = db.Column(db.String(128))

    def __init__(self, username, email, wachtwoord):
        self.username = username
        self.email = email
        self.set_wachtwoord(wachtwoord)

    def set_wachtwoord(self, wachtwoord):
        self.wachtwoord_hash = bcrypt.generate_password_hash(wachtwoord).decode('utf-8')

    def check_wachtwoord(self, wachtwoord):
        return bcrypt.check_password_hash(self.wachtwoord_hash, wachtwoord)
    


class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String(100), nullable=False)
    regisseur_id = db.Column(db.Integer, db.ForeignKey('regisseur.id'), nullable=False)
    jaar = db.Column(db.Integer, nullable=False)
    # Relatie met Regisseur en Rol

class Regisseur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voornaam = db.Column(db.String(50), nullable=False)
    achternaam = db.Column(db.String(50), nullable=False)
    films = db.relationship('Film', backref='regisseur', lazy=True)

class Acteur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voornaam = db.Column(db.String(50), nullable=False)
    achternaam = db.Column(db.String(50), nullable=False)
    rollen = db.relationship('Rol', backref='acteur', lazy=True)

class Rol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    acteur_id = db.Column(db.Integer, db.ForeignKey('acteur.id'), nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'), nullable=False)
    personage = db.Column(db.String(100), nullable=False)

# db.create_all()