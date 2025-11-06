# Utilise une image Python officielle comme base
FROM python:3.10-slim-buster

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier requirements.txt et installe les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste du code de l'application
COPY . .

# Expose le port sur lequel l'application Flask s'exécutera
EXPOSE 5001

# Commande par défaut pour lancer l'application (sera surchargée par docker-compose)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
