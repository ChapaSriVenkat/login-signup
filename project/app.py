import streamlit as st
import os
import json
import hashlib
from datetime import datetime
import tempfile
import base64
from auth import authenticate_user, register_user, load_users
from audio_converter import TextToAudioConverter
from file_manager import AudioFileManager

# Page configuration
st.set_page_config(
    page_title="Text to Audio Converter",
    page_icon="🎵",
    layout="wide"
)

# Initialize session state
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'audio_files' not in st.session_state:
        st.session_state.audio_files = []

def show_login_page():
    st.title("🔐 Login")
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.page = 'dashboard'
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.markdown("---")
    if st.button("Don't have an account? Sign up"):
        st.session_state.page = 'signup'
        st.rerun()

def show_signup_page():
    st.title("📝 Sign Up")
    st.markdown("---")
    
    with st.form("signup_form"):
        username = st.text_input("Choose Username")
        email = st.text_input("Email Address")
        password = st.text_input("Choose Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        signup_button = st.form_submit_button("Sign Up")
        
        if signup_button:
            if not username or not email or not password:
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                if register_user(username, email, password):
                    st.success("Account created successfully! Please login.")
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error("Username already exists. Please choose a different username.")
    
    st.markdown("---")
    if st.button("Already have an account? Login"):
        st.session_state.page = 'login'
        st.rerun()

def show_dashboard():
    st.title(f"🎵 Audio Dashboard - Welcome {st.session_state.username}!")
    
    # Logout button in sidebar
    with st.sidebar:
        st.markdown("### User Menu")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.page = 'login'
            st.rerun()
    
    # Initialize components
    audio_converter = TextToAudioConverter()
    file_manager = AudioFileManager(st.session_state.username)
    
    # Main dashboard tabs
    tab1, tab2, tab3 = st.tabs(["🎤 Convert Text", "📁 My Audio Files", "⚙️ Settings"])
    
    with tab1:
        st.header("Text to Audio Conversion")
        
        # Text input
        text_input = st.text_area(
            "Enter text to convert to audio:",
            height=150,
            placeholder="Type your text here..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            voice_options = ["female", "male"]
            selected_voice = st.selectbox("Select Voice:", voice_options)
            
        with col2:
            speech_rate = st.slider("Speech Rate:", 50, 300, 150)
        
        if st.button("🎵 Convert to Audio", type="primary"):
            if text_input.strip():
                with st.spinner("Converting text to audio..."):
                    try:
                        audio_file = audio_converter.convert_text_to_audio(
                            text_input, 
                            voice=selected_voice,
                            rate=speech_rate
                        )
                        
                        if audio_file:
                            st.success("Audio conversion completed!")
                            
                            # Audio player
                            st.audio(audio_file, format='audio/wav')
                            
                            # Save and download options
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                filename = st.text_input(
                                    "Save as:", 
                                    value=f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                )
                                if st.button("💾 Save to My Files"):
                                    if file_manager.save_audio_file(audio_file, filename, text_input):
                                        st.success(f"Audio saved as '{filename}'!")
                                    else:
                                        st.error("Failed to save audio file.")
                            
                            with col2:
                                # Download button
                                with open(audio_file, "rb") as file:
                                    st.download_button(
                                        label="⬇️ Download Audio",
                                        data=file.read(),
                                        file_name=f"{filename}.wav",
                                        mime="audio/wav"
                                    )
                        else:
                            st.error("Failed to convert text to audio.")
                    
                    except Exception as e:
                        st.error(f"Error during conversion: {str(e)}")
            else:
                st.warning("Please enter some text to convert.")
    
    with tab2:
        st.header("My Audio Files")
        
        # Load user's saved audio files
        saved_files = file_manager.get_user_audio_files()
        
        if saved_files:
            for file_info in saved_files:
                with st.expander(f"🎵 {file_info['filename']} - {file_info['created_at']}"):
                    st.write(f"**Original Text:** {file_info['text'][:100]}{'...' if len(file_info['text']) > 100 else ''}")
                    
                    # Audio player
                    if os.path.exists(file_info['filepath']):
                        st.audio(file_info['filepath'], format='audio/wav')
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Download button
                            with open(file_info['filepath'], "rb") as file:
                                st.download_button(
                                    label="⬇️ Download",
                                    data=file.read(),
                                    file_name=f"{file_info['filename']}.wav",
                                    mime="audio/wav",
                                    key=f"download_{file_info['filename']}"
                                )
                        
                        with col2:
                            # Delete button
                            if st.button("🗑️ Delete", key=f"delete_{file_info['filename']}"):
                                if file_manager.delete_audio_file(file_info['filename']):
                                    st.success("File deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete file.")
                    else:
                        st.error("Audio file not found.")
        else:
            st.info("No saved audio files found. Convert some text to audio and save them to see them here!")
    
    with tab3:
        st.header("Settings")
        
        st.subheader("Account Information")
        st.write(f"**Username:** {st.session_state.username}")
        
        st.subheader("Audio Settings")
        st.info("Audio settings can be configured during conversion in the 'Convert Text' tab.")
        
        st.subheader("Storage Information")
        storage_info = file_manager.get_storage_info()
        st.write(f"**Total Audio Files:** {storage_info['file_count']}")
        st.write(f"**Storage Used:** {storage_info['total_size']:.2f} MB")

def main():
    init_session_state()
    
    # Route to appropriate page
    if not st.session_state.authenticated:
        if st.session_state.page == 'signup':
            show_signup_page()
        else:
            show_login_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()