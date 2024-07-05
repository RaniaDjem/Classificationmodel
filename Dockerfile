# Utiliser une image officielle comme un parent
FROM python:3.9-slim


# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers requirements.txt et installer les dépendances
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . /app

# Exposer le port sur lequel l'application sera accessible
EXPOSE 8080

# Définir la commande pour lancer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
