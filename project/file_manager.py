import os
import json
import shutil
from datetime import datetime
from auth import load_users, save_users

class AudioFileManager:
    def __init__(self, username):
        self.username = username
        self.user_audio_dir = f"user_audio/{username}"
        os.makedirs(self.user_audio_dir, exist_ok=True)
    
    def save_audio_file(self, temp_audio_path, filename, original_text):
        """Save audio file to user's directory"""
        try:
            # Ensure filename is safe
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_filename:
                safe_filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create destination path
            destination_path = os.path.join(self.user_audio_dir, f"{safe_filename}.wav")
            
            # Copy temp file to user directory
            shutil.copy2(temp_audio_path, destination_path)
            
            # Update user's audio file list
            users = load_users()
            if self.username in users:
                if 'audio_files' not in users[self.username]:
                    users[self.username]['audio_files'] = []
                
                file_info = {
                    'filename': safe_filename,
                    'filepath': destination_path,
                    'text': original_text,
                    'created_at': datetime.now().isoformat(),
                    'file_size': os.path.getsize(destination_path)
                }
                
                users[self.username]['audio_files'].append(file_info)
                save_users(users)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error saving audio file: {e}")
            return False
    
    def get_user_audio_files(self):
        """Get list of user's audio files"""
        try:
            users = load_users()
            if self.username in users and 'audio_files' in users[self.username]:
                # Sort by creation date (newest first)
                audio_files = users[self.username]['audio_files']
                return sorted(audio_files, key=lambda x: x['created_at'], reverse=True)
            return []
            
        except Exception as e:
            print(f"Error getting user audio files: {e}")
            return []
    
    def delete_audio_file(self, filename):
        """Delete an audio file"""
        try:
            users = load_users()
            if self.username in users and 'audio_files' in users[self.username]:
                # Find and remove file info
                audio_files = users[self.username]['audio_files']
                file_to_remove = None
                
                for file_info in audio_files:
                    if file_info['filename'] == filename:
                        file_to_remove = file_info
                        break
                
                if file_to_remove:
                    # Remove file from filesystem
                    if os.path.exists(file_to_remove['filepath']):
                        os.remove(file_to_remove['filepath'])
                    
                    # Remove from user's file list
                    audio_files.remove(file_to_remove)
                    save_users(users)
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting audio file: {e}")
            return False
    
    def get_storage_info(self):
        """Get storage information for user"""
        try:
            users = load_users()
            file_count = 0
            total_size = 0
            
            if self.username in users and 'audio_files' in users[self.username]:
                audio_files = users[self.username]['audio_files']
                file_count = len(audio_files)
                
                for file_info in audio_files:
                    if os.path.exists(file_info['filepath']):
                        total_size += file_info.get('file_size', 0)
            
            return {
                'file_count': file_count,
                'total_size': total_size / (1024 * 1024)  # Convert to MB
            }
            
        except Exception as e:
            print(f"Error getting storage info: {e}")
            return {'file_count': 0, 'total_size': 0}
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files"""
        try:
            temp_dir = "temp_audio"
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    filepath = os.path.join(temp_dir, filename)
                    # Remove files older than 1 hour
                    if os.path.isfile(filepath):
                        file_age = datetime.now().timestamp() - os.path.getmtime(filepath)
                        if file_age > 3600:  # 1 hour in seconds
                            os.remove(filepath)
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")