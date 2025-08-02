import json
import hashlib
import os
from datetime import datetime

USERS_FILE = "users.json"

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Authenticate user credentials"""
    users = load_users()
    
    if username in users:
        stored_password_hash = users[username]['password']
        input_password_hash = hash_password(password)
        return stored_password_hash == input_password_hash
    
    return False

def register_user(username, email, password):
    """Register a new user"""
    users = load_users()
    
    # Check if username already exists
    if username in users:
        return False
    
    # Add new user
    users[username] = {
        'email': email,
        'password': hash_password(password),
        'created_at': datetime.now().isoformat(),
        'audio_files': []
    }
    
    return save_users(users)

def get_user_info(username):
    """Get user information"""
    users = load_users()
    return users.get(username, None)