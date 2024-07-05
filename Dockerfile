FROM python:3.9-slim


# répertoire de travail
WORKDIR /app

# Copie des fichiers requirements.txt et installer les dépendances
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste de l'application
COPY . /app

# Exposition du port sur lequel l'application sera accessible
EXPOSE 8080

# lancer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
