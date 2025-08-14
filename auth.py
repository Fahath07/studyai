#!/usr/bin/env python3
"""
Authentication System for StudyMate
Provides user registration, login, and session management
"""

import os
import json
import hashlib
import secrets
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User data file
USERS_FILE = "users.json"
SESSIONS_FILE = "sessions.json"

class AuthManager:
    """Handles user authentication and session management."""
    
    def __init__(self):
        """Initialize the authentication manager."""
        self.users_file = USERS_FILE
        self.sessions_file = SESSIONS_FILE
        self.session_timeout = timedelta(hours=24)  # 24 hour sessions
        
    def _load_users(self) -> Dict:
        """Load users from file."""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            return {}
    
    def _save_users(self, users: Dict) -> bool:
        """Save users to file."""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving users: {e}")
            return False
    
    def _load_sessions(self) -> Dict:
        """Load active sessions from file."""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            return {}
    
    def _save_sessions(self, sessions: Dict) -> bool:
        """Save sessions to file."""
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")
            return False
    
    def _hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash password with salt."""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Create hash using SHA-256
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt
    
    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash."""
        password_hash, _ = self._hash_password(password, salt)
        return password_hash == stored_hash
    
    def register_user(self, username: str, email: str, password: str, full_name: str = "") -> Tuple[bool, str]:
        """
        Register a new user.
        
        Args:
            username: Unique username
            email: User email
            password: User password
            full_name: Optional full name
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate inputs
            if len(username) < 3:
                return False, "Username must be at least 3 characters long"
            
            if len(password) < 6:
                return False, "Password must be at least 6 characters long"
            
            if "@" not in email:
                return False, "Please enter a valid email address"
            
            # Load existing users
            users = self._load_users()
            
            # Check if username or email already exists
            for user_data in users.values():
                if user_data.get('username', '').lower() == username.lower():
                    return False, "Username already exists"
                if user_data.get('email', '').lower() == email.lower():
                    return False, "Email already registered"
            
            # Hash password
            password_hash, salt = self._hash_password(password)
            
            # Create user ID
            user_id = secrets.token_hex(16)
            
            # Create user record
            user_data = {
                'user_id': user_id,
                'username': username,
                'email': email,
                'full_name': full_name,
                'password_hash': password_hash,
                'salt': salt,
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'is_active': True,
                'preferences': {
                    'theme': 'dark',
                    'default_ai_provider': 'auto',
                    'notifications': True
                }
            }
            
            # Save user
            users[user_id] = user_data
            if self._save_users(users):
                logger.info(f"New user registered: {username}")
                return True, "Registration successful! You can now log in."
            else:
                return False, "Error saving user data. Please try again."
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, "Registration failed. Please try again."
    
    def login_user(self, username_or_email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Login user with username/email and password.
        
        Args:
            username_or_email: Username or email
            password: User password
            
        Returns:
            Tuple of (success, message, user_data)
        """
        try:
            users = self._load_users()
            
            # Find user by username or email
            user_data = None
            user_id = None
            
            for uid, data in users.items():
                if (data.get('username', '').lower() == username_or_email.lower() or 
                    data.get('email', '').lower() == username_or_email.lower()):
                    user_data = data
                    user_id = uid
                    break
            
            if not user_data:
                return False, "Invalid username/email or password", None
            
            if not user_data.get('is_active', True):
                return False, "Account is deactivated. Please contact support.", None
            
            # Verify password
            if not self._verify_password(password, user_data['password_hash'], user_data['salt']):
                return False, "Invalid username/email or password", None
            
            # Update last login
            user_data['last_login'] = datetime.now().isoformat()
            users[user_id] = user_data
            self._save_users(users)
            
            # Create session
            session_token = secrets.token_hex(32)
            sessions = self._load_sessions()
            
            sessions[session_token] = {
                'user_id': user_id,
                'username': user_data['username'],
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + self.session_timeout).isoformat(),
                'is_active': True
            }
            
            self._save_sessions(sessions)
            
            # Return user data without sensitive info
            safe_user_data = {
                'user_id': user_id,
                'username': user_data['username'],
                'email': user_data['email'],
                'full_name': user_data.get('full_name', ''),
                'preferences': user_data.get('preferences', {}),
                'session_token': session_token
            }
            
            logger.info(f"User logged in: {user_data['username']}")
            return True, "Login successful!", safe_user_data
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, "Login failed. Please try again.", None
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user by invalidating session."""
        try:
            sessions = self._load_sessions()
            if session_token in sessions:
                sessions[session_token]['is_active'] = False
                self._save_sessions(sessions)
                logger.info(f"User logged out: {sessions[session_token].get('username', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    def validate_session(self, session_token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Validate user session.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            Tuple of (is_valid, user_data)
        """
        try:
            sessions = self._load_sessions()
            
            if session_token not in sessions:
                return False, None
            
            session_data = sessions[session_token]
            
            if not session_data.get('is_active', False):
                return False, None
            
            # Check if session expired
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                # Invalidate expired session
                session_data['is_active'] = False
                sessions[session_token] = session_data
                self._save_sessions(sessions)
                return False, None
            
            # Get user data
            users = self._load_users()
            user_id = session_data['user_id']
            
            if user_id not in users:
                return False, None
            
            user_data = users[user_id]
            
            # Return safe user data
            safe_user_data = {
                'user_id': user_id,
                'username': user_data['username'],
                'email': user_data['email'],
                'full_name': user_data.get('full_name', ''),
                'preferences': user_data.get('preferences', {}),
                'session_token': session_token
            }
            
            return True, safe_user_data
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return False, None
    
    def get_user_stats(self) -> Dict:
        """Get user statistics."""
        try:
            users = self._load_users()
            sessions = self._load_sessions()
            
            active_sessions = sum(1 for s in sessions.values() if s.get('is_active', False))
            
            return {
                'total_users': len(users),
                'active_sessions': active_sessions,
                'total_sessions': len(sessions)
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {'total_users': 0, 'active_sessions': 0, 'total_sessions': 0}


# Global auth manager instance
auth_manager = AuthManager()
