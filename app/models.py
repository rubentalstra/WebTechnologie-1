from email.policy import default
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
    trailer_url = db.Column(db.String(255))  # Assuming trailers are hosted externally
    bezoekers = db.Column(db.Integer, default=None)  # Visitor count
    omzet = db.Column(db.BigInteger, default=None)  # Revenue, using BigInteger for larger numbers
    overzicht = db.Column(db.Text)  # General overview or description of the film
    citaten = db.relationship('Citaat', backref='film', lazy=True)

    def __init__(self, titel, regisseur_id, jaar, trailer_url=None, bezoekers=None, omzet=None, overzicht=None):
        self.titel = titel
        self.regisseur_id = regisseur_id
        self.jaar = jaar
        self.trailer_url = trailer_url
        self.bezoekers = bezoekers
        self.omzet = omzet
        self.overzicht = overzicht


class Citaat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inhoud = db.Column(db.Text, nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'), nullable=False)

    def __init__(self, inhoud, film_id):
        self.inhoud = inhoud
        self.film_id = film_id

class Regisseur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voornaam = db.Column(db.String(50), nullable=False)
    achternaam = db.Column(db.String(50), nullable=False)
    films = db.relationship('Film', backref='regisseur', lazy=True)

    def __init__(self, voornaam, achternaam):
        self.voornaam = voornaam
        self.achternaam = achternaam

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