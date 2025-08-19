#!/bin/bash
# Script pour créer la structure du projet Flask

echo "📁 Création de la structure du projet Flask..."

# Fichiers Python
touch app.py models.py routes.py forms.py

# Dossiers static et templates
mkdir -p static/css static/js static/uploads
mkdir -p templates

# Fichier CSS
touch static/css/style.css

# Templates HTML
touch templates/base.html templates/login.html templates/dashboard.html 
templates/documents.html templates/users.html

# Fichiers de config
touch requirements.txt Procfile README.md

echo "✅ Structure du projet Flask créée avec succès !"

