from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",  # Include all possible frontend origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow all frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = tf.keras.models.load_model("model_name.h5")

CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]

@app.get("/ping")
async def ping():
    return "Hello, I am alive"

def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    # Resize image to 256x256 (assuming this is the expected input size)
    image = tf.image.resize(image, [256, 256])
    # Normalize pixel values to [0, 1]
    image = image / 255.0
    return image

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
):
    # Read and process the image
    image = read_file_as_image(await file.read())
    img_batch = np.expand_dims(image, 0)
    
    # Get the prediction
    predictions = MODEL.predict(img_batch)

    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    confidence = np.max(predictions[0])

    # Log prediction details for debugging
    print(f"Predicted Class: {predicted_class}")
    print(f"Confidence: {confidence}")

    # Return the prediction result as a response
    return {
        "class": predicted_class,
        "confidence": float(confidence)
    }

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)
