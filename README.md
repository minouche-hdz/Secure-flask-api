# Secure Flask API

Ce projet est une API RESTful simple développée avec Flask, conçue pour démontrer les bonnes pratiques de développement backend et de sécurité.

## 🚀 Fonctionnalités

*   Point de terminaison racine simple (`/`)
*   Structure de projet de base pour une API Flask

## 🛠️ Technologies Utilisées

*   **Python**
*   **Flask** : Micro-framework web pour Python
*   **python-dotenv** : Pour la gestion des variables d'environnement

## ⚙️ Installation et Lancement

Suivez ces étapes pour configurer et exécuter le projet localement :

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/minouche-hdz/secure-flask-api.git
    cd secure-flask-api
    ```

2.  **Créer et activer l'environnement virtuel :**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note : Le fichier `requirements.txt` sera créé ultérieurement.)*

4.  **Exécuter l'application Flask :**
    ```bash
    flask run
    ```

    L'API sera accessible à l'adresse `http://127.0.0.1:5000/`.

## 📝 Utilisation

Accédez à `http://127.0.0.1:5000/` dans votre navigateur ou avec un outil comme `curl` pour voir le message de bienvenue :

```bash
curl http://127.0.0.1:5000/
```

## 🚧 Prochaines Étapes

*   Ajouter la gestion des utilisateurs (enregistrement, connexion).
*   Implémenter l'authentification JWT.
*   Connecter l'API à une base de données (par exemple, PostgreSQL avec SQLAlchemy).
*   Ajouter des tests unitaires et d'intégration.
*   Mettre en œuvre des mesures de sécurité supplémentaires (validation des entrées, gestion des erreurs, CORS).
*   Conteneuriser l'application avec Docker.
