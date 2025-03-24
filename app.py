import streamlit as st
import requests
from PIL import Image
import io

# Custom CSS for styling
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, rgba(173, 216, 230, 0.7), rgba(135, 206, 235, 0.7), rgba(102, 205, 170, 0.7));
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stButton>button {
        background: linear-gradient(135deg, #4a90e2 0%, #50c878 100%);
        color: white;
        border: none;
        padding: 14px 28px;
        border-radius: 32px;
        font-size: 1.2rem;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1), 0 6px 10px rgba(0, 0, 0, 0.05);
        transition: transform 0.4s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
    }
    .result-box {
        background: linear-gradient(145deg, #f0f8ff, #e6f2ff);  /* Light blue gradient background */
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0, 105, 217, 0.2);  /* Enhanced shadow */
        border: 2px solid #4a90e2;  /* Added border */
        color: #2c3e50;  /* Dark text color for better readability */
    }
    .result-box h3 {
        color: #4a90e2;  /* Blue color for the heading */
        margin-bottom: 15px;
    }
    .result-box p {
        margin-bottom: 10px;
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Set up the title and layout
st.title("🌱 Plant Disease Prediction")

# File upload section
st.subheader("Upload an Image of a Plant Leaf")
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "png", "jpeg"])

# Prediction logic
if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    st.write("Analyzing the image...")
    
    # Send the image to the backend API
    try:
        # Corrected URL to match FastAPI server port
        response = requests.post(
            "http://localhost:8000/predict",
            files={"file": uploaded_file.getvalue()}
        )
        
        if response.status_code == 200:
            prediction = response.json()
            st.markdown(
                f"""
                <div class="result-box">
                    <h3>Prediction Result:</h3>
                    <p><strong>Class:</strong> {prediction['class']}</p>
                    <p><strong>Confidence:</strong> {(prediction['confidence'] * 100):.2f}%</p>
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.error("Error: Unable to process the image. Please try again.")
    
    except Exception as e:
        st.error(f"Error: {e}")