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
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
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
        width: 100%;
        max-width: 300px;
        margin: 0 auto;
        display: block;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
    }
    .result-box {
        background: linear-gradient(145deg, #f0f8ff, #e6f2ff);
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0, 105, 217, 0.2);
        border: 2px solid #4a90e2;
        color: #2c3e50;
        margin: 20px auto;
        width: 100%;
        max-width: 500px;
    }
    .result-box h3 {
        color: #4a90e2;
        margin-bottom: 20px;
        text-align: center;
        font-size: 1.5rem;
    }
    .result-box p {
        margin-bottom: 15px;
        font-size: 1.1rem;
        text-align: center;
    }
    .upload-box {
        background: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        margin: 20px auto;
        width: 100%;
        max-width: 500px;
        text-align: center;
    }
    .upload-box h3 {
        color: #2c3e50;
        margin-bottom: 15px;
        font-size: 1.3rem;
    }
    .stImage {
        max-width: 300px;
        margin: 0 auto;
        display: block;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    .image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin: 20px auto;
        padding: 15px;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 16px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    }
    .main-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 20px;
    }
    .footer {
        text-align: center;
        margin-top: 40px;
        color: #666;
        padding: 20px;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Set up the title and layout
st.title("🥔 Potato Disease Detection")
st.markdown("""
    <div style='text-align: center; color: #8B4513; margin-bottom: 30px;'>
        <p style='font-size: 1.2rem;'>Upload a potato leaf image to detect diseases like Early Blight and Late Blight</p>
    </div>
""", unsafe_allow_html=True)

# File upload section with custom styling
st.markdown("""
    <div class="upload-box">
        <h3>Upload Potato Leaf Image</h3>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "png", "jpeg"])

# Prediction logic
if uploaded_file is not None:
    # Create a centered container for the image and results
    st.markdown('<div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">', unsafe_allow_html=True)
    
    # Display the uploaded image in a centered container
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    st.image(uploaded_file, caption="Uploaded Potato Leaf", width=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("🔍 Analyzing the image...")
    
    # Send the image to the backend API
    try:
        response = requests.post(
            "http://localhost:8000/predict",
            files={"file": uploaded_file.getvalue()}
        )
        
        if response.status_code == 200:
            prediction = response.json()
            
            # Check if model is stuck on one class
            probabilities = prediction['probabilities']
            max_prob = max(probabilities.values())
            min_prob = min(probabilities.values())
            is_stuck = max_prob > 0.95 and min_prob < 0.05
            
            # Create probability bars
            prob_bars = ""
            for class_name, prob in probabilities.items():
                width = prob * 100
                color = "#4a90e2" if class_name == prediction['class'] else "#50c878"
                prob_bars += f"""
                    <div style="margin: 10px 0;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span><strong>{class_name}:</strong></span>
                            <span>{width:.2f}%</span>
                        </div>
                        <div style="background: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden;">
                            <div style="background: {color}; width: {width}%; height: 100%; transition: width 0.5s ease;"></div>
                        </div>
                    </div>
                """
            
            warning_message = ""
            if is_stuck:
                warning_message = """
                    <div style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 8px; margin-top: 15px;">
                        ⚠️ Warning: The model seems to be very confident in this prediction. This might indicate a potential issue with the model's training or input processing.
                    </div>
                """
            
            st.markdown(
                f"""
                <div class="result-box">
                    <h3>Detection Result</h3>
                    <p><strong>Predicted Disease:</strong> {prediction['class']}</p>
                    <p><strong>Confidence:</strong> {(prediction['confidence'] * 100):.2f}%</p>
                    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #4a90e2;">
                        <h4 style="color: #4a90e2; margin-bottom: 10px;">Class Probabilities:</h4>
                        {prob_bars}
                    </div>
                    {warning_message}
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.error("❌ Error: Unable to process the image. Please try again.")
    
    except Exception as e:
        st.error(f"❌ Error: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Add footer with information
st.markdown("""
    <div class="footer">
        <p style="margin-bottom: 10px;">This application helps detect common potato plant diseases using AI</p>
        <p>Supported diseases: Early Blight, Late Blight, and Healthy plants</p>
    </div>
""", unsafe_allow_html=True)

# Close main container
st.markdown('</div>', unsafe_allow_html=True)