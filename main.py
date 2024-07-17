from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from google.cloud import storage
from tensorflow.keras.models import load_model
import os
import logging
import numpy as np
from PIL import Image
import cv2
import urllib.request
import matplotlib.pyplot as plt

app = FastAPI()
model = None
class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']  # Les noms des classes de votre modèle

logging.basicConfig(level=logging.INFO)

@app.on_event("startup")
async def startup_event():
    await load_model_on_startup()

async def load_model_on_startup():
    global model
    bucket_name = 'bucket-de-machinelearning'
    model_path = 'mon_modele.h5'  
    local_model_path = '/tmp/model.h5'

    # Création du répertoire s'il n'existe pas
    os.makedirs(os.path.dirname(local_model_path), exist_ok=True)

    # Initialisation du client GCS
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(model_path)

    # Télécharger le modèle dans un fichier temporaire local
    blob.download_to_filename(local_model_path)

    # Charger le modèle
    model = load_model(local_model_path)
    logging.info("Model loaded successfully.")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("./templates/index.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/status")
async def get_status():
    if model:
        return {"message": "Bonne nouvelle le modèle a bien été chargé."}
    else:
        return {"message": "Le modèle n'est pas chargé."}

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    if not model:
        return {"message": "Le modèle n'est pas chargé."}

    # Lire l'image téléchargée
    image = Image.open(file.file)
    image = np.array(image)
    
    # Redimensionner l'image à 32x32 pixels (ou la taille attendue par votre modèle)
    image = cv2.resize(image, (32, 32))

    # Normaliser l'image (Assurez-vous de mettre à jour mean et std selon votre modèle)
    mean = np.mean(image)
    std = np.std(image)
    image = (image - mean) / (std + 1e-7)

    # Ajouter une dimension supplémentaire car le modèle attend un lot d'images
    image = np.expand_dims(image, axis=0)

    # Faire une prédiction
    predictions = model.predict(image)
    predicted_class = predictions.argmax()

    return {"predicted_class": class_names[predicted_class]}

app.mount("/static", StaticFiles(directory="./static"), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
