from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.forms.forms import RegisseurForm
from app.models.models import Regisseur
from app import db

regisseur_bp = Blueprint('regisseur', __name__, url_prefix='/regisseur')

@regisseur_bp.route('/', methods=['GET'])
def regisseurs():
    search_query = request.args.get('search', '')
    if search_query:
        regisseurs = Regisseur.query.filter(
            db.or_(
                Regisseur.voornaam.ilike(f'%{search_query}%'),
                Regisseur.achternaam.ilike(f'%{search_query}%')
            )
        ).all()
    else:
        regisseurs:list[Regisseur] = Regisseur.query.all()
    
    return render_template('regisseur/regisseurs.html', regisseurs=regisseurs)



@regisseur_bp.route('/add', methods=['GET', 'POST'])
@login_required
def regisseur_add():
    form: RegisseurForm = RegisseurForm()
    if form.validate_on_submit():
        regisseur = Regisseur(voornaam=form.voornaam.data, achternaam=form.achternaam.data)
        db.session.add(regisseur)
        db.session.commit()
        flash('De regisseur is succesvol toegevoegd!', 'success')
        return redirect(url_for('regisseur.regisseurs'))
    return render_template('regisseur/regisseur_add.html', form=form)


@regisseur_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def regisseur_edit(id):
    regisseur:Regisseur = Regisseur.query.get_or_404(id)
    form = RegisseurForm(obj=regisseur)
    
    if form.validate_on_submit():
        regisseur.voornaam = form.voornaam.data
        regisseur.achternaam = form.achternaam.data
        
        db.session.commit()
        flash('De regisseur is succesvol bijgewerkt!', 'success')
        return redirect(url_for('regisseur.regisseurs', id=regisseur.id))
    
    return render_template('regisseur/regisseur_edit.html', form=form)


@regisseur_bp.route('/delete/<int:id>')
@login_required
def delete_regisseur(id):
    regisseur:Regisseur = Regisseur.query.get_or_404(id)
    if regisseur.films:
        flash('Cannot delete a Regisseur connected to films.', 'danger')
    else:
        db.session.delete(regisseur)
        db.session.commit()
        flash('Regisseur successfully deleted.', 'success')
    return redirect(url_for('regisseur.regisseurs'))