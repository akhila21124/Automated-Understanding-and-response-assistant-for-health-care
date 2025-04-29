# medical_chatbot.py
import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

def run_medical_chatbot():
    """
    Main function to run the medical chatbot page
    """
    # Load environment variables if not already loaded
    load_dotenv()
    
    # Configure the API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = "YOUR_API_KEY" 
    genai.configure(api_key=api_key)
    
    # Streamlit UI
    st.set_page_config(page_title="MediAssist - Medical Q&A Chatbot", page_icon="🩺")
    
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
        .response-container {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #28a745;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # App header
    st.markdown("<h1 class='main-header'>MediAssist 🩺</h1>", unsafe_allow_html=True)
    st.markdown("Your AI-powered medical assistant. Ask any medical questions you have.")
    
    # Initialize chat history
    if "medical_messages" not in st.session_state:
        st.session_state.medical_messages = []
    
    # Display chat history
    for message in st.session_state.medical_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input
    user_query = st.chat_input("Ask your medical question here...")
    
    # When user submits a question
    if user_query:
        # Add user message to chat history
        st.session_state.medical_messages.append({"role": "user", "content": user_query})
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_query)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            # Get response from Gemini
            response = get_medical_response(user_query)
            
            # Update placeholder with response
            message_placeholder.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.medical_messages.append({"role": "assistant", "content": response})
    
    # Sidebar with information
    with st.sidebar:
        st.header("About MediAssist")
        st.info("""
        MediAssist is a specialized medical chatbot designed to provide information on medical topics only.
        
        **Important Disclaimer:** This chatbot provides general information and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.
        """)
        
        st.header("Example Questions")
        st.markdown("""
        - What are common symptoms of the flu?
        - How can I manage my migraine?
        - What is hypertension?
        - How often should I exercise for heart health?
        - What are the side effects of ibuprofen?
        """)
        
        # Reset conversation button
        if st.button("Clear Conversation"):
            st.session_state.medical_messages = []
            st.rerun()

def get_medical_response(question):
    """
    Function to get response from Gemini for medical queries
    """
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

# Run the app directly if this file is executed
if __name__ == "__main__":
    run_medical_chatbot()