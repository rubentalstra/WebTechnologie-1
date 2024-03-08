from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from markupsafe import Markup
from app.forms.forms import ActeurForm
from app.models.models import Acteur, Film, Rol
from app import db

acteur_bp = Blueprint('acteur', __name__, url_prefix='/acteur')

@acteur_bp.route('/', methods=['GET'])
def acteurs():
    search_query = request.args.get('search', '')
    if search_query:
        acteurs:list[Acteur] = Acteur.query.filter(
            db.or_(
                Acteur.voornaam.ilike(f'%{search_query}%'),
                Acteur.achternaam.ilike(f'%{search_query}%')
            )
        ).all()
    else:
        acteurs:list[Acteur] = Acteur.query.all()
    
    return render_template('acteur/acteurs.html', acteurs=acteurs)


@acteur_bp.route('/add', methods=['GET', 'POST'])
@login_required
def acteur_add():
    form:ActeurForm = ActeurForm()
    if form.validate_on_submit():
        acteur:Acteur = Acteur(voornaam=form.voornaam.data, achternaam=form.achternaam.data)
        db.session.add(acteur)
        db.session.commit()
        flash('De acteur is succesvol toegevoegd!', 'success')
        return redirect(url_for('acteur.acteurs'))
    return render_template('acteur/acteur_add.html', form=form)


@acteur_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def acteur_edit(id):
    acteur:Acteur = Acteur.query.get_or_404(id)
    form = ActeurForm(obj=acteur)
    
    if form.validate_on_submit():
        acteur.voornaam = form.voornaam.data
        acteur.achternaam = form.achternaam.data
        
        db.session.commit()
        flash('De acteur is succesvol bijgewerkt!', 'success')
        return redirect(url_for('acteur.acteurs', id=acteur.id))
    
    return render_template('acteur/acteur_edit.html', form=form)


@acteur_bp.route('/delete/<int:id>', methods=['GET'])
@login_required
def acteur_delete(id):
    acteur:list[Acteur] = Acteur.query.get_or_404(id)
    roles:list[Rol] = Rol.query.filter_by(acteur_id=id).all()

    if roles:
        # Actor has roles, construct a message indicating in which films
        roles_info = "<br>- " + "<br>- ".join([f"'{rol.personage}' in '{Film.query.get(rol.film_id).titel}'" for rol in roles])
        flash(Markup(f'Cannot delete actor because they are assigned to roles:<br>{roles_info}'), 'danger')
        return redirect(url_for('acteur.acteurs'))  # Redirect to actor's detail page or another relevant page
    else:
        # Safe to delete actor
        db.session.delete(acteur)
        db.session.commit()
        flash('Actor successfully deleted', 'success')
        return redirect(url_for('acteur.acteurs'))  # Redirect to the list of actors or another relevant page


