from fastapi import FastAPI
from google.cloud import storage
from tensorflow.keras.models import load_model
import os

app = FastAPI()
model = None

@app.on_event("startup")
async def startup_event():
    await load_model_on_startup()

async def load_model_on_startup():
    global model
    bucket_name = 'bucket-de-machinelearning'
    model_path = 'mon_modele.h5'  # Mettez à jour avec le chemin exact de votre modèle dans le bucket
    local_model_path = '/tmp/model.h5'

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(local_model_path), exist_ok=True)

    # Initialize the GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(model_path)

    # Download the model to a local temporary file
    blob.download_to_filename(local_model_path)

    # Load the model
    model = load_model(local_model_path)
    print("Model loaded successfully.")

@app.get("/")
async def root():
    if model:
        return {"message": "Model loaded successfully."}
    else:
        return {"message": "Model not loaded."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
