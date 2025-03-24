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

MODEL = tf.keras.models.load_model("production.h5")

CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]

@app.get("/ping")
async def ping():
    return "Hello, I am alive"

def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    # Resize image to 224x224 (MobileNetV2 expected input size)
    image = tf.image.resize(image, [224, 224])
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

    # Get all class probabilities
    class_probabilities = predictions[0]
    predicted_class = CLASS_NAMES[np.argmax(class_probabilities)]
    confidence = np.max(class_probabilities)

    # Detailed debugging information
    print("\n=== Detailed Prediction Information ===")
    print(f"Input Image Shape: {image.shape}")
    print(f"Model Output Shape: {predictions.shape}")
    print(f"Raw Model Output: {predictions}")
    print("\nPrediction Details:")
    print(f"Predicted Class: {predicted_class}")
    print(f"Confidence: {confidence}")
    print("\nAll Class Probabilities:")
    for class_name, prob in zip(CLASS_NAMES, class_probabilities):
        print(f"{class_name}: {prob:.4f}")
    
    # Check if probabilities sum to 1
    prob_sum = np.sum(class_probabilities)
    print(f"\nSum of probabilities: {prob_sum:.4f}")
    
    # Check if any probabilities are exactly 0 or 1
    for class_name, prob in zip(CLASS_NAMES, class_probabilities):
        if prob < 0.0001:
            print(f"Warning: {class_name} has very low probability: {prob:.4f}")
        elif prob > 0.9999:
            print(f"Warning: {class_name} has very high probability: {prob:.4f}")

    # Return the prediction result as a response
    return {
        "class": predicted_class,
        "confidence": float(confidence),
        "probabilities": {
            class_name: float(prob) 
            for class_name, prob in zip(CLASS_NAMES, class_probabilities)
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)
