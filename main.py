from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from google.cloud import storage
from tensorflow.keras.models import load_model
import os
import logging

app = FastAPI()
model = None

logging.basicConfig(level=logging.INFO)

@app.on_event("startup")
async def startup_event():
    await load_model_on_startup()

async def load_model_on_startup():
    global model
    bucket_name = 'bucket-de-machinelearning'
    model_path = 'mon_modele.h5'  
    local_model_path = '/tmp/model.h5'

    # Creation du directory s'il n'existe pas
    os.makedirs(os.path.dirname(local_model_path), exist_ok=True)

    # GCS client init
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(model_path)

    # Load le model dans un fichier dans un local temporary file
    blob.download_to_filename(local_model_path)

    # load le model
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

app.mount("/static", StaticFiles(directory="./static"), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
