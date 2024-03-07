from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, ValidationError
from wtforms.validators import InputRequired, DataRequired, Optional, Email, URL, Length, EqualTo
from app.models import Gebruiker

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message='Ongeldig email'), Length(max=100)])
    wachtwoord = PasswordField('Wachtwoord', validators=[DataRequired(), Length(min=8, max=80)])
    remember_me = BooleanField('Onthoud mij')
    submit = SubmitField('Inloggen')

class RegistratieForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email(message='Ongeldig email'), Length(max=100)])
    wachtwoord = PasswordField('Wachtwoord', validators=[InputRequired(), Length(min=8, max=80), EqualTo('confirm', message='Wachtwoorden moeten overeenkomen')])
    confirm = PasswordField('Bevestig Wachtwoord')
    submit = SubmitField('Registreren')

    def check_username(self, field):
        # Check of de gebruikersnaam nog niet vergeven is!
        if Gebruiker.query.filter_by(username=field.data).first():
            raise ValidationError('Deze gebruikersnaam is al vergeven, kies een andere naam!')

    def check_email(self, field):
        # Check of het e-mailadres al in de database voorkomt!
        if Gebruiker.query.filter_by(email=field.data).first():
            raise ValidationError('Dit e-mailadres staat al geregistreerd!')
        
    
class FilmForm(FlaskForm):
    titel = StringField('Titel', validators=[DataRequired()])
    regisseur_id = SelectField('Regisseur', coerce=int, validators=[DataRequired()])
    jaar = IntegerField('Jaar', validators=[DataRequired()])
    trailer_url = StringField('Trailer URL', validators=[Optional(), URL()])
    bezoekers = IntegerField('Bezoekers', validators=[Optional()])
    omzet = IntegerField('Omzet', validators=[Optional()])
    overzicht = TextAreaField('Overzicht', validators=[Optional()])
    submit = SubmitField('Film Toevoegen')
    
class CitaatForm(FlaskForm):
    inhoud = TextAreaField('Citaat', validators=[DataRequired(message="Quote content is required")])
    submit = SubmitField('Add Quote')

class RegisseurForm(FlaskForm):
    voornaam = StringField('Voornaam', validators=[DataRequired()])
    achternaam = StringField('Achternaam', validators=[DataRequired()])
    submit = SubmitField('Regisseur Toevoegen')

class ActeurForm(FlaskForm):
    voornaam = StringField('Voornaam', validators=[DataRequired()])
    achternaam = StringField('Achternaam', validators=[DataRequired()])
    submit = SubmitField('Actuer Toevoegen')