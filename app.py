from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Bienvenue sur l'API RESTful sécurisée !"})

if __name__ == '__main__':
    app.run(debug=True)
