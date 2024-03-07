from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from .models import Acteur, Citaat, Gebruiker, Film, Regisseur, Rol
from .forms import ActeurForm, CitaatForm, FilmForm, LoginForm, RegisseurForm, RegistratieForm, RolForm
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



@app.route('/film/<int:id>', methods=['GET', 'POST'])
def film_detail(id):
    film = Film.query.get_or_404(id)
    quotes = Citaat.query.filter_by(film_id=id).all()  # Fetch quotes related to the film
    
    form = CitaatForm()
    if form.validate_on_submit():
        new_quote = Citaat(inhoud=form.inhoud.data, film_id=id)
        db.session.add(new_quote)
        db.session.commit()
        flash('Quote successfully added.', 'success')
        return redirect(url_for('main.film_detail', id=id))  # Refresh the page to show the new quote
    
    return render_template('film_detail.html', film=film, quotes=quotes, form=form)


    
@app.route('/film/add', methods=['GET', 'POST'])
@login_required
def film_add():
    form = FilmForm()
    form.regisseur_id.choices = [(0, 'Choose...')] + [(r.id, r.voornaam + ' '  + r.achternaam ) for r in Regisseur.query.all()]

    if form.validate_on_submit():
        # Create a new Film instance with all the form fields
        film = Film(
            titel=form.titel.data, 
            regisseur_id=form.regisseur_id.data,
            jaar=form.jaar.data,
            trailer_url=form.trailer_url.data,
            bezoekers=form.bezoekers.data,
            omzet=form.omzet.data,
            overzicht=form.overzicht.data
        )
        db.session.add(film)
        db.session.commit()
        flash('De film is succesvol toegevoegd!', 'success')
        return redirect(url_for('main.index'))
    return render_template('film_add.html', title='Film Toevoegen', form=form)


@app.route('/film/<int:film_id>/add_quote', methods=['GET', 'POST'])
@login_required
def add_quote_for_film(film_id):
    form = CitaatForm()
    if form.validate_on_submit():
        quote = Citaat(inhoud=form.inhoud.data, film_id=film_id)
        db.session.add(quote)
        db.session.commit()
        flash('Quote successfully added.', 'success')
        return redirect(url_for('main.film_detail', id=film_id))
    return render_template('film_add_quote.html', form=form, film_id=film_id)



@app.route('/film/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_film(id):
    film = Film.query.get_or_404(id)
    form = FilmForm(obj=film)

    form.regisseur_id.choices = [(0, 'Choose...')] + [(r.id, r.voornaam + ' '  + r.achternaam ) for r in Regisseur.query.all()]
    
    if form.validate_on_submit():
        # if form.regisseur_id.data == 0:
        #     flash('Please select a valid regisseur.', 'danger')
        #     return render_template('film_edit.html', form=form, film=film)

        film.titel = form.titel.data
        film.regisseur_id = form.regisseur_id.data
        film.jaar = form.jaar.data
        film.trailer_url = form.trailer_url.data
        film.bezoekers = form.bezoekers.data
        film.omzet = form.omzet.data
        film.overzicht = form.overzicht.data
        
        db.session.commit()
        flash('De film is succesvol bijgewerkt!', 'success')
        return redirect(url_for('main.film_detail', id=film.id))
    
    return render_template('film_edit.html', form=form, film=film)



@app.route('/film/delete/<int:id>')
@login_required
def delete_film(id):
    film = Film.query.get_or_404(id)
    db.session.delete(film)
    db.session.commit()
    flash('Film successfully deleted.', 'success')
    return redirect(url_for('main.index'))





@app.route('/regisseurs', methods=['GET'])
def regisseurs():
    regisseurs = Regisseur.query.all()  # Fetch all regisseurs
    return render_template('regisseurs.html', regisseurs=regisseurs)


@app.route('/regisseur/add', methods=['GET', 'POST'])
@login_required
def regisseur_add():
    form = RegisseurForm()
    if form.validate_on_submit():
        regisseur = Regisseur(voornaam=form.voornaam.data, achternaam=form.achternaam.data)
        db.session.add(regisseur)
        db.session.commit()
        flash('De regisseur is succesvol toegevoegd!', 'success')
        return redirect(url_for('main.regisseurs'))
    return render_template('regisseur_add.html', form=form)


@app.route('/regisseur/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def regisseur_edit(id):
    regisseur = Regisseur.query.get_or_404(id)
    form = RegisseurForm(obj=regisseur)
    
    if form.validate_on_submit():
        regisseur.voornaam = form.voornaam.data
        regisseur.achternaam = form.achternaam.data
        
        db.session.commit()
        flash('De regisseur is succesvol bijgewerkt!', 'success')
        return redirect(url_for('main.regisseurs', id=regisseur.id))
    
    return render_template('regisseur_edit.html', form=form)


@app.route('/regisseur/delete/<int:id>')
@login_required
def delete_regisseur(id):
    regisseur = Regisseur.query.get_or_404(id)
    if regisseur.films:
        flash('Cannot delete a Regisseur connected to films.', 'danger')
    else:
        db.session.delete(regisseur)
        db.session.commit()
        flash('Regisseur successfully deleted.', 'success')
    return redirect(url_for('main.regisseurs'))




@app.route('/acteurs', methods=['GET'])
def acteurs():
    acteurs = Acteur.query.all()  # Fetch all acteurs
    return render_template('acteurs.html', acteurs=acteurs)

@app.route('/acteur/add', methods=['GET', 'POST'])
@login_required
def acteur_add():
    form = ActeurForm()
    if form.validate_on_submit():
        acteur = Acteur(voornaam=form.voornaam.data, achternaam=form.achternaam.data)
        db.session.add(acteur)
        db.session.commit()
        flash('De acteur is succesvol toegevoegd!', 'success')
        return redirect(url_for('main.acteurs'))
    return render_template('acteur_add.html', form=form)


@app.route('/acteur/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def acteur_edit(id):
    acteur = Acteur.query.get_or_404(id)
    form = ActeurForm(obj=acteur)
    
    if form.validate_on_submit():
        acteur.voornaam = form.voornaam.data
        acteur.achternaam = form.achternaam.data
        
        db.session.commit()
        flash('De acteur is succesvol bijgewerkt!', 'success')
        return redirect(url_for('main.acteurs', id=acteur.id))
    
    return render_template('acteur_edit.html', form=form)


@app.route('/acteur/delete/<int:id>')
@login_required
def acteur_delete(id):
    # Logic to display roles
    pass






@app.route('/rollen', methods=['GET'])
def rollen():
    # roles = Rol.query \
    #     .join(Film, Rol.film_id == Film.id) \
    #     .join(Acteur, Rol.acteur_id == Acteur.id) \
    #     .add_columns(Rol.id, Rol.personage, Film.titel, Acteur.voornaam, Acteur.achternaam) \
    #     .all()
    
    roles = db.session.query(Rol, Film.titel, Acteur.voornaam, Acteur.achternaam)\
                  .join(Film, Rol.film_id == Film.id)\
                  .join(Acteur, Rol.acteur_id == Acteur.id)\
                  .all()

    return render_template('rollen.html', roles=roles)

@app.route('/rol/add', methods=['GET', 'POST'])
@login_required
def rol_add():
    form = RolForm()
    form.acteur_id.choices = [(0, 'Choose...')] + [(a.id, a.voornaam + ' ' + a.achternaam) for a in Acteur.query.all()]
    form.film_id.choices = [(0, 'Choose...')] + [(f.id, f.titel) for f in Film.query.all()]

    if form.validate_on_submit():
        # Create a new Rol instance with all the form fields
        rol = Rol(
            acteur_id=form.acteur_id.data, 
            film_id=form.film_id.data,
            personage=form.personage.data
        )
        db.session.add(rol)
        db.session.commit()
        flash('De Rol is succesvol toegevoegd!', 'success')
        return redirect(url_for('main.rollen'))
    
    return render_template('rol_add.html', form=form)


@app.route('/rol/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def rol_edit(id):
    rol = Rol.query.get_or_404(id)
    form = RolForm(obj=rol)
    
    # if form.validate_on_submit():
    #     acteur.voornaam = form.voornaam.data
    #     acteur.achternaam = form.achternaam.data
        
    #     db.session.commit()
    #     flash('De acteur is succesvol bijgewerkt!', 'success')
    #     return redirect(url_for('main.rollen', id=rol.id))
    
    return render_template('rol_edit.html', form=form)

@app.route('/rol/delete/<int:id>')
@login_required
def rol_delete(id):
    # Logic to display roles
    pass