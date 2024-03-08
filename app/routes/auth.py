from app import db, bcrypt
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app.forms.forms import LoginForm, RegistratieForm

from app.models.models import Gebruiker


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        gebruiker:Gebruiker = Gebruiker.query.filter_by(email=form.email.data).first()
        if gebruiker and bcrypt.check_password_hash(gebruiker.wachtwoord_hash, form.wachtwoord.data):
            login_user(gebruiker, remember=form.remember_me.data)
            flash('Succesvol ingelogd.', 'success')

            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('Login mislukt. Controleer e-mail en wachtwoord.', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Je bent nu uitgelogd!')
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form:RegistratieForm = RegistratieForm()
    if form.validate_on_submit():
        new_user:Gebruiker = Gebruiker(username=form.username.data, email=form.email.data, wachtwoord=form.wachtwoord.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Je account is aangemaakt. Je kunt nu inloggen.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

