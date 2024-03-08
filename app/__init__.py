import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_bcrypt import Bcrypt

db: SQLAlchemy = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'mijngeheimesleutel'
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'


    from app.routes.acteur import acteur_bp
    from app.routes.auth import auth_bp
    from app.routes.film import film_bp
    from app.routes.main import main_bp
    from app.routes.regisseur import regisseur_bp

    app.register_blueprint(acteur_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(film_bp)
    app.register_blueprint(regisseur_bp)

    return app
