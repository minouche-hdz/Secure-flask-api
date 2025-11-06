import pytest
from app import create_app, db, User # Importe create_app, db et User
from flask_jwt_extended import create_access_token
import json

@pytest.fixture(scope='module')
def test_client():
    # Configure l'application pour les tests
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
    app = create_app(test_config)

    with app.test_client() as client:
        with app.app_context():
            # Accède à db et User via l'instance d'application
            from app import db, User # Importe db et User ici
            db.create_all() # Crée les tables pour la base de données en mémoire
        yield client
        with app.app_context():
            from app import db # Importe db ici pour drop_all
            db.drop_all() # Supprime les tables après les tests

def register_user(client, username, password):
    return client.post(
        '/register',
        data=json.dumps({'username': username, 'password': password}),
        content_type='application/json'
    )

def login_user(client, username, password):
    return client.post(
        '/login',
        data=json.dumps({'username': username, 'password': password}),
        content_type='application/json'
    )

def test_home_route(test_client):
    """Teste la route racine."""
    rv = test_client.get('/')
    assert rv.status_code == 200
    response_data = json.loads(rv.data)
    assert response_data['message'] == "Bienvenue sur l'API RESTful sécurisée !"

def test_register_user(test_client):
    """Teste l'enregistrement d'un nouvel utilisateur."""
    rv = register_user(test_client, 'testuser', 'password123')
    assert rv.status_code == 201
    response_data = json.loads(rv.data)
    assert response_data['msg'] == "Utilisateur enregistré avec succès"

    # Tente d'enregistrer le même utilisateur à nouveau
    rv = register_user(test_client, 'testuser', 'password123')
    assert rv.status_code == 409
    response_data = json.loads(rv.data)
    assert response_data['msg'] == "Nom d'utilisateur déjà pris"

def test_login_user(test_client):
    """Teste la connexion d'un utilisateur."""
    register_user(test_client, 'loginuser', 'loginpassword')
    rv = login_user(test_client, 'loginuser', 'loginpassword')
    assert rv.status_code == 200
    response_data = json.loads(rv.data)
    assert "access_token" in response_data

    # Mauvais mot de passe
    rv = login_user(test_client, 'loginuser', 'wrongpassword')
    assert rv.status_code == 401
    response_data = json.loads(rv.data)
    assert response_data['msg'] == "Mauvais nom d'utilisateur ou mot de passe"

    # Mauvais nom d'utilisateur
    rv = login_user(test_client, 'wronguser', 'loginpassword')
    assert rv.status_code == 401
    response_data = json.loads(rv.data)
    assert response_data['msg'] == "Mauvais nom d'utilisateur ou mot de passe"

def test_protected_route(test_client):
    """Teste l'accès à une route protégée."""
    # Accès sans token
    rv = test_client.get('/protected')
    assert rv.status_code == 401

    # Accès avec un token valide
    register_user(test_client, 'protecteduser', 'protectedpassword')
    login_rv = login_user(test_client, 'protecteduser', 'protectedpassword')
    access_token = json.loads(login_rv.data)['access_token']

    rv = test_client.get(
        '/protected',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    assert rv.status_code == 200
    response_data = json.loads(rv.data)
    assert response_data['logged_in_as'] == "protecteduser"
