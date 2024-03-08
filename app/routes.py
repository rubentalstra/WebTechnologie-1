import os
import secrets
from flask import Blueprint, current_app, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from markupsafe import Markup
from .models import Acteur, Citaat, Gebruiker, Film, Regisseur, Rol
from .forms import ActeurForm, CitaatForm, FilmForm, LoginForm, RegisseurForm, RegistratieForm, RolForm
from . import db, bcrypt

app = Blueprint('main', __name__)

@app.route('/')
def index():
    films = Film.query.all()
    return render_template('index.html', films=films)


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
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('Login mislukt. Controleer e-mail en wachtwoord.', 'danger')
    
    return render_template('auth/login.html', form=form)


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
    return render_template('auth/register.html', form=form)



@app.route('/film/<int:id>', methods=['GET', 'POST'])
def film_detail(id):
    film = Film.query.get_or_404(id)
    quotes = Citaat.query.filter_by(film_id=id).all()  # Fetch quotes related to the film
    rollen = Rol.query.join(Acteur).filter(Rol.film_id==id).all()
    
    form = CitaatForm()
    if form.validate_on_submit():
        new_quote = Citaat(inhoud=form.inhoud.data, film_id=id)
        db.session.add(new_quote)
        db.session.commit()
        flash('Quote successfully added.', 'success')
        return redirect(url_for('main.film_detail', id=id))  # Refresh the page to show the new quote
    
    return render_template('films/film_detail.html', film=film, rollen=rollen, quotes=quotes, form=form)



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/film_pics', picture_fn)

    # You might need to add some resizing logic here with Pillow

    form_picture.save(picture_path)
    return picture_fn
   
@app.route('/film/add', methods=['GET', 'POST'])
@login_required
def film_add():
    form = FilmForm()
    form.regisseur_id.choices = [(0, 'Choose...')] + [(r.id, r.voornaam + ' '  + r.achternaam) for r in Regisseur.query.all()]

    if form.validate_on_submit():
        if form.poster.data:
            poster_file = save_picture(form.poster.data)
            film = Film(
                titel=form.titel.data,
                regisseur_id=form.regisseur_id.data,
                jaar=form.jaar.data,
                trailer_url=form.trailer_url.data,
                bezoekers=form.bezoekers.data,
                omzet=form.omzet.data,
                overzicht=form.overzicht.data,
                poster_url=poster_file  # Save the path of the uploaded image
            )
        else:
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
    return render_template('films/film_add.html', title='Film Toevoegen', form=form)


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
    return render_template('films/film_add_quote.html', form=form, film_id=film_id)



@app.route('/film/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_film(id):
    film = Film.query.get_or_404(id)
    form = FilmForm(obj=film)

    form.regisseur_id.choices = [(0, 'Choose...')] + [(r.id, r.voornaam + ' ' + r.achternaam) for r in Regisseur.query.all()]

    if form.validate_on_submit():
        if form.poster.data:
            # Remove old image if exists
            if film.poster_url:
                old_image_path = os.path.join(current_app.root_path, 'static/film_pics', film.poster_url)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # Save new image and update poster_url
            picture_file = save_picture(form.poster.data)
            film.poster_url = picture_file

        # Update other film attributes
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
    
    return render_template('films/film_edit.html', form=form, film=film)




@app.route('/film/delete/<int:id>')
@login_required
def delete_film(id):
    film = Film.query.get_or_404(id)
    
    # Delete associated roles
    Rol.query.filter_by(film_id=id).delete()
    
    # Delete associated quotes (citaten)
    Citaat.query.filter_by(film_id=id).delete()
    
    # Remove film image if it exists
    if film.poster_url:
        image_path = os.path.join(current_app.root_path, 'static/film_pics', film.poster_url)
        try:
            os.remove(image_path)
        except OSError:
            flash('Error while deleting the image file.', 'warning')

    # Now, delete the film
    db.session.delete(film)
    db.session.commit()
    flash('Film successfully deleted.', 'success')
    return redirect(url_for('main.index'))




@app.route('/regisseurs', methods=['GET'])
def regisseurs():
    regisseurs = Regisseur.query.all()  # Fetch all regisseurs
    return render_template('regisseurs/regisseurs.html', regisseurs=regisseurs)


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
    return render_template('regisseurs/regisseur_add.html', form=form)


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
    
    return render_template('regisseurs/regisseur_edit.html', form=form)


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
    return render_template('acteurs/acteurs.html', acteurs=acteurs)

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
    return render_template('acteurs/acteur_add.html', form=form)


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
    
    return render_template('acteurs/acteur_edit.html', form=form)


@app.route('/acteur/delete/<int:id>', methods=['GET'])
@login_required
def acteur_delete(id):
    acteur = Acteur.query.get_or_404(id)
    roles = Rol.query.filter_by(acteur_id=id).all()

    if roles:
        # Actor has roles, construct a message indicating in which films
        roles_info = "<br>- " + "<br>- ".join([f"'{rol.personage}' in '{Film.query.get(rol.film_id).titel}'" for rol in roles])
        flash(Markup(f'Cannot delete actor because they are assigned to roles:<br>{roles_info}'), 'danger')
        return redirect(url_for('main.acteurs'))  # Redirect to actor's detail page or another relevant page
    else:
        # Safe to delete actor
        db.session.delete(acteur)
        db.session.commit()
        flash('Actor successfully deleted', 'success')
        return redirect(url_for('main.acteurs'))  # Redirect to the list of actors or another relevant page







@app.route('/rol/add/<int:film_id>', methods=['GET', 'POST'])  # New route to handle specific film ID
@login_required
def rol_add(film_id):
    form = RolForm()
    form.acteur_id.choices = [(0, 'Choose...')] + [(a.id, a.voornaam + ' ' + a.achternaam) for a in Acteur.query.all()]

    if form.validate_on_submit():
        rol = Rol(
            acteur_id=form.acteur_id.data, 
            film_id=film_id,
            personage=form.personage.data
        )
        db.session.add(rol)
        db.session.commit()
        flash('De Rol is succesvol toegevoegd!', 'success')
        return redirect(url_for('main.film_detail', id=film_id))
    
    return render_template('films/film_rol_add.html', form=form, film_id=film_id)


@app.route('/rol/edit/<int:id>', methods=['GET', 'POST'])
@login_required  
def rol_edit(id):
    rol = Rol.query.get_or_404(id)
    form = RolForm(obj=rol)
    
    # Update choices for acteur_id
    form.acteur_id.choices = [(a.id, a.voornaam + ' ' + a.achternaam) for a in Acteur.query.order_by(Acteur.voornaam).all()]
    
    if request.method == 'POST' and form.validate_on_submit():
        rol.acteur_id = form.acteur_id.data
        rol.personage = form.personage.data
        db.session.commit()
        flash('Rol successfully updated!', 'success')
        return redirect(url_for('main.film_detail', id=rol.film_id))
    
    return render_template('films/film_rol_edit.html', form=form, rol=rol)


@app.route('/rol/delete/<int:id>', methods=['GET'])
@login_required
def rol_delete(id):
    rol = Rol.query.get_or_404(id)
    film_id = rol.film_id
    db.session.delete(rol)
    db.session.commit()
    flash('De Rol is succesvol verwijderd!', 'success')
    return redirect(url_for('main.film_detail', id=film_id))
