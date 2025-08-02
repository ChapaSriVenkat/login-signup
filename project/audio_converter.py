import pyttsx3
import tempfile
import os
from datetime import datetime

class TextToAudioConverter:
    def __init__(self):
        self.engine = None
        self.init_engine()
    
    def init_engine(self):
        """Initialize the text-to-speech engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices:
                self.voices = voices
            else:
                self.voices = []
                
        except Exception as e:
            print(f"Error initializing TTS engine: {e}")
            self.engine = None
    
    def convert_text_to_audio(self, text, voice="female", rate=150):
        """Convert text to audio file"""
        if not self.engine:
            self.init_engine()
            
        if not self.engine:
            return None
        
        try:
            # Set speech rate
            self.engine.setProperty('rate', rate)
            
            # Set voice
            voices = self.engine.getProperty('voices')
            if voices:
                if voice == "female" and len(voices) > 1:
                    self.engine.setProperty('voice', voices[1].id)
                elif voice == "male" and len(voices) > 0:
                    self.engine.setProperty('voice', voices[0].id)
            
            # Create temporary file
            temp_dir = "temp_audio"
            os.makedirs(temp_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = os.path.join(temp_dir, f"audio_{timestamp}.wav")
            
            # Save audio to file
            self.engine.save_to_file(text, temp_file)
            self.engine.runAndWait()
            
            # Check if file was created successfully
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                return temp_file
            else:
                return None
                
        except Exception as e:
            print(f"Error converting text to audio: {e}")
            return None
    
    def get_available_voices(self):
        """Get list of available voices"""
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            voice_list = []
            
            for i, voice in enumerate(voices):
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'gender': 'female' if 'female' in voice.name.lower() or i % 2 == 1 else 'male'
                }
                voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            print(f"Error getting voices: {e}")
            return []