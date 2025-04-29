# app.py
import streamlit as st
import os
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
from medical_chatbot import run_medical_chatbot  # Import the medical chatbot function

# Load environment variables
load_dotenv()

# Configure the API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    api_key = "YOUR_API_KEY"  # Replace with your actual API key if not using .env
genai.configure(api_key=api_key)

def get_gemini_vision_response(input_text, image):
    """Function to get Gemini's response for image analysis"""
    model = genai.GenerativeModel('gemini-pro-vision')
    if input_text != "":
        response = model.generate_content([input_text, image])
    else:
        response = model.generate_content(image)
    return response.text

def run_image_analysis():
    """Main function to run the image analysis page"""
    st.set_page_config(page_title="Medical Image Analysis", page_icon="🔍")
    
    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            font-family: 'Arial', sans-serif;
            color: #2c3e50;
        }
        .response-container {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #0066cc;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # App header
    st.markdown("<h1 class='main-header'>Medical Image Analysis 🔍</h1>", unsafe_allow_html=True)
    st.markdown("Upload a medical image and I'll provide an analysis")
    
    # Text input for providing context to the image
    input_text = st.text_input("Describe what you'd like to know about this medical image:", key="image_input")
    
    # Image uploader
    uploaded_file = st.file_uploader("Upload a medical image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Medical Image", use_column_width=True)
        
        # Add a medical context to ensure responses focus on medical aspects
        if st.button("Analyze Medical Image"):
            # Combine user input with medical context
            medical_context = "This is a medical image. "
            if input_text:
                full_prompt = medical_context + input_text
            else:
                full_prompt = medical_context + "Provide a medical analysis of this image. Only discuss medical aspects."
            
            with st.spinner("Analyzing medical image..."):
                # Get response from Gemini Vision
                try:
                    response = get_gemini_vision_response(full_prompt, image)
                    
                    st.markdown("### Analysis Result:")
                    st.markdown(f"""<div class="response-container">{response}</div>""", unsafe_allow_html=True)
                    
                    # Disclaimer
                    st.markdown("""
                    **Important Disclaimer:** This analysis is provided by an AI system and is not a substitute 
                    for professional medical diagnosis. Please consult with a qualified healthcare provider for 
                    proper medical evaluation.
                    """)
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
    
    # Sidebar with information
    with st.sidebar:
        st.header("About Medical Image Analysis")
        st.info("""
        This tool uses AI to analyze medical images and provide information based on visual data.
        
        **Important Disclaimer:** This application provides general information and is not a substitute for professional medical advice, diagnosis, or treatment.
        """)
        
        st.header("Image Analysis Tips")
        st.markdown("""
        - Upload clear, well-lit images
        - Only upload medical images (X-rays, skin conditions, etc.)
        - Provide context about what you're looking for
        - Remember this is for educational purposes only
        """)
        
        # Navigation to medical chatbot
        st.header("Navigation")
        if st.button("Go to Medical Chatbot"):
            st.session_state.app_mode = "medical_chatbot"
            st.rerun()

def main():
    # Initialize app_mode in session state if it doesn't exist
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "image_analysis"  # Default to image analysis
    
    # Route to the appropriate page based on app_mode
    if st.session_state.app_mode == "medical_chatbot":
        run_medical_chatbot()
    else:
        run_image_analysis()

if __name__ == "__main__":
    main()