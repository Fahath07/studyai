#!/usr/bin/env python3
"""
Login UI Components for StudyMate
Provides beautiful login and registration interfaces
"""

import streamlit as st
from auth import auth_manager
import re

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def render_login_styles():
    """Render CSS styles for login components."""
    st.markdown("""
    <style>
    /* Login Container Styles */
    .login-container {
        background: linear-gradient(135deg, rgba(26, 26, 46, 0.95), rgba(22, 33, 62, 0.95));
        border: 2px solid rgba(0, 212, 170, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 500px;
        box-shadow: 0 15px 35px rgba(0, 212, 170, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h2 {
        color: #00D4AA;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 20px rgba(0, 212, 170, 0.3);
    }
    
    .login-header p {
        color: #EAEAEA;
        opacity: 0.8;
        font-size: 1.1rem;
    }
    
    .auth-tabs {
        display: flex;
        margin-bottom: 2rem;
        background: rgba(0, 212, 170, 0.1);
        border-radius: 15px;
        padding: 5px;
    }
    
    .auth-tab {
        flex: 1;
        text-align: center;
        padding: 12px 20px;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #EAEAEA;
        font-weight: 600;
    }
    
    .auth-tab.active {
        background: linear-gradient(135deg, #00D4AA, #0099CC);
        color: white;
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
    }
    
    .auth-tab:hover {
        background: rgba(0, 212, 170, 0.2);
    }
    
    .welcome-message {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 153, 204, 0.1));
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .user-profile {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 153, 204, 0.1));
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .user-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00D4AA, #0099CC);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        color: white;
        font-weight: bold;
    }
    
    .user-info h4 {
        color: #00D4AA;
        margin: 0;
        font-size: 1.2rem;
    }
    
    .user-info p {
        color: #EAEAEA;
        margin: 0;
        opacity: 0.8;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

def render_login_form():
    """Render the login form."""
    st.markdown("""
    <div class="login-header">
        <h2>🔐 Sign In</h2>
        <p>Welcome back to StudyMate!</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        username_or_email = st.text_input(
            "Username or Email",
            placeholder="Enter your username or email",
            help="You can use either your username or email address"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            help="Enter your account password"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("🚀 Sign In", type="primary", use_container_width=True)
        with col2:
            forgot_password = st.form_submit_button("🔑 Forgot Password?", use_container_width=True)
        
        if login_button:
            if not username_or_email or not password:
                st.error("❌ Please fill in all fields")
                return False
            
            # Attempt login
            success, message, user_data = auth_manager.login_user(username_or_email, password)
            
            if success:
                # Store user data in session state
                st.session_state.authenticated = True
                st.session_state.user_data = user_data
                st.session_state.session_token = user_data['session_token']
                
                st.success(f"✅ {message}")
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ {message}")
        
        if forgot_password:
            st.info("🔄 Password reset feature coming soon! Please contact support if you need help.")
    
    return False

def render_registration_form():
    """Render the registration form."""
    st.markdown("""
    <div class="login-header">
        <h2>📝 Create Account</h2>
        <p>Join StudyMate and supercharge your learning!</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("registration_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Full Name (Optional)",
                placeholder="Enter your full name",
                help="Your display name (optional)"
            )
        
        with col2:
            username = st.text_input(
                "Username *",
                placeholder="Choose a username",
                help="Must be at least 3 characters long"
            )
        
        email = st.text_input(
            "Email Address *",
            placeholder="Enter your email address",
            help="We'll use this for account recovery"
        )
        
        col3, col4 = st.columns(2)
        
        with col3:
            password = st.text_input(
                "Password *",
                type="password",
                placeholder="Create a password",
                help="Must be at least 6 characters long"
            )
        
        with col4:
            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Confirm your password",
                help="Re-enter your password"
            )
        
        # Terms and conditions
        agree_terms = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy",
            help="You must agree to continue"
        )
        
        register_button = st.form_submit_button("🎉 Create Account", type="primary", use_container_width=True)
        
        if register_button:
            # Validation
            errors = []
            
            if not username or len(username) < 3:
                errors.append("Username must be at least 3 characters long")
            
            if not email or not validate_email(email):
                errors.append("Please enter a valid email address")
            
            if not password or len(password) < 6:
                errors.append("Password must be at least 6 characters long")
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            if not agree_terms:
                errors.append("You must agree to the Terms of Service")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
                return False
            
            # Attempt registration
            success, message = auth_manager.register_user(username, email, password, full_name)
            
            if success:
                st.success(f"✅ {message}")
                st.balloons()
                st.info("🔄 Please switch to the Sign In tab to log in with your new account.")
            else:
                st.error(f"❌ {message}")
    
    return False

def render_user_profile():
    """Render user profile section."""
    user_data = st.session_state.get('user_data', {})
    
    # User profile card
    avatar_letter = user_data.get('username', 'U')[0].upper()
    
    st.markdown(f"""
    <div class="user-profile">
        <div class="user-avatar">{avatar_letter}</div>
        <div class="user-info">
            <h4>👋 Welcome, {user_data.get('full_name') or user_data.get('username', 'User')}!</h4>
            <p>📧 {user_data.get('email', 'No email')}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👤 Profile", help="View and edit your profile", use_container_width=True):
            st.session_state.show_profile = True
    
    with col2:
        if st.button("⚙️ Settings", help="Manage your preferences", use_container_width=True):
            st.session_state.show_settings = True
    
    with col3:
        if st.button("🚪 Logout", help="Sign out of your account", use_container_width=True):
            logout_user()

def render_auth_interface():
    """Render the complete authentication interface."""
    render_login_styles()
    
    # Check if user is already authenticated
    if st.session_state.get('authenticated', False):
        render_user_profile()
        return True
    
    # Authentication interface
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Tab selection
    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = 'login'
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔐 Sign In", key="login_tab", use_container_width=True):
            st.session_state.auth_tab = 'login'
    
    with col2:
        if st.button("📝 Sign Up", key="register_tab", use_container_width=True):
            st.session_state.auth_tab = 'register'
    
    st.markdown("---")
    
    # Render appropriate form
    if st.session_state.auth_tab == 'login':
        render_login_form()
    else:
        render_registration_form()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return False

def logout_user():
    """Logout the current user."""
    session_token = st.session_state.get('session_token')
    if session_token:
        auth_manager.logout_user(session_token)
    
    # Clear session state
    for key in ['authenticated', 'user_data', 'session_token']:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("✅ You have been logged out successfully!")
    st.rerun()

def render_user_settings():
    """Render user settings interface."""
    st.markdown("### ⚙️ User Settings")

    user_data = st.session_state.get('user_data', {})
    preferences = user_data.get('preferences', {})

    with st.form("user_settings"):
        st.markdown("#### 🎨 Appearance")
        theme = st.selectbox(
            "Theme",
            ["dark", "light"],
            index=0 if preferences.get('theme', 'dark') == 'dark' else 1,
            help="Choose your preferred theme"
        )

        st.markdown("#### 🤖 AI Preferences")
        default_ai = st.selectbox(
            "Default AI Provider",
            ["auto", "deepseek", "openai", "gemini", "watsonx", "huggingface", "demo"],
            index=0,
            help="Your preferred AI provider"
        )

        st.markdown("#### 🔔 Notifications")
        notifications = st.checkbox(
            "Enable notifications",
            value=preferences.get('notifications', True),
            help="Receive system notifications"
        )

        if st.form_submit_button("💾 Save Settings", type="primary"):
            # Update preferences
            new_preferences = {
                'theme': theme,
                'default_ai_provider': default_ai,
                'notifications': notifications
            }

            # Here you would typically save to the user database
            # For now, just update session state
            user_data['preferences'] = new_preferences
            st.session_state.user_data = user_data

            st.success("✅ Settings saved successfully!")

def render_user_profile_edit():
    """Render user profile editing interface."""
    st.markdown("### 👤 Edit Profile")

    user_data = st.session_state.get('user_data', {})

    with st.form("edit_profile"):
        full_name = st.text_input(
            "Full Name",
            value=user_data.get('full_name', ''),
            help="Your display name"
        )

        email = st.text_input(
            "Email Address",
            value=user_data.get('email', ''),
            help="Your email address",
            disabled=True  # Email changes require verification
        )

        st.info("📧 To change your email address, please contact support.")

        st.markdown("#### 🔒 Change Password")
        current_password = st.text_input(
            "Current Password",
            type="password",
            help="Enter your current password"
        )

        new_password = st.text_input(
            "New Password",
            type="password",
            help="Enter a new password (leave blank to keep current)"
        )

        confirm_new_password = st.text_input(
            "Confirm New Password",
            type="password",
            help="Confirm your new password"
        )

        if st.form_submit_button("💾 Update Profile", type="primary"):
            # Validate and update profile
            if new_password:
                if new_password != confirm_new_password:
                    st.error("❌ New passwords do not match")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters long")
                elif not current_password:
                    st.error("❌ Please enter your current password")
                else:
                    st.success("✅ Profile updated successfully!")
                    # Here you would update the database
            else:
                # Just update name
                user_data['full_name'] = full_name
                st.session_state.user_data = user_data
                st.success("✅ Profile updated successfully!")

def check_authentication():
    """Check if user is authenticated and validate session."""
    if not st.session_state.get('authenticated', False):
        return False

    session_token = st.session_state.get('session_token')
    if not session_token:
        return False

    # Validate session
    is_valid, user_data = auth_manager.validate_session(session_token)

    if not is_valid:
        # Session expired or invalid
        logout_user()
        return False

    # Update user data
    st.session_state.user_data = user_data
    return True
