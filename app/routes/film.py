import os
import secrets
from flask import Blueprint, current_app, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.forms.forms import CitaatForm, FilmForm, RolForm
from app.models.models import Acteur, Citaat, Film, Regisseur, Rol
from app import db

film_bp = Blueprint('film', __name__, url_prefix='/film')



@film_bp.route('/<int:id>', methods=['GET'])
def film_detail(id):
    form = CitaatForm()
    film: Film = Film.query.get_or_404(id)
    quotes: list[Citaat] = Citaat.query.filter_by(film_id=id).all() 
    rollen = Rol.query.join(Acteur).filter(Rol.film_id==id).all()
    
    return render_template('film/film_detail.html', film=film, rollen=rollen, quotes=quotes, form=form)




def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/film_pics', picture_fn)

    form_picture.save(picture_path)
    return picture_fn
   
@film_bp.route('/add', methods=['GET', 'POST'])
@login_required
def film_add():
    form: FilmForm = FilmForm()
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
    return render_template('film/film_add.html', title='Film Toevoegen', form=form)




@film_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_film(id):
    film:Film = Film.query.get_or_404(id)
    form:FilmForm = FilmForm(obj=film)

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
        return redirect(url_for('film.film_detail', id=film.id))
    
    return render_template('film/film_edit.html', form=form, film=film)



@film_bp.route('/delete/<int:id>')
@login_required
def delete_film(id):
    film:Film = Film.query.get_or_404(id)
    
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






@film_bp.route('/<int:id>/add_quote', methods=['POST'])
@login_required
def film_add_quote(id):
    form:CitaatForm = CitaatForm()
    if form.validate_on_submit():
        new_quote = Citaat(inhoud=form.inhoud.data, film_id=id, user_id=current_user.id)
        db.session.add(new_quote)
        db.session.commit()
        flash('Quote successfully added.', 'success')
    return redirect(url_for('film.film_detail', id=id, tab='quotes'))





@film_bp.route('/quote/edit/<int:quote_id>', methods=['GET', 'POST'])
@login_required
def film_edit_quote(quote_id):
    quote:Citaat = Citaat.query.get_or_404(quote_id)
    if quote.user_id != current_user.id:
        flash('You do not have permission to edit this quote.', 'danger')
        return redirect(url_for('main.index'))
    
    form:CitaatForm = CitaatForm(obj=quote)
    if form.validate_on_submit():
        quote.inhoud = form.inhoud.data
        db.session.commit()
        flash('Quote successfully updated.', 'success')
        return redirect(url_for('film.film_detail', id=quote.film_id, tab='quotes'))
    return render_template('edit_quote.html', form=form)  # You'll need to create this template



@film_bp.route('/quote/delete/<int:quote_id>', methods=['GET'])
@login_required
def film_delete_quote(quote_id):
    quote:Citaat = Citaat.query.get_or_404(quote_id)
    if quote.user_id != current_user.id:
        flash('You do not have permission to delete this quote.', 'danger')
        return redirect(url_for('main.index'))
    db.session.delete(quote)
    db.session.commit()
    flash('Quote successfully deleted.', 'success')
    return redirect(url_for('film.film_detail', id=quote.film_id, tab='quotes'))





# ROL FILM

@film_bp.route('/rol/add/<int:film_id>', methods=['GET', 'POST'])  # New route to handle specific film ID
@login_required
def rol_add(film_id):
    form:RolForm = RolForm()
    form.acteur_id.choices = [(0, 'Choose...')] + [(a.id, a.voornaam + ' ' + a.achternaam) for a in Acteur.query.all()]

    if form.validate_on_submit():
        rol:Rol = Rol(
            acteur_id=form.acteur_id.data, 
            film_id=film_id,
            personage=form.personage.data
        )
        db.session.add(rol)
        db.session.commit()
        flash('De Rol is succesvol toegevoegd!', 'success')
        return redirect(url_for('film.film_detail', id=film_id, tab='actors-roles'))
    
    return render_template('film/film_rol_add.html', form=form, film_id=film_id)


@film_bp.route('/rol/edit/<int:id>', methods=['GET', 'POST'])
@login_required  
def rol_edit(id):
    rol:Rol = Rol.query.get_or_404(id)
    form:RolForm = RolForm(obj=rol)
    
    # Update choices for acteur_id
    form.acteur_id.choices = [(0, 'Choose...')] +  [(acteur.id, acteur.voornaam + ' ' + acteur.achternaam) for acteur in Acteur.query.order_by(Acteur.voornaam).all()]
    
    if request.method == 'POST' and form.validate_on_submit():
        rol.acteur_id = form.acteur_id.data
        rol.personage = form.personage.data
        db.session.commit()
        flash('Rol successfully updated!', 'success')
        return redirect(url_for('film.film_detail', id=rol.film_id, tab='actors-roles'))
    
    return render_template('film/film_rol_edit.html', form=form, rol=rol)


@film_bp.route('/rol/delete/<int:id>', methods=['GET'])
@login_required
def rol_delete(id):
    rol:Rol = Rol.query.get_or_404(id)
    film_id = rol.film_id
    db.session.delete(rol)
    db.session.commit()
    flash('De Rol is succesvol verwijderd!', 'success')
    return redirect(url_for('film.film_detail', id=film_id, tab='actors-roles'))