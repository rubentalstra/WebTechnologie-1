from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from .models import Gebruiker, Film
from .forms import FilmForm, LoginForm, RegistratieForm
from . import db, bcrypt

app = Blueprint('main', __name__)

@app.route('/')
def index():
    films = Film.query.all()
    return render_template('index.html', films=films)

@app.route('/welkom')
@login_required
def welkom():
    return render_template('welcome.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        gebruiker = Gebruiker.query.filter_by(email=form.email.data).first()
        if gebruiker and bcrypt.check_password_hash(gebruiker.wachtwoord_hash, form.wachtwoord.data):
            login_user(gebruiker, remember=form.remember_me.data)
            flash('Succesvol ingelogd.', 'success')

            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.welkom')
            return redirect(next_page)
        else:
            flash('Login mislukt. Controleer e-mail en wachtwoord.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Je bent nu uitgelogd!')
    return redirect(url_for('main.index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistratieForm()
    if form.validate_on_submit():
        new_user = Gebruiker(username=form.username.data, email=form.email.data, wachtwoord=form.wachtwoord.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Je account is aangemaakt. Je kunt nu inloggen.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@app.route('/film/<int:id>')
def film_detail(id):
    film = Film.query.get_or_404(id)
    return render_template('film_detail.html', film=film)



@app.route('/film/add', methods=['GET', 'POST'])
def add_film():
    form = FilmForm()
    if form.validate_on_submit():
        film = Film(titel=form.titel.data, regisseur_id=form.regisseur_id.data, jaar=form.jaar.data)
        db.session.add(film)
        db.session.commit()
        flash('De film is succesvol toegevoegd!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_film.html', title='Film Toevoegen', form=form)

@app.route('/film/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_film(id):
    film = Film.query.get_or_404(id)
    if request.method == 'POST':
        # Logic to update film
        return redirect(url_for('film_detail', id=film.id))
    return render_template('edit_film.html', film=film)

@app.route('/film/delete/<int:id>', methods=['POST'])
@login_required
def delete_film(id):
    film = Film.query.get_or_404(id)
    # Logic to delete film
    return redirect(url_for('index'))


@app.route('/regisseurs')
@login_required
def regisseurs():
    # Logic to display directors
    pass

@app.route('/acteurs')
@login_required
def acteurs():
    # Logic to display actors
    pass

@app.route('/rollen')
@login_required
def rollen():
    # Logic to display roles
    pass
