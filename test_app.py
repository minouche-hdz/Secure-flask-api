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

def test_register_user_validation(test_client):
    """Teste la validation des entrées lors de l'enregistrement."""
    # Nom d'utilisateur trop court
    rv = register_user(test_client, 'ab', 'password123')
    assert rv.status_code == 400
    response_data = json.loads(rv.data)
    assert "Erreurs de validation" in response_data['msg']
    assert "Length must be between 3 and 80." in response_data['errors']['username'][0]

    # Mot de passe trop court
    rv = register_user(test_client, 'testuser2', 'pass')
    assert rv.status_code == 400
    response_data = json.loads(rv.data)
    assert "Erreurs de validation" in response_data['msg']
    assert "Shorter than minimum length 6." in response_data['errors']['password'][0]

    # Pas de JSON
    rv = test_client.post('/register', data='not json', content_type='text/plain')
    assert rv.status_code == 400
    response_data = json.loads(rv.data)
    assert response_data['msg'] == "Type de contenu doit être application/json"

def test_login_user_validation(test_client):
    """Teste la validation des entrées lors de la connexion."""
    # Pas de JSON
    rv = test_client.post('/login', data='not json', content_type='text/plain')
    assert rv.status_code == 400
    response_data = json.loads(rv.data)
    assert response_data['msg'] == "Type de contenu doit être application/json"

def test_error_handlers(test_client):
    """Teste les gestionnaires d'erreurs."""
    # Teste la route 404
    rv = test_client.get('/nonexistent_route')
    assert rv.status_code == 404
    response_data = json.loads(rv.data)
    assert response_data['msg'] == "Ressource non trouvée"

    # Teste la route 400 (déjà couverte par les tests de validation, mais on peut ajouter un cas générique)
    rv = test_client.post('/register', data='{"username": "a"}', content_type='application/json')
    assert rv.status_code == 400
    response_data = json.loads(rv.data)
    assert "Erreurs de validation" in response_data['msg']

def test_cors_headers(test_client):
    """Teste les en-têtes CORS."""
    rv = test_client.get('/', headers={'Origin': 'http://localhost:3000'})
    assert rv.status_code == 200
    assert 'Access-Control-Allow-Origin' in rv.headers
    assert rv.headers['Access-Control-Allow-Origin'] == 'http://localhost:3000'
