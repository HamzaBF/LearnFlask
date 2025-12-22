from datetime import timedelta
from flask import Flask, render_template, redirect, request, url_for,session,flash
from flask.cli import with_appcontext
from app.modeles import Projet, Avis, Contact,db,projets,avis
from os import path
import click
from app.forms import FormAvis

from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from app.modeles import db, Utilisateur, Role
from flask_babel import Babel
from flask_jwt_extended import JWTManager

from app import portfolio,admin,api_0_1
from app import client

def create_app(conf=None):
    app = Flask(__name__, 
            instance_path=path.abspath('instance'), 
            instance_relative_config=True)
    app.config.from_pyfile('config.py')
    if conf:
        app.config.update(conf)
    app.logger.setLevel(app.config['PORTFOLIO_NIVEAU_LOG'])
    # app.secret_key = app.config['SECRET_KEY']
    # app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI']
    db.init_app(app)

    Babel(app)

    app.security = Security(
        app, SQLAlchemyUserDatastore(db, Utilisateur, Role)
    )

    JWTManager(app)
    app.logger.info('Sécurité ok')

    with app.app_context():
        if app.config['TESTING']:
            db.create_all()
            db.session.add_all([Projet(**p) for p in projets])
            db.session.add_all([Avis(**a) for a in avis])
            db.session.commit()
        app.security.datastore.find_or_create_role(name="admin")
        app.security.datastore.find_or_create_role(name="client")
        db.session.commit()
        admin_mail = app.config['ADMIN_MAIL']
        if not app.security.datastore.find_user(email=admin_mail):
            app.security.datastore.create_user(
                email=admin_mail,
                password=hash_password(app.config['ADMIN_PASSE_INITIAL']),
                roles=['admin'],
                logo=app.config['ADMIN_LOGO'])
            db.session.commit()


    @app.errorhandler(404)
    @app.route("/oups")
    def introuvable(e=None):
        return render_template('introuvable.html')

    @app.before_request
    def cookies_pref():
        if 'cookies' in request.args:
            pref = request.args['cookies']
            session['cookies'] = pref
            session.permanent = pref=='y'
    
    app.register_blueprint(portfolio.bp)
    app.register_blueprint(client.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(api_0_1.bp)
    app.add_url_rule('/', endpoint='portfolio.index')

    @app.cli.command(help="Modifie un mot de passe utilisateur.")
    @click.argument('email')
    @click.argument('passe')
    @with_appcontext
    def mdp(email, passe):
        utilisateur = app.security.datastore.find_user(email=email)
        if not utilisateur:
            print("Utilisateur inconnu.")
            return -1
        utilisateur.password = hash_password(passe)
        db.session.commit()
        print("Mot de passe modifié avec succès.")

    # if you nedd to use click from cli use this flask mdp hamza@gmail.com hamza1

    return app