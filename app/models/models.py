from app import db, bcrypt, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Gebruiker.query.get(user_id)

class Gebruiker(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    wachtwoord_hash = db.Column(db.String(128))

    def __init__(self, username: str, email: str, wachtwoord: str):
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
    trailer_url = db.Column(db.String(255))
    poster_url = db.Column(db.String(255)) 
    bezoekers = db.Column(db.Integer, default=None) 
    omzet = db.Column(db.BigInteger, default=None)
    overzicht = db.Column(db.Text)
    citaten = db.relationship('Citaat', backref='film', lazy=True)

    def __init__(self, titel: str, regisseur_id: int, jaar: int, trailer_url: str = '', poster_url: str = '', bezoekers: int = 0, omzet: int = 0, overzicht: str = ''):
        self.titel = titel
        self.regisseur_id = regisseur_id
        self.jaar = jaar
        self.trailer_url = trailer_url
        self.poster_url = poster_url
        self.bezoekers = bezoekers
        self.omzet = omzet
        self.overzicht = overzicht


class Citaat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inhoud = db.Column(db.Text, nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('gebruiker.id'), nullable=False)
    user = db.relationship('Gebruiker', backref='quotes')

    def __init__(self, inhoud: str, film_id: int, user_id: int):
        self.inhoud = inhoud
        self.film_id = film_id
        self.user_id = user_id


class Regisseur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voornaam = db.Column(db.String(50), nullable=False)
    achternaam = db.Column(db.String(50), nullable=False)
    films = db.relationship('Film', backref='regisseur', lazy=True)

    def __init__(self, voornaam: str, achternaam: str):
        self.voornaam = voornaam
        self.achternaam = achternaam

class Acteur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voornaam = db.Column(db.String(50), nullable=False)
    achternaam = db.Column(db.String(50), nullable=False)
    rollen = db.relationship('Rol', backref='acteur', lazy=True)

    def __init__(self, voornaam: str, achternaam: str):
        self.voornaam = voornaam
        self.achternaam = achternaam

class Rol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    acteur_id = db.Column(db.Integer, db.ForeignKey('acteur.id'), nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'), nullable=False)
    personage = db.Column(db.String(100), nullable=False)

    def __init__(self, acteur_id: int, film_id: int, personage: str):
        self.acteur_id = acteur_id
        self.film_id = film_id
        self.personage = personage