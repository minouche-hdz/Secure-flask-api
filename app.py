from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_cors import CORS # Importe Flask-CORS
import os
from datetime import timedelta
from dotenv import load_dotenv
import re # Pour la validation des entrées
from marshmallow import Schema, fields, validate, ValidationError # Pour la validation des entrées
from http import HTTPStatus # Pour les codes d'état HTTP

load_dotenv() # Charge les variables d'environnement du fichier .env

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        app.config.from_mapping(test_config)
    else:
        # Configuration de la base de données PostgreSQL
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
        app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app) # Initialise CORS pour l'application

    # Gestionnaire d'erreurs pour les erreurs 400 (Bad Request)
    @app.errorhandler(HTTPStatus.BAD_REQUEST)
    def bad_request(error):
        return jsonify({"msg": "Requête invalide", "errors": error.description}), HTTPStatus.BAD_REQUEST

    # Gestionnaire d'erreurs pour les erreurs 404 (Not Found)
    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def not_found(error):
        return jsonify({"msg": "Ressource non trouvée"}), HTTPStatus.NOT_FOUND

    # Gestionnaire d'erreurs pour les erreurs 500 (Internal Server Error)
    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    def internal_server_error(error):
        return jsonify({"msg": "Erreur interne du serveur"}), HTTPStatus.INTERNAL_SERVER_ERROR

    # Création des tables de la base de données pour le contexte d'application
    # Ceci est géré par Flask-Migrate en production, mais nécessaire pour les tests SQLite en mémoire
    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return jsonify({"message": "Bienvenue sur l'API RESTful sécurisée !"})

    # Schéma de validation pour l'enregistrement et la connexion
    class AuthSchema(Schema):
        username = fields.String(required=True, validate=validate.Length(min=3, max=80))
        password = fields.String(required=True, validate=validate.Length(min=6)) # Minimum 6 caractères pour le mot de passe

    # Route d'enregistrement
    @app.route('/register', methods=['POST'])
    def register():
        if not request.is_json:
            return jsonify({"msg": "Type de contenu doit être application/json"}), HTTPStatus.BAD_REQUEST
        try:
            AuthSchema().load(request.json)
        except ValidationError as err:
            return jsonify({"msg": "Erreurs de validation", "errors": err.messages}), HTTPStatus.BAD_REQUEST

        username = request.json.get('username')
        password = request.json.get('password')

        if User.query.filter_by(username=username).first():
            return jsonify({"msg": "Nom d'utilisateur déjà pris"}), HTTPStatus.CONFLICT

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"msg": "Utilisateur enregistré avec succès"}), HTTPStatus.CREATED

    # Route de connexion
    @app.route('/login', methods=['POST'])
    def login():
        if not request.is_json:
            return jsonify({"msg": "Type de contenu doit être application/json"}), HTTPStatus.BAD_REQUEST
        try:
            AuthSchema().load(request.json)
        except ValidationError as err:
            return jsonify({"msg": "Erreurs de validation", "errors": err.messages}), HTTPStatus.BAD_REQUEST

        username = request.json.get('username')
        password = request.json.get('password')

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            return jsonify({"msg": "Mauvais nom d'utilisateur ou mot de passe"}), HTTPStatus.UNAUTHORIZED

        access_token = create_access_token(identity=user.username)
        return jsonify(access_token=access_token), HTTPStatus.OK

    # Route protégée (exemple)
    @app.route('/protected', methods=['GET'])
    @jwt_required()
    def protected():
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), HTTPStatus.OK

    return app

# Modèle utilisateur
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
