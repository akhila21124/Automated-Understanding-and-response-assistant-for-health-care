import streamlit as st
import os
import pathlib
import textwrap
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    api_key = "AIzaSyDQGvldzoPny1ws_ZlLA-GM12loXA7rTfA"
genai.configure(api_key="AIzaSyDQGvldzoPny1ws_ZlLA-GM12loXA7rTfA")

# Function to get response from Gemini for medical queries
def get_medical_response(question):
    # Create a prompt that ensures medical-only responses
    medical_prompt = f"""
    You are MediAssist, a specialized medical chatbot designed to provide helpful information on medical topics only.
    
    Instructions:
    - Only respond to questions related to medical topics, health advice, symptoms, treatments, medications, or general wellness
    - If the query is not medical-related, politely explain that you can only provide information on medical topics
    - Always include a disclaimer that you're an AI assistant and not a replacement for professional medical advice
    - Provide evidence-based information when possible
    - Be compassionate and clear in your responses
    
    User Query: {question}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(medical_prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to get Gemini's response for image analysis
def get_gemini_vision_response(input_text, image):
    model = genai.GenerativeModel('gemini-1.5-pro')
    if input_text != "":
        response = model.generate_content([input_text, image])
    else:
        response = model.generate_content(image)
    return response.text

# Streamlit UI setup
st.set_page_config(page_title="AI Medical Assistant", page_icon="🩺")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-family: 'Arial', sans-serif;
        color: #2c3e50;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    .tab-content {
        padding: 20px 0;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        border-left: 5px solid #3498db;
    }
    .assistant-message {
        border-left: 5px solid #2ecc71;
    }
    .message-content {
        margin-left: 10px;
    }
    .disclaimer {
        font-size: 0.8rem;
        color: #7f8c8d;
        font-style: italic;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>AI Medical Assistant 🩺</h1>", unsafe_allow_html=True)

# Create tabs for different functionalities
tab1, tab2 = st.tabs(["Medical Chatbot", "Image Analysis"])

# Tab 1: Medical Chatbot
with tab1:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.markdown("### MediAssist Chatbot")
    st.markdown("Ask any medical questions you have, and I'll provide helpful information.")
    
    # Set this tab as active when interacting with it
    if tab1.active:
        st.session_state["active_tab"] = "medical"
    
    # Initialize chat history for medical bot
    if "medical_messages" not in st.session_state:
        st.session_state.medical_messages = []
        # Add welcome message
        welcome_message = {
            "role": "assistant", 
            "content": "Hello! I'm MediAssist, your AI medical assistant. How can I help you with your medical questions today? Please note that I can only provide information on medical topics, and my responses should not replace professional medical advice."
        }
        st.session_state.medical_messages.append(welcome_message)

    # Chat container for better styling
    chat_container = st.container()
    
    # Display chat history with improved styling
    with chat_container:
        for message in st.session_state.medical_messages:
            role_class = "user-message" if message["role"] == "user" else "assistant-message"
            with st.container():
                st.markdown(f"""
                <div class="chat-message {role_class}">
                    <div class="message-content">
                        <strong>{"You" if message["role"] == "user" else "MediAssist"}:</strong>
                        <div>{message["content"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # User input
    user_query = st.chat_input("Ask your medical question here...")

    # When user submits a question
    if user_query:
        # Add user message to chat history
        st.session_state.medical_messages.append({"role": "user", "content": user_query})
        
        # Process the query and get response
        with st.spinner("Generating response..."):
            response = get_medical_response(user_query)
            
            # Add assistant response to chat history
            st.session_state.medical_messages.append({"role": "assistant", "content": response})
        
        # Rerun to update the chat display
        st.rerun()
    
    # Control buttons - in columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Chat History", key="clear_medical"):
            # Keep only the welcome message
            welcome_message = {
                "role": "assistant", 
                "content": "Hello! I'm MediAssist, your AI medical assistant. How can I help you with your medical questions today? Please note that I can only provide information on medical topics, and my responses should not replace professional medical advice."
            }
            st.session_state.medical_messages = [welcome_message]
            st.rerun()
    
    with col2:
        if st.button("Example Questions", key="examples_medical"):
            st.session_state.show_examples = not st.session_state.get("show_examples", False)
            st.rerun()
    
    # Show example questions that users can click
    if st.session_state.get("show_examples", False):
        example_questions = [
            "What are common symptoms of the flu?",
            "How can I manage my migraine?",
            "What is hypertension?",
            "How often should I exercise for heart health?",
            "What are the side effects of ibuprofen?"
        ]
        
        st.markdown("### Example Questions")
        for question in example_questions:
            if st.button(question, key=f"q_{question}"):
                # Add the selected question to the chat as if the user had typed it
                st.session_state.medical_messages.append({"role": "user", "content": question})
                
                # Process the query and get response
                with st.spinner("Generating response..."):
                    response = get_medical_response(question)
                    st.session_state.medical_messages.append({"role": "assistant", "content": response})
                
                # Hide examples after selection
                st.session_state.show_examples = False
                st.rerun()
    
    # Add disclaimer at the bottom of the chat
    st.markdown("""
    <div class="disclaimer">
        <strong>Disclaimer:</strong> The information provided by this AI assistant is for educational purposes only 
        and should not replace professional medical advice, diagnosis, or treatment. 
        Always consult with a qualified healthcare provider for medical concerns.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Tab 2: Medical Image Analysis
with tab2:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.markdown("### Medical Image Analysis")
    st.markdown("Upload a medical image and I'll provide an analysis (only for medical images).")
    
    # Set this tab as active when interacting with it
    if tab2.active:
        st.session_state["active_tab"] = "image"
    
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
    
    st.markdown("</div>", unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.header("About AI Medical Assistant")
    st.info("""
    This application offers two main features:
    
    1. **MediAssist Chatbot**: A specialized medical chatbot that provides information on medical topics only.
    
    2. **Medical Image Analysis**: Upload medical images for AI-powered analysis.
    
    **Important Disclaimer:** This application provides general information and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.
    """)
    
    # Add information about the AI models used
    st.header("Technology")
    st.markdown("""
    This application uses:
    - Google's Gemini 1.5 Pro for both text and image analysis
    - Streamlit for the web interface
    """)
    
    st.header("Example Questions")
    st.markdown("""
    - What are common symptoms of the flu?
    - How can I manage my migraine?
    - What is hypertension?
    - How often should I exercise for heart health?
    - What are the side effects of ibuprofen?
    """)
    
    # Add information about image analysis
    st.header("Image Analysis Tips")
    st.markdown("""
    - Upload clear, well-lit images
    - Only upload medical images (X-rays, skin conditions, etc.)
    - Provide context about what you're looking for
    - Remember this is for educational purposes only
    """)
    
    # Add a feedback section
    st.header("Feedback")
    feedback = st.text_area("Help us improve! Share your feedback:", key="feedback_input")
    if st.button("Submit Feedback", key="submit_feedback"):
        if feedback:
            st.success("Thank you for your feedback! We appreciate your input.")
            # In a real application, you would save this feedback to a database
        else:
            st.warning("Please enter some feedback before submitting.")