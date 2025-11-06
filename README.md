# Secure Flask API

Ce projet est une API RESTful simple développée avec Flask, conçue pour démontrer les bonnes pratiques de développement backend et de sécurité.

## 🚀 Fonctionnalités

*   Point de terminaison racine simple (`/`)
*   Structure de projet de base pour une API Flask

## 🛠️ Technologies Utilisées

*   **Python**
*   **Flask** : Micro-framework web pour Python
*   **Flask-SQLAlchemy** : ORM pour interagir avec la base de données
*   **Flask-JWT-Extended** : Pour l'authentification basée sur les tokens JWT
*   **Werkzeug** : Pour le hachage des mots de passe
*   **python-dotenv** : Pour la gestion des variables d'environnement
*   **psycopg2-binary** : Adaptateur PostgreSQL pour Python

## ⚙️ Installation et Lancement

Ce projet peut être lancé en utilisant Docker Compose, ce qui simplifie la gestion de la base de données PostgreSQL et de l'application Flask.

### Prérequis

*   [Docker](https://docs.docker.com/get-docker/) et [Docker Compose](https://docs.docker.com/compose/install/) installés.

### Étapes de Lancement

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/minouche-hdz/secure-flask-api.git
    cd secure-flask-api
    ```

2.  **Configuration des variables d'environnement :**
    *   Créez un fichier `.env` à la racine du projet avec les variables d'environnement suivantes (remplacez les valeurs par les vôtres). Ces variables seront utilisées par Docker Compose.
        ```
        DATABASE_URL="postgresql://user:password@db:5432/mydatabase"
        JWT_SECRET_KEY="your-super-secret-jwt-key"
        ```
        *(Note : `JWT_SECRET_KEY` doit être une chaîne de caractères longue et aléatoire. L'utilisateur et le mot de passe de la base de données sont définis dans `docker-compose.yml`.)*

3.  **Initialiser la base de données et lancer l'application avec Docker Compose :**
    ```bash
    docker-compose up --build -d
    docker-compose exec web flask db init
    docker-compose exec web flask db migrate -m "Initial migration"
    docker-compose exec web flask db upgrade
    ```
    *   `docker-compose up --build -d` : Construit les images Docker, crée et démarre les conteneurs en arrière-plan.
    *   `flask db init` : Initialise le répertoire des migrations.
    *   `flask db migrate -m "Initial migration"` : Crée la première migration basée sur le modèle `User`.
    *   `flask db upgrade` : Applique la migration à la base de données, créant la table `User`.

    L'API sera accessible à l'adresse `http://localhost:5001/`.

## 📝 Utilisation

### Point de terminaison racine
Accédez à `http://localhost:5001/` dans votre navigateur ou avec un outil comme `curl` pour voir le message de bienvenue :

```bash
curl http://localhost:5001/
```

### Enregistrement d'un utilisateur
```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "testuser", "password": "password123"}' http://localhost:5001/register
```

### Connexion d'un utilisateur et obtention d'un token JWT
```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "testuser", "password": "password123"}' http://localhost:5001/login
```
*(Copiez le `access_token` retourné.)*

### Accès à une route protégée avec le token
```bash
curl -X GET -H "Authorization: Bearer VOTRE_TOKEN_JWT_ICI" http://localhost:5001/protected
```

### Arrêter et supprimer les conteneurs Docker
```bash
docker-compose down
```

## 🚧 Prochaines Étapes

*   Mettre en œuvre des mesures de sécurité supplémentaires (validation des entrées, gestion des erreurs, CORS).
*   Ajouter d'autres fonctionnalités à l'API.

## ✅ Tests

Pour exécuter les tests unitaires et d'intégration, assurez-vous que les conteneurs Docker sont arrêtés (`docker-compose down`) ou que vous exécutez les tests dans un environnement virtuel séparé pour éviter les conflits de base de données.

1.  **Activer l'environnement virtuel (si vous n'utilisez pas Docker) :**
    ```bash
    source venv/bin/activate
    ```

2.  **Exécuter les tests :**
    ```bash
    pytest
    ```
    Les tests utiliseront une base de données SQLite en mémoire pour ne pas interférer avec votre base de données PostgreSQL principale.
