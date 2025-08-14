"""
StudyMate - AI-Powered Academic PDF RAG System
Main Streamlit Application
"""

import streamlit as st
from datetime import datetime
import os
from typing import List, Dict, Any

# Import custom modules
try:
    from pdf_processing import process_uploaded_pdfs, get_processing_stats
    from embedding_retrieval import initialize_retrieval_system, format_retrieved_chunks, get_chunk_sources
    from watsonx_integration import initialize_watsonx_client, query_watsonx, format_error_response
    from huggingface_integration import initialize_huggingface_client, create_academic_prompt_hf
    from openai_integration import initialize_openai_client, query_openai
    from gemini_integration import initialize_gemini_client, query_gemini
    from deepseek_integration import initialize_deepseek_client, query_deepseek
    from openrouter_integration import OpenRouterClient
    from quiz_generator import (
        generate_mcqs_with_ai, create_quiz_session, calculate_quiz_score,
        get_quiz_feedback, MCQuestion, QuizSession
    )
    from quiz_export import (
        create_quiz_word_document, create_quiz_pdf_document, prepare_quiz_export_data
    )
    from utils import (
        load_environment_variables, validate_question, format_qa_for_display,
        create_qa_session_export, create_qa_session_pdf_export, get_session_stats, create_download_filename,
        log_user_action
    )
    from image_to_text import handle_image_upload, display_api_info
    from voice_assistant import handle_voice_qa_interface, initialize_voice_assistant
    from chatbot import handle_general_chatbot, initialize_chatbot_session
    IMPORTS_AVAILABLE = True
except ImportError as e:
    st.error(f"⚠️ Some dependencies are missing: {e}")
    st.info("Installing dependencies... Please run: pip install -r requirements.txt")
    IMPORTS_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="StudyMate - AI Academic Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Educational Theme with Background Images
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Main App Background with Educational Patterns */
    .stApp {
        background:
            linear-gradient(135deg, rgba(15, 15, 35, 0.95), rgba(26, 26, 46, 0.95)),
            url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><defs><pattern id="educational" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse"><rect fill="%23ffffff" opacity="0.01" width="40" height="40"/><circle cx="20" cy="20" r="2" fill="%2300D4AA" opacity="0.1"/><path d="M10,10 L30,10 L30,30 L10,30 Z" fill="none" stroke="%2300D4AA" stroke-width="0.5" opacity="0.15"/><path d="M5,35 L15,25 L25,35 L35,25" fill="none" stroke="%230099CC" stroke-width="0.5" opacity="0.1"/></pattern></defs><rect width="100%25" height="100%25" fill="url(%23educational)"/></svg>'),
            radial-gradient(circle at 20% 80%, rgba(0, 212, 170, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(0, 153, 204, 0.1) 0%, transparent 50%);
        background-size: cover, 100px 100px, 800px 800px, 600px 600px;
        background-attachment: fixed, scroll, fixed, fixed;
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
    }

    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #00D4AA, #0099CC);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 212, 170, 0.3);
        border: 1px solid rgba(0, 212, 170, 0.2);
    }

    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        font-weight: 300;
    }

    /* Sidebar Styling with Educational Theme */
    .css-1d391kg {
        background:
            linear-gradient(180deg, rgba(26, 26, 46, 0.95), rgba(22, 33, 62, 0.95)),
            url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="sidebar-pattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><rect fill="%23ffffff" opacity="0.01" width="20" height="20"/><circle cx="10" cy="10" r="1" fill="%2300D4AA" opacity="0.2"/></pattern></defs><rect width="100%25" height="100%25" fill="url(%23sidebar-pattern)"/></svg>');
        border-right: 3px solid #00D4AA;
        box-shadow: 5px 0 15px rgba(0, 212, 170, 0.1);
    }

    /* Sidebar Headers */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: #00D4AA !important;
        text-shadow: 0 0 10px rgba(0, 212, 170, 0.3);
    }

    /* Card Styling with Hover Effects */
    .study-card {
        background: linear-gradient(135deg, rgba(26, 26, 46, 0.9), rgba(22, 33, 62, 0.9));
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .study-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 212, 170, 0.2);
        border-color: rgba(0, 212, 170, 0.5);
    }

    .study-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 170, 0.1), transparent);
        transition: left 0.5s;
    }

    .study-card:hover::before {
        left: 100%;
    }

    /* Answer Cards */
    .answer-card {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 153, 204, 0.1));
        border: 1px solid rgba(0, 212, 170, 0.4);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #EAEAEA;
        line-height: 1.7;
        box-shadow: 0 5px 15px rgba(0, 212, 170, 0.2);
    }

    /* Source Cards */
    .source-card {
        background: linear-gradient(135deg, rgba(22, 33, 62, 0.8), rgba(26, 26, 46, 0.8));
        border-left: 4px solid #00D4AA;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #EAEAEA;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
    }

    /* Chat Message Styling */
    .chat-user {
        background: linear-gradient(135deg, #00D4AA, #0099CC);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(0, 212, 170, 0.3);
        max-width: 80%;
        margin-left: auto;
    }

    .chat-ai {
        background: linear-gradient(135deg, rgba(26, 26, 46, 0.9), rgba(22, 33, 62, 0.9));
        color: #EAEAEA;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        border: 1px solid rgba(0, 212, 170, 0.3);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        max-width: 80%;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #00D4AA, #0099CC);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 212, 170, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 212, 170, 0.4);
    }

    /* File Uploader Styling */
    .stFileUploader {
        background: rgba(26, 26, 46, 0.6);
        border: 2px dashed rgba(0, 212, 170, 0.5);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
    }

    /* Metrics Styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 153, 204, 0.1));
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00D4AA, #0099CC);
    }

    /* Text Input Styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 10px;
        color: #EAEAEA;
    }

    /* Selectbox Styling */
    .stSelectbox > div > div {
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 10px;
    }

    /* Success/Error/Warning Messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.2), rgba(0, 153, 204, 0.2));
        border: 1px solid #00D4AA;
        border-radius: 10px;
    }

    .stError {
        background: linear-gradient(135deg, rgba(255, 99, 99, 0.2), rgba(255, 71, 87, 0.2));
        border: 1px solid #FF6B6B;
        border-radius: 10px;
    }

    .stWarning {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.2), rgba(255, 152, 0, 0.2));
        border: 1px solid #FFC107;
        border-radius: 10px;
    }

    /* Educational Icons Background */
    .education-bg {
        position: relative;
        overflow: hidden;
    }

    .education-bg::before {
        content: "📚 🎓 📖 ✏️ 🔬 📊 💡 🧠 📝 🎯 🖥️ 📱 🌟 ⚡ 🚀 🎨 📐 🧮 🔍 📋";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        font-size: 2rem;
        opacity: 0.08;
        z-index: -1;
        animation: float 25s infinite linear;
        white-space: nowrap;
        line-height: 3rem;
    }

    .education-bg::after {
        content: "🎯 💻 📈 🔬 🧪 📊 🎨 🎭 🎪 🎨 📚 📖 📝 ✏️ 🖊️ 📏 📐 🧮 🔍 💡";
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        bottom: 0;
        font-size: 1.5rem;
        opacity: 0.05;
        z-index: -1;
        animation: float-reverse 30s infinite linear;
        white-space: nowrap;
        line-height: 2.5rem;
    }

    @keyframes float {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    @keyframes float-reverse {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }

    /* Glowing Effects */
    .glow {
        box-shadow: 0 0 20px rgba(0, 212, 170, 0.3);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 20px rgba(0, 212, 170, 0.3); }
        50% { box-shadow: 0 0 30px rgba(0, 212, 170, 0.5); }
        100% { box-shadow: 0 0 20px rgba(0, 212, 170, 0.3); }
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* AI Agent Switcher Button - Fixed Top Left */
    .ai-switcher-container {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 9999;
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.95), rgba(0, 153, 204, 0.95));
        border-radius: 15px;
        padding: 10px 15px;
        box-shadow: 0 8px 25px rgba(0, 212, 170, 0.4);
        border: 2px solid rgba(0, 212, 170, 0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        min-width: 220px;
        font-size: 14px;
        font-weight: 600;
        color: white;
    }

    .ai-switcher-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(0, 212, 170, 0.6);
        background: linear-gradient(135deg, rgba(0, 212, 170, 1), rgba(0, 153, 204, 1));
    }

    .ai-switcher-button {
        background: none;
        border: none;
        color: white;
        font-weight: 600;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
        width: 100%;
        text-align: left;
    }

    .ai-status-indicator {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-left: auto;
        flex-shrink: 0;
    }

    .ai-status-active {
        background: #00FF88;
        box-shadow: 0 0 8px rgba(0, 255, 136, 0.6);
        animation: pulse-green 2s infinite;
    }

    .ai-status-inactive {
        background: #666;
    }

    @keyframes pulse-green {
        0% { box-shadow: 0 0 8px rgba(0, 255, 136, 0.6); }
        50% { box-shadow: 0 0 15px rgba(0, 255, 136, 0.8); }
        100% { box-shadow: 0 0 8px rgba(0, 255, 136, 0.6); }
    }

    /* Style the AI switcher selectbox */
    .ai-switcher-selectbox .stSelectbox > div > div {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.95), rgba(0, 153, 204, 0.95));
        border: 2px solid rgba(0, 212, 170, 0.3);
        border-radius: 15px;
        color: white;
        font-weight: 600;
        box-shadow: 0 8px 25px rgba(0, 212, 170, 0.4);
        backdrop-filter: blur(10px);
    }

    .ai-switcher-selectbox .stSelectbox > div > div:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(0, 212, 170, 0.6);
        background: linear-gradient(135deg, rgba(0, 212, 170, 1), rgba(0, 153, 204, 1));
    }
</style>
""", unsafe_allow_html=True)




def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []
    
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    
    if "watsonx_client" not in st.session_state:
        st.session_state.watsonx_client = None

    if "huggingface_client" not in st.session_state:
        st.session_state.huggingface_client = None

    if "openai_client" not in st.session_state:
        st.session_state.openai_client = None

    if "gemini_client" not in st.session_state:
        st.session_state.gemini_client = None

    if "deepseek_client" not in st.session_state:
        st.session_state.deepseek_client = None

    if "ai_provider" not in st.session_state:
        st.session_state.ai_provider = "auto"  # auto, watsonx, huggingface, openai, gemini

    if "processed_files" not in st.session_state:
        st.session_state.processed_files = []

    if "chunks" not in st.session_state:
        st.session_state.chunks = []

    # Quiz-related session state
    if "quiz_session" not in st.session_state:
        st.session_state.quiz_session = None
    if "quiz_mode" not in st.session_state:
        st.session_state.quiz_mode = False
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0

    # Voice assistant session state
    if "voice_assistant" not in st.session_state:
        st.session_state.voice_assistant = None

    # Chatbot session state
    if "chatbot_session" not in st.session_state:
        st.session_state.chatbot_session = None

    # Chatbot session state
    if "chatbot_session" not in st.session_state:
        st.session_state.chatbot_session = None
    if "quiz_history" not in st.session_state:
        st.session_state.quiz_history = []
    if "current_document_chunks" not in st.session_state:
        st.session_state.current_document_chunks = []


def render_ai_switcher():
    """Render the permanent AI switcher at the top of the page."""
    # Get current AI provider info
    current_provider = st.session_state.get('ai_provider', 'auto')
    provider_display_names = {
        "auto": "🔄 Auto (Best Available)",
        "deepseek": "🆓 DeepSeek (Free)",
        "openai": "🧠 OpenAI (ChatGPT)",
        "gemini": "🌟 Google Gemini",
        "watsonx": "🏢 IBM Watsonx",
        "huggingface": "🤗 Hugging Face",
        "demo": "🎭 Demo Mode"
    }

    # Create columns for the switcher - simplified layout
    col1, col2 = st.columns([3, 1])

    with col1:
        # Create the AI provider selectbox without label
        selected_provider = st.selectbox(
            "Select AI Provider:",
            options=list(provider_display_names.keys()),
            format_func=lambda x: provider_display_names[x],
            index=list(provider_display_names.keys()).index(current_provider),
            key="ai_provider_switcher",
            help="Switch between different AI providers instantly",
            label_visibility="collapsed"
        )

        # Handle provider change
        if selected_provider != current_provider:
            st.session_state.ai_provider = selected_provider
            with st.spinner(f"Switching to {provider_display_names[selected_provider]}..."):
                initialize_ai_clients()
            st.success(f"✅ Switched to {provider_display_names[selected_provider]}")
            st.rerun()

    with col2:
        # Quick initialize button
        if st.button("🔄 Initialize", help="Initialize the selected AI provider", type="secondary"):
            with st.spinner("Initializing AI..."):
                initialize_ai_clients()
            st.rerun()

    st.markdown("---")


def display_header():
    """Display the main application header with vibrant dark theme and animations."""
    # Hero Banner with Custom Styling and Educational Elements
    st.markdown("""
    <div class="main-header education-bg glow">
        <h1>📚 StudyMate</h1>
        <p>Your AI-powered study companion for the digital age</p>
        <div style="margin-top: 1rem; font-size: 1.5rem; opacity: 0.8;">
            🎓 Learn • 🤖 Ask • 📊 Analyze • 🚀 Excel
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Welcome message for new users
    if not st.session_state.get('user_welcomed', False):
        st.markdown("""
        <div class="study-card" style="text-align: center; border: 2px solid rgba(0, 212, 170, 0.5); animation: pulse 2s infinite;">
            <h3 style="color: #00D4AA; margin-top: 0;">🌟 Welcome to StudyMate!</h3>
            <p style="color: #EAEAEA; opacity: 0.9;">Choose your learning mode below and let AI supercharge your studies!</p>
            <div style="font-size: 2rem; margin: 1rem 0;">
                📚 ➡️ 🤖 ➡️ 🎯 ➡️ 🏆
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.user_welcomed = True

    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)


def generate_quiz_word_document(quiz_session: Dict[str, Any], include_answers: bool = True):
    """Generate Word document from quiz session."""
    try:
        quiz_data = prepare_quiz_export_data(quiz_session, include_answers)
        return create_quiz_word_document(quiz_data)
    except Exception as e:
        st.error(f"Error generating Word document: {e}")
        return None


def generate_quiz_pdf_document(quiz_session: Dict[str, Any], include_answers: bool = True):
    """Generate PDF document from quiz session."""
    try:
        quiz_data = prepare_quiz_export_data(quiz_session, include_answers)
        return create_quiz_pdf_document(quiz_data)
    except Exception as e:
        st.error(f"Error generating PDF document: {e}")
        return None


def get_ai_error_message(error_str: str) -> str:
    """Get user-friendly error message for AI initialization failures."""
    if "quota" in error_str.lower() or "429" in error_str:
        return "Quota exceeded - try again later or use demo mode"
    elif "api_key" in error_str.lower() or "401" in error_str:
        return "Invalid API key - check your configuration"
    elif "network" in error_str.lower() or "connection" in error_str.lower():
        return "Network connection issue - check your internet"
    else:
        return "Configuration or service issue"


def initialize_ai_clients():
    """Initialize AI clients based on user selection with improved error handling."""
    provider = st.session_state.ai_provider

    with st.spinner("Initializing AI..."):
        if provider == "auto":
            # Try providers in order with detailed feedback
            success = False

            # Try DeepSeek first (free and reliable)
            try:
                st.session_state.deepseek_client = initialize_deepseek_client()
                if st.session_state.deepseek_client:
                    st.success("✅ DeepSeek initialized successfully")
                    st.session_state.ai_provider = "deepseek"
                    success = True
                else:
                    st.info("ℹ️ DeepSeek not available - trying next provider...")
            except Exception as e:
                error_msg = get_ai_error_message(str(e))
                if "Insufficient Balance" in str(e):
                    st.info("ℹ️ DeepSeek: Account verification needed - trying next provider...")
                else:
                    st.info(f"ℹ️ DeepSeek: {error_msg} - trying next provider...")

            # Try OpenAI if DeepSeek failed
            if not success:
                try:
                    st.session_state.openai_client = initialize_openai_client()
                    if st.session_state.openai_client:
                        st.success("✅ OpenAI initialized successfully")
                        st.session_state.ai_provider = "openai"
                        success = True
                    else:
                        st.info("ℹ️ OpenAI not available - trying next provider...")
                except Exception as e:
                    error_msg = get_ai_error_message(str(e))
                    st.info(f"ℹ️ OpenAI: {error_msg} - trying next provider...")

            # Try Gemini if OpenAI failed
            if not success:
                try:
                    st.session_state.gemini_client = initialize_gemini_client()
                    if st.session_state.gemini_client:
                        st.success("✅ Google Gemini initialized successfully")
                        st.session_state.ai_provider = "gemini"
                        success = True
                    else:
                        st.info("ℹ️ Google Gemini not available - trying next provider...")
                except Exception as e:
                    error_msg = get_ai_error_message(str(e))
                    st.info(f"ℹ️ Google Gemini: {error_msg} - trying next provider...")

            # Try Watsonx if previous failed
            if not success:
                try:
                    st.session_state.watsonx_client = initialize_watsonx_client()
                    if st.session_state.watsonx_client and hasattr(st.session_state.watsonx_client, 'model_id') and st.session_state.watsonx_client.model_id != "demo-mode":
                        st.success("✅ IBM Watsonx initialized successfully")
                        st.session_state.ai_provider = "watsonx"
                        success = True
                    else:
                        st.info("ℹ️ IBM Watsonx not configured - trying next provider...")
                except Exception as e:
                    error_msg = get_ai_error_message(str(e))
                    st.info(f"ℹ️ IBM Watsonx: {error_msg} - trying next provider...")

            # Try Hugging Face if previous failed
            if not success:
                try:
                    st.session_state.huggingface_client = initialize_huggingface_client()
                    if st.session_state.huggingface_client:
                        st.success("✅ Hugging Face initialized successfully")
                        st.session_state.ai_provider = "huggingface"
                        success = True
                    else:
                        st.info("ℹ️ Hugging Face not available - using demo mode...")
                except Exception as e:
                    error_msg = get_ai_error_message(str(e))
                    st.info(f"ℹ️ Hugging Face: {error_msg} - using demo mode...")

            # Fall back to demo mode
            if not success:
                st.session_state.watsonx_client = initialize_watsonx_client()  # Demo client
                st.warning("⚠️ All AI providers unavailable - using demo mode with intelligent fallback")
                st.session_state.ai_provider = "demo"

        elif provider == "deepseek":
            try:
                st.session_state.deepseek_client = initialize_deepseek_client()
                if st.session_state.deepseek_client:
                    st.success("✅ DeepSeek initialized successfully")
                else:
                    st.error("❌ DeepSeek initialization failed")
                    st.info("💡 **Common Solutions:**")
                    st.info("1. **Verify Account**: Visit https://platform.deepseek.com/ and complete email verification")
                    st.info("2. **Check Balance**: Ensure your account has free credits activated")
                    st.info("3. **New API Key**: Try generating a fresh API key")
                    st.info("4. **Account Setup**: Complete the account setup process")
            except Exception as e:
                error_msg = get_ai_error_message(str(e))
                if "Insufficient Balance" in str(e):
                    st.error("❌ DeepSeek Account Verification Required")
                    st.warning("🔧 **Account Setup Needed:**")
                    st.info("1. Visit: https://platform.deepseek.com/")
                    st.info("2. Complete email verification")
                    st.info("3. Activate free credits")
                    st.info("4. Generate new API key if needed")
                else:
                    st.error(f"❌ DeepSeek initialization failed: {error_msg}")

        elif provider == "openai":
            try:
                st.session_state.openai_client = initialize_openai_client()
                if st.session_state.openai_client:
                    st.success("✅ OpenAI initialized successfully")
                else:
                    st.error("❌ OpenAI initialization failed - check your API key")
            except Exception as e:
                error_msg = get_ai_error_message(str(e))
                st.error(f"❌ OpenAI initialization failed: {error_msg}")

        elif provider == "gemini":
            try:
                st.session_state.gemini_client = initialize_gemini_client()
                if st.session_state.gemini_client:
                    st.success("✅ Google Gemini initialized successfully")
                else:
                    st.error("❌ Google Gemini initialization failed - check your API key")
            except Exception as e:
                error_msg = get_ai_error_message(str(e))
                st.error(f"❌ Google Gemini initialization failed: {error_msg}")

        elif provider == "watsonx":
            try:
                st.session_state.watsonx_client = initialize_watsonx_client()
                if st.session_state.watsonx_client and hasattr(st.session_state.watsonx_client, 'model_id') and st.session_state.watsonx_client.model_id != "demo-mode":
                    st.success("✅ IBM Watsonx initialized successfully")
                else:
                    st.error("❌ IBM Watsonx initialization failed - check your credentials")
            except Exception as e:
                error_msg = get_ai_error_message(str(e))
                st.error(f"❌ IBM Watsonx initialization failed: {error_msg}")

        elif provider == "huggingface":
            try:
                st.session_state.huggingface_client = initialize_huggingface_client()
                if st.session_state.huggingface_client:
                    st.success("✅ Hugging Face initialized successfully")
                else:
                    st.error("❌ Hugging Face initialization failed - check your API token")
            except Exception as e:
                error_msg = get_ai_error_message(str(e))
                st.error(f"❌ Hugging Face initialization failed: {error_msg}")

        elif provider == "demo":
            st.session_state.watsonx_client = initialize_watsonx_client()  # This will return demo client
            st.info("ℹ️ Demo mode activated - using intelligent fallback system")


def display_ai_status():
    """Display current AI provider status."""
    provider = st.session_state.ai_provider

    if provider == "deepseek" and st.session_state.deepseek_client:
        st.success("🚀 DeepSeek Active")
        if hasattr(st.session_state.deepseek_client, 'get_model_info'):
            info = st.session_state.deepseek_client.get_model_info()
            st.caption(f"Model: {info.get('model_name', 'Unknown')}")
        st.caption("✅ Free unlimited usage")

    elif provider == "openai" and st.session_state.openai_client:
        st.success("🤖 OpenAI Active")
        if hasattr(st.session_state.openai_client, 'get_model_info'):
            info = st.session_state.openai_client.get_model_info()
            st.caption(f"Model: {info.get('model_name', 'Unknown')}")
        st.caption("✅ Quiz generation available")

    elif provider == "gemini" and st.session_state.gemini_client:
        st.success("🔮 Google Gemini Active")
        if hasattr(st.session_state.gemini_client, 'get_model_info'):
            info = st.session_state.gemini_client.get_model_info()
            st.caption(f"Model: {info.get('model_name', 'Unknown')}")
        st.caption("✅ Quiz generation available")

    elif provider == "watsonx" and st.session_state.watsonx_client:
        if hasattr(st.session_state.watsonx_client, 'model_id') and st.session_state.watsonx_client.model_id != "demo-mode":
            st.success("🤖 IBM Watsonx Active")
            if hasattr(st.session_state.watsonx_client, 'get_model_info'):
                info = st.session_state.watsonx_client.get_model_info()
                st.caption(f"Model: {info.get('model_id', 'Unknown')}")
        else:
            st.warning("⚠️ Demo Mode (Watsonx failed)")

    elif provider == "huggingface" and st.session_state.huggingface_client:
        st.success("🤗 Hugging Face Active")
        if hasattr(st.session_state.huggingface_client, 'get_model_info'):
            info = st.session_state.huggingface_client.get_model_info()
            st.caption(f"Model: {info.get('model_name', 'Unknown')}")
            st.caption(f"Device: {info.get('device', 'Unknown')}")

    elif provider == "demo":
        st.info("🎭 Demo Mode Active")
        st.caption("Using intelligent fallback system")
        st.caption("✅ Dynamic quiz generation available")

    elif provider == "auto":
        st.warning("🔄 Auto Mode")
        st.caption("Click 'Initialize AI' to find best provider")

    else:
        st.error("❌ No AI provider active")
        st.caption("Click 'Initialize AI' above")

    # Show helpful information for quota issues
    if provider in ["openai", "gemini"]:
        with st.expander("ℹ️ Provider Status", expanded=False):
            st.write("**Note**: If you see quota errors, the system will automatically use the intelligent fallback mode for quiz generation.")
            st.write("**Fallback Features**:")
            st.write("• Dynamic questions that change each time")
            st.write("• Difficulty-based content (easy/medium/hard)")
            st.write("• Topic-focused questions")
            st.write("• Content-based on your uploaded documents")


def display_sidebar():
    """Display sidebar with configuration and stats."""
    with st.sidebar:
        # User Profile Section
        if st.session_state.get('authenticated', False):
            user_data = st.session_state.get('user_data', {})
            username = user_data.get('username', 'User')
            full_name = user_data.get('full_name', '')
            email = user_data.get('email', '')

            # User profile card
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 153, 204, 0.1));
                        border: 1px solid rgba(0, 212, 170, 0.3);
                        border-radius: 10px;
                        padding: 15px;
                        margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 40px; height: 40px; border-radius: 50%;
                                background: linear-gradient(135deg, #00D4AA, #0099CC);
                                display: flex; align-items: center; justify-content: center;
                                color: white; font-weight: bold; font-size: 1.2rem;">
                        {username[0].upper()}
                    </div>
                    <div>
                        <h4 style="color: #00D4AA; margin: 0; font-size: 1rem;">
                            {full_name or username}
                        </h4>
                        <p style="color: #EAEAEA; margin: 0; font-size: 0.8rem; opacity: 0.8;">
                            {email}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # User action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👤 Profile", help="Edit your profile", use_container_width=True):
                    st.session_state.show_profile = True
                    st.rerun()

            with col2:
                if st.button("⚙️ Settings", help="Manage preferences", use_container_width=True):
                    st.session_state.show_settings = True
                    st.rerun()

            # Logout button
            if st.button("🚪 Logout", help="Sign out of your account", type="secondary", use_container_width=True):
                from login_ui import logout_user
                logout_user()

            st.divider()

        st.header("🤖 AI Configuration")

        # AI Provider Selection
        ai_provider = st.selectbox(
            "Choose AI Provider:",
            ["Auto (Best Available)", "DeepSeek (Free)", "OpenAI (ChatGPT)", "Google Gemini", "IBM Watsonx", "Hugging Face", "Demo Mode"],
            index=0,
            help="Select which AI provider to use for generating responses"
        )

        # Map selection to internal values
        provider_map = {
            "Auto (Best Available)": "auto",
            "DeepSeek (Free)": "deepseek",
            "OpenAI (ChatGPT)": "openai",
            "Google Gemini": "gemini",
            "IBM Watsonx": "watsonx",
            "Hugging Face": "huggingface",
            "Demo Mode": "demo"
        }
        st.session_state.ai_provider = provider_map[ai_provider]

        # Initialize AI clients based on selection
        if st.button("🔄 Initialize AI", help="Initialize the selected AI provider"):
            initialize_ai_clients()

        st.divider()
        st.header("📊 Session Info")

        # Display AI status
        display_ai_status()

        st.divider()

        # Gamified User Stats
        if st.session_state.get('authenticated', False):
            user_data = st.session_state.get('user_data', {})
            user_id = user_data.get('user_id', 'demo_user')

            from gamification import game_manager
            user_progress = game_manager.load_user_progress(user_id)

            st.markdown("### 🎮 Your Progress")

            # Points and rank
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💎 Points", user_progress.get('total_points', 0))
            with col2:
                st.metric("🏆 Rank", game_manager.get_user_rank(user_id))

            # Progress bar to next level
            current_points = user_progress.get('total_points', 0)
            next_level_points = ((current_points // 500) + 1) * 500  # Every 500 points is a new level
            progress = min((current_points % 500) / 500, 1.0)

            st.markdown(f"**Level Progress** ({current_points % 500}/500)")
            st.progress(progress)

            # Quick stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔥 Streak", f"{user_progress.get('current_streak', 0)} days")
            with col2:
                st.metric("🧠 Quizzes", user_progress.get('quizzes_completed', 0))

            # Recent badges
            recent_badges = user_progress.get('badges_earned', [])[-3:]  # Last 3 badges
            if recent_badges:
                st.markdown("**🏅 Recent Badges**")
                for badge in recent_badges:
                    st.markdown(f"• {badge.get('icon', '🏅')} {badge.get('name', 'Badge')}")

        # Session statistics
        elif st.session_state.qa_history:
            stats = get_session_stats(st.session_state.qa_history)
            st.markdown("### Session Stats")
            st.metric("Questions Asked", stats["total_questions"])
            st.metric("Avg Answer Length", f"{stats['avg_answer_length']} chars")
            st.metric("Session Duration", stats["session_duration"])
        
        # Document processing stats
        if st.session_state.chunks:
            processing_stats = get_processing_stats(st.session_state.chunks)
            st.markdown("### Document Stats")
            st.metric("Files Processed", processing_stats["total_files"])
            st.metric("Text Chunks", processing_stats["total_chunks"])
            st.metric("Avg Chunk Length", f"{processing_stats['avg_chunk_length']} chars")

        # Quiz history
        if st.session_state.quiz_history:
            st.markdown("### 🧠 Quiz History")
            st.metric("Quizzes Generated", len(st.session_state.quiz_history))

            # Show recent quizzes
            with st.expander("Recent Quizzes", expanded=False):
                for i, quiz in enumerate(reversed(st.session_state.quiz_history[-3:])):  # Show last 3
                    st.write(f"**Quiz {len(st.session_state.quiz_history) - i}**")
                    st.write(f"🕒 {quiz['timestamp']}")
                    st.write(f"📝 {quiz['num_questions']} questions ({quiz['difficulty']})")
                    st.write(f"🎯 {quiz['topic_focus']}")
                    st.write(f"⚙️ {quiz['generation_method']}")
                    if quiz.get('source_documents'):
                        st.write(f"📄 {', '.join(quiz['source_documents'])}")
                    st.write("---")

            if st.button("🗑️ Clear Quiz History"):
                st.session_state.quiz_history = []
                st.rerun()

        # DeepSeek API Status
        st.markdown("### 🚀 DeepSeek AI")
        from deepseek_integration import DeepSeekClient
        deepseek_client = DeepSeekClient()

        if deepseek_client.is_available():
            st.warning("⚠️ Account Verification Needed")
            st.caption("DeepSeek API key configured but account needs verification")
            if st.button("🔧 Fix DeepSeek Account"):
                st.info("**Steps to fix DeepSeek:**")
                st.info("1. Visit: https://platform.deepseek.com/")
                st.info("2. Complete email verification")
                st.info("3. Check account dashboard for free credits")
                st.info("4. Generate new API key if needed")
                st.info("5. Restart the app after verification")
        else:
            st.error("❌ API Key Missing")
            st.caption("Add DEEPSEEK_API_KEY to .env file")

        # Image-to-Text API Status
        st.markdown("### 🖼️ Image to Text")
        from image_to_text import get_image_processor
        processor = get_image_processor()

        if processor.is_available():
            st.success("✅ Hugging Face API Ready")
            st.caption("🔍 Image-to-text conversion available")
        else:
            st.error("❌ API Token Missing")
            if st.button("ℹ️ Get API Token"):
                display_api_info()


def handle_pdf_upload():
    """Handle PDF file upload and processing."""
    st.header("📄 Upload Academic PDFs")

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        help="Upload lecture notes, textbooks, or research papers"
    )

    if uploaded_files:
        # Display file information
        st.write(f"📁 **{len(uploaded_files)} file(s) selected:**")
        for i, file in enumerate(uploaded_files):
            file_size = len(file.getvalue()) if hasattr(file, 'getvalue') else 0
            st.write(f"   {i+1}. {file.name} ({file_size:,} bytes)")

        if st.button("Process PDFs", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                status_text.text("Starting PDF processing...")
                progress_bar.progress(10)

                # Process PDFs
                status_text.text("Extracting text from PDFs...")
                chunks = process_uploaded_pdfs(uploaded_files)
                progress_bar.progress(60)

                if chunks:
                    status_text.text("Building search index...")
                    # Replace previous chunks with new ones (don't accumulate)
                    st.session_state.chunks = chunks
                    st.session_state.processed_files = [f.name for f in uploaded_files]
                    st.session_state.current_document_chunks = chunks  # Store current document chunks separately

                    # Clear any existing quiz session to ensure fresh questions for new document
                    if hasattr(st.session_state, 'quiz_session'):
                        st.session_state.quiz_session = None
                    if hasattr(st.session_state, 'current_question_index'):
                        st.session_state.current_question_index = 0

                    # Initialize retrieval system
                    st.session_state.retriever = initialize_retrieval_system(chunks)
                    progress_bar.progress(80)

                    # Initialize Watsonx client if not already done
                    status_text.text("Initializing AI client...")
                    if not st.session_state.watsonx_client:
                        st.session_state.watsonx_client = initialize_watsonx_client()
                    progress_bar.progress(100)

                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()

                    # Show success message with details
                    st.success(f"✅ Successfully processed {len(uploaded_files)} files into {len(chunks)} chunks")

                    # Show processing statistics
                    stats = get_processing_stats(chunks)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Files Processed", stats["total_files"])
                    with col2:
                        st.metric("Text Chunks", stats["total_chunks"])
                    with col3:
                        st.metric("Total Characters", f"{stats['total_characters']:,}")

                    # Show file breakdown
                    if stats["file_breakdown"]:
                        st.write("**File Processing Details:**")
                        for filename, chunk_count in stats["file_breakdown"].items():
                            st.write(f"   • {filename}: {chunk_count} chunks")

                    log_user_action("pdf_upload", {"file_count": len(uploaded_files), "chunk_count": len(chunks)})

                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("❌ No text could be extracted from the uploaded files")
                    st.warning("**Possible reasons:**")
                    st.write("• The PDFs might be scanned images without text")
                    st.write("• The PDFs might be password protected")
                    st.write("• The files might be corrupted")
                    st.write("• The PDFs might contain only images/graphics")

            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Error processing PDFs: {str(e)}")

                # Show detailed error information
                with st.expander("🔍 Error Details"):
                    import traceback
                    st.code(traceback.format_exc())

    # Display current files
    if st.session_state.processed_files:
        st.info(f"📁 Currently loaded: {', '.join(st.session_state.processed_files)}")

        # Add button to clear current files
        if st.button("🗑️ Clear Loaded Files"):
            st.session_state.chunks = []
            st.session_state.processed_files = []
            st.session_state.retriever = None
            st.success("✅ Cleared all loaded files")
            st.rerun()


def get_active_ai_client():
    """Get the currently active AI client."""
    provider = st.session_state.ai_provider

    if provider == "deepseek" and st.session_state.deepseek_client:
        return st.session_state.deepseek_client
    elif provider == "openai" and st.session_state.openai_client:
        return st.session_state.openai_client
    elif provider == "gemini" and st.session_state.gemini_client:
        return st.session_state.gemini_client
    elif provider in ["watsonx", "demo", "auto"] and st.session_state.watsonx_client:
        return st.session_state.watsonx_client
    elif provider == "huggingface" and st.session_state.huggingface_client:
        return st.session_state.huggingface_client

    return None


def get_ai_provider_info():
    """Get information about the current AI provider."""
    provider = st.session_state.ai_provider
    client = get_active_ai_client()

    if not client:
        return {"name": "None", "description": "No AI provider active"}

    if provider == "deepseek":
        return {"name": "DeepSeek", "description": "DeepSeek's advanced language model - completely free"}
    elif provider == "openai":
        return {"name": "OpenAI", "description": "ChatGPT models with advanced reasoning"}
    elif provider == "gemini":
        return {"name": "Google Gemini", "description": "Google's advanced AI with multimodal capabilities"}
    elif provider == "watsonx" or (hasattr(client, 'model_id') and client.model_id != "demo-mode"):
        return {"name": "IBM Watsonx", "description": "Enterprise AI with advanced reasoning"}
    elif provider == "huggingface":
        return {"name": "Hugging Face", "description": "Open-source AI models"}
    else:
        return {"name": "Demo Mode", "description": "Context-based responses from your documents"}


def query_ai_provider(client, context: str, question: str):
    """Query the appropriate AI provider."""
    try:
        # Check for DeepSeek client (direct or via OpenRouter)
        if (hasattr(client, 'base_url') and ('deepseek' in str(client.base_url).lower() or 'openrouter' in str(client.base_url).lower())) or \
           (hasattr(client, 'model') and 'deepseek' in str(client.model).lower()):
            result = query_deepseek(client, question, context)
            return {
                "answer": result,
                "success": bool(result),
                "error": None if result else "DeepSeek query failed",
                "prompt_length": len(context) + len(question),
                "response_length": len(result) if result else 0
            }

        # Check for OpenAI client
        elif hasattr(client, 'client') and 'openai' in str(type(client.client)).lower():
            result = query_openai(client, context, question)
            return {
                "answer": result.get("response"),
                "success": result.get("success", False),
                "error": result.get("error"),
                "prompt_length": len(context) + len(question),
                "response_length": len(result.get("response", ""))
            }

        # Check for Gemini client
        elif hasattr(client, 'model') and hasattr(client, 'config'):
            result = query_gemini(client, context, question)
            return {
                "answer": result.get("response"),
                "success": result.get("success", False),
                "error": result.get("error"),
                "prompt_length": len(context) + len(question),
                "response_length": len(result.get("response", ""))
            }

        # Check if it's a Hugging Face client
        if hasattr(client, 'model_name'):
            # Hugging Face client
            prompt = create_academic_prompt_hf(context, question)
            response_text = client.generate_response(prompt, max_new_tokens=300, temperature=0.3)

            if response_text:
                return {
                    "answer": response_text,
                    "success": True,
                    "error": None,
                    "prompt_length": len(prompt),
                    "response_length": len(response_text)
                }
            else:
                return {
                    "answer": None,
                    "success": False,
                    "error": "No response generated from Hugging Face model",
                    "prompt_length": len(prompt),
                    "response_length": 0
                }
        else:
            # IBM Watsonx or Demo client
            return query_watsonx(client, context, question)

    except Exception as e:
        return {
            "answer": None,
            "success": False,
            "error": str(e),
            "prompt_length": 0,
            "response_length": 0
        }


def handle_question_answering():
    """Handle the Q&A interface with voice integration."""
    st.header("❓ Ask Questions")

    if not st.session_state.chunks:
        st.warning("⚠️ Please upload and process PDF files first")
        return

    # Check AI client availability
    ai_client = get_active_ai_client()
    if not ai_client:
        st.error("❌ No AI client initialized. Please select and initialize an AI provider in the sidebar.")
        return

    # Display current AI provider status
    provider_info = get_ai_provider_info()
    st.info(f"🤖 **Using {provider_info['name']}**: {provider_info['description']}")

    # Show document status
    if hasattr(st.session_state, 'processed_files') and st.session_state.processed_files:
        st.success(f"📄 **Ready to answer questions about**: {', '.join(st.session_state.processed_files)}")

    # Initialize voice assistant
    from voice_assistant import initialize_voice_assistant, display_voice_assistant_status
    voice_assistant = initialize_voice_assistant()

    # Voice settings in an expander
    with st.expander("🎤 Voice Settings", expanded=False):
        voice_available = display_voice_assistant_status()

        if voice_available:
            col1, col2 = st.columns(2)

            with col1:
                tts_method = st.selectbox(
                    "Text-to-Speech Method:",
                    ["Browser TTS (Free)", "OpenAI TTS (Requires API Key)"],
                    help="Choose how answers will be spoken"
                )

            with col2:
                if tts_method == "OpenAI TTS (Requires API Key)":
                    voice_option = st.selectbox(
                        "Voice:",
                        ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                        help="Choose OpenAI TTS voice"
                    )
                else:
                    voice_option = "browser"

            # Store voice settings in session state (only if not already set by widget)
            if "tts_method" not in st.session_state:
                st.session_state.tts_method = tts_method
            if "voice_option" not in st.session_state:
                st.session_state.voice_option = voice_option
        else:
            if "tts_method" not in st.session_state:
                st.session_state.tts_method = "Browser TTS (Free)"
            if "voice_option" not in st.session_state:
                st.session_state.voice_option = "browser"

    # Question input methods
    st.markdown("### 💬 Ask Your Question")

    # Create tabs for different input methods
    if voice_assistant and voice_assistant.is_available():
        tab1, tab2 = st.tabs(["⌨️ Type Question", "🎤 Voice Question"])

        with tab1:
            question = st.text_area(
                "Enter your question:",
                placeholder="What is the main concept discussed in chapter 3?",
                height=100,
                key="text_question"
            )

            if st.button("Get Answer", type="primary", key="text_submit"):
                if question.strip():
                    handle_text_question(question, ai_client)

        with tab2:
            st.markdown("Click the button below and speak your question:")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Calibrate microphone button
                if st.button("🎚️ Calibrate Microphone", help="Adjust for background noise"):
                    with st.spinner("Calibrating microphone..."):
                        if voice_assistant.calibrate_microphone():
                            st.success("✅ Microphone calibrated!")
                        else:
                            st.error("❌ Failed to calibrate microphone")

                # Voice question button
                if st.button("🎤 Ask Question (Voice)", type="primary", help="Click and speak your question"):
                    handle_voice_question_integrated(voice_assistant, ai_client)
    else:
        # Text-only mode if voice not available
        question = st.text_area(
            "Enter your question:",
            placeholder="What is the main concept discussed in chapter 3?",
            height=100
        )

        if st.button("Get Answer", type="primary"):
            if question.strip():
                handle_text_question(question, ai_client)


def handle_text_question(question: str, ai_client, input_method: str = "text"):
    """Handle a text-based question."""
    # Check if documents are loaded first
    if not st.session_state.chunks:
        st.error("❌ No documents loaded. Please upload and process PDF files first.")
        return

    # Validate question
    validation = validate_question(question)

    if not validation["valid"]:
        st.error(validation["message"])
        return

    with st.spinner("Searching documents and generating answer..."):
        try:
            # Check if retriever exists and re-initialize if needed
            if not st.session_state.retriever and st.session_state.chunks:
                st.session_state.retriever = initialize_retrieval_system(st.session_state.chunks)

            # Check if retriever is still None
            if not st.session_state.retriever:
                st.error("❌ No documents loaded. Please upload and process PDF files first.")
                return

            # Retrieve relevant chunks
            relevant_chunks = st.session_state.retriever.retrieve_relevant_chunks(
                validation["cleaned_question"],
                top_k=3
            )

            if not relevant_chunks:
                st.warning("⚠️ No relevant content found in the documents")
                return

            # Format context for LLM
            context = format_retrieved_chunks(relevant_chunks)

            # Query AI provider
            response = query_ai_provider(
                ai_client,
                context,
                validation["cleaned_question"]
            )

            if response["success"]:
                # Create Q&A entry
                qa_entry = {
                    "question": validation["cleaned_question"],
                    "answer": response["answer"],
                    "sources": get_chunk_sources(relevant_chunks),
                    "timestamp": datetime.now(),
                    "input_method": input_method
                }

                # Add to history
                st.session_state.qa_history.append(qa_entry)

                # Display answer
                display_answer_with_voice(qa_entry)

                log_user_action("question_answered", {"question_length": len(question), "input_method": input_method})

            else:
                error_msg = format_error_response(response.get("error", "Unknown error"))
                st.error(error_msg)

        except Exception as e:
            st.error(f"❌ Error processing question: {str(e)}")


def handle_voice_question_integrated(voice_assistant, ai_client):
    """Handle a voice question in the integrated Q&A interface."""
    # Step 1: Listen for speech
    with st.spinner("🎤 Listening... Please speak your question"):
        question_text = voice_assistant.listen_for_speech(timeout=10, phrase_time_limit=15)

    if not question_text:
        st.error("❌ Could not understand your question. Please try again.")
        return

    # Display transcribed question
    st.success(f"🎤 **You asked:** {question_text}")

    # Step 2: Process question using the same logic as text questions but mark as voice
    handle_text_question(question_text, ai_client, input_method="voice")


def display_beautiful_qa_interface():
    """Display the beautiful two-column Q&A interface with dark theme."""
    # Two-Column Main Layout with Cards
    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        # PDF Library Section with Card Styling
        st.markdown("""
        <div class="study-card glow">
            <h3 style="color: #00D4AA; margin-top: 0;">📄 Document Library</h3>
            <p style="color: #EAEAEA; opacity: 0.8;">Upload your study materials to get started</p>
        </div>
        """, unsafe_allow_html=True)

        # File upload
        uploaded_files = st.file_uploader(
            "📚 Choose PDF files to upload",
            type="pdf",
            accept_multiple_files=True,
            help="Upload lecture notes, textbooks, research papers, or any study materials"
        )

        # Display uploaded files with enhanced styling
        if uploaded_files:
            st.markdown(f"""
            <div class="answer-card">
                <h4 style="color: #00D4AA; margin-top: 0;">📚 {len(uploaded_files)} file(s) ready for processing</h4>
            </div>
            """, unsafe_allow_html=True)

            for file in uploaded_files:
                file_size = len(file.getvalue()) if hasattr(file, 'getvalue') else 0
                st.markdown(f"""
                <div class="source-card">
                    <strong>✅ {file.name}</strong><br>
                    <span style="opacity: 0.7;">Size: {file_size:,} bytes</span>
                </div>
                """, unsafe_allow_html=True)

            if st.button("🚀 Process Documents", type="primary"):
                handle_pdf_processing(uploaded_files)
        else:
            st.markdown("""
            <div class="study-card" style="text-align: center; padding: 2rem;">
                <h4 style="color: #00D4AA;">📤 Ready to Upload</h4>
                <p style="color: #EAEAEA; opacity: 0.8;">Drag and drop your PDF files above to get started</p>
                <p style="font-size: 2rem; margin: 1rem 0;">📚 📖 📝</p>
            </div>
            """, unsafe_allow_html=True)

        # Current documents status
        if st.session_state.processed_files:
            st.divider()
            st.subheader("📊 Processing Stats")

            # Display metrics
            if st.session_state.chunks:
                stats = get_processing_stats(st.session_state.chunks)
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("📄 Files", stats["total_files"])
                with col2:
                    st.metric("📝 Chunks", stats["total_chunks"])
                with col3:
                    st.metric("📊 Characters", f"{stats['total_characters']:,}")

            # Clear documents button
            if st.button("🗑️ Clear Documents"):
                st.session_state.chunks = []
                st.session_state.processed_files = []
                st.session_state.retriever = None
                st.success("✅ Documents cleared")
                st.rerun()

    with right_col:
        # Chat Workspace with Enhanced Styling
        st.markdown("""
        <div class="study-card glow">
            <h3 style="color: #00D4AA; margin-top: 0;">💬 AI Chat Workspace</h3>
            <p style="color: #EAEAEA; opacity: 0.8;">Ask questions about your documents</p>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.chunks:
            st.markdown("""
            <div class="study-card" style="text-align: center; border: 2px dashed rgba(255, 193, 7, 0.5);">
                <h4 style="color: #FFC107;">⚠️ Documents Required</h4>
                <p style="color: #EAEAEA; opacity: 0.8;">Please upload and process PDF files first</p>
                <p style="font-size: 1.5rem;">📄 ➡️ 🤖</p>
            </div>
            """, unsafe_allow_html=True)
            return

        # Check AI client
        ai_client = get_active_ai_client()
        if not ai_client:
            st.markdown("""
            <div class="study-card" style="text-align: center; border: 2px dashed rgba(255, 99, 99, 0.5);">
                <h4 style="color: #FF6B6B;">❌ AI Not Ready</h4>
                <p style="color: #EAEAEA; opacity: 0.8;">Please initialize an AI provider in the sidebar</p>
                <p style="font-size: 1.5rem;">🤖 ⚙️</p>
            </div>
            """, unsafe_allow_html=True)
            return

        # Display AI status with enhanced styling
        provider_info = get_ai_provider_info()
        st.markdown(f"""
        <div class="answer-card" style="text-align: center;">
            <h4 style="color: #00D4AA; margin-top: 0;">🤖 AI Ready</h4>
            <p style="color: #EAEAEA;"><strong>{provider_info['name']}</strong> is active</p>
            <p style="color: #EAEAEA; opacity: 0.7; font-size: 0.9rem;">{provider_info['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Question input
        question = st.text_area(
            "Type your question here...",
            placeholder="What is the main concept discussed in chapter 3?",
            height=100
        )

        if st.button("🚀 Get Answer", type="primary"):
            if question.strip():
                handle_beautiful_question(question, ai_client)

        # Display recent answer
        if st.session_state.qa_history:
            st.divider()
            st.subheader("💡 Latest Answer")
            latest_qa = st.session_state.qa_history[-1]

            # Answer in container
            with st.container():
                st.markdown(f"> **🤖 AI:** {latest_qa['answer']}")

            # References
            sources = latest_qa.get("sources", [])
            if sources:
                with st.expander(f"📚 Referenced Paragraphs ({len(sources)} sources)"):
                    for i, source in enumerate(sources, 1):
                        st.markdown(f"**Source {i}:** {source['filename']}")
                        st.markdown(f"*{source['preview']}*")
                        st.divider()

    # Session History at bottom
    if st.session_state.qa_history:
        st.divider()
        display_beautiful_history()


def display_answer_with_voice(qa_entry: Dict[str, Any]):
    """Display a formatted answer with optional voice output and dark theme."""
    # Answer with enhanced dark theme styling
    st.markdown(f"""
    <div class="answer-card glow">
        <h3 style="color: #00D4AA; margin-top: 0;">🤖 AI Answer</h3>
        <p style="color: #EAEAEA; line-height: 1.7; font-size: 1.1rem;">{qa_entry['answer']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Voice output if enabled and available
    if hasattr(st.session_state, 'tts_method') and hasattr(st.session_state, 'voice_option'):
        from voice_assistant import initialize_voice_assistant
        voice_assistant = initialize_voice_assistant()

        if voice_assistant and voice_assistant.is_available():
            # Add voice output controls
            col1, col2 = st.columns([3, 1])

            with col2:
                if st.button("🔊 Play Answer", key=f"play_answer_{len(st.session_state.qa_history)}"):
                    play_answer_audio(qa_entry['answer'], st.session_state.tts_method, st.session_state.voice_option)

    # Sources section with enhanced dark theme styling
    sources = qa_entry.get("sources", [])
    if sources:
        with st.expander(f"📖 Referenced Paragraphs ({len(sources)} sources)", expanded=False):
            for i, source in enumerate(sources, 1):
                st.markdown(f"""
                <div class="source-card">
                    <strong style="color: #00D4AA;">📄 Source {i}:</strong> {source['filename']} - {source['section']}<br>
                    <em style="color: #EAEAEA; opacity: 0.8;">{source['preview']}</em>
                </div>
                """, unsafe_allow_html=True)


def play_answer_audio(answer_text: str, tts_method: str, voice_option: str):
    """Play answer using TTS."""
    from voice_assistant import initialize_voice_assistant
    voice_assistant = initialize_voice_assistant()

    if not voice_assistant:
        st.error("❌ Voice assistant not available")
        return

    with st.spinner("🔊 Converting to speech..."):
        if tts_method == "OpenAI TTS (Requires API Key)":
            # Use OpenAI TTS
            audio_bytes = voice_assistant.text_to_speech_openai(answer_text, voice_option)
            if audio_bytes:
                # Create audio player
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            else:
                st.warning("⚠️ OpenAI TTS failed, falling back to browser TTS")
                # Fallback to browser TTS
                js_code = voice_assistant.text_to_speech_browser(answer_text)
                st.components.v1.html(js_code, height=0)
        else:
            # Use browser TTS
            js_code = voice_assistant.text_to_speech_browser(answer_text)
            st.components.v1.html(js_code, height=0)





def display_answer(qa_entry: Dict[str, Any]):
    """Display a formatted answer with sources."""
    st.markdown("### 🤖 Answer")
    
    # Answer card
    st.markdown(f"""
    <div class="answer-card">
        <p style="color: #1e293b; margin: 0; line-height: 1.6;">{qa_entry['answer']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sources section
    sources = qa_entry.get("sources", [])
    if sources:
        with st.expander(f"📖 Referenced Paragraphs ({len(sources)} sources)", expanded=False):
            for i, source in enumerate(sources, 1):
                st.markdown(f"""
                <div class="source-card">
                    <p style="color: #334155; margin: 0; line-height: 1.5;">
                        <strong style="color: #1e293b;">Source {i}:</strong> {source['filename']} - {source['section']}<br>
                        <em style="color: #64748b;">{source['preview']}</em>
                    </p>
                </div>
                """, unsafe_allow_html=True)


def display_qa_history():
    """Display the Q&A session history."""
    if not st.session_state.qa_history:
        return

    st.header("📝 Session History")

    # Export options
    st.markdown("### 📥 Download Options")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Download as Text", type="secondary"):
            export_text = create_qa_session_export(
                st.session_state.qa_history,
                {"files_processed": st.session_state.processed_files}
            )

            filename = create_download_filename("studymate_session", "txt")

            if export_text and isinstance(export_text, str):
                st.download_button(
                    label="💾 Download Text File",
                    data=export_text.encode('utf-8'),
                    file_name=filename,
                    mime="text/plain",
                    key="download_qa_text"
                )

    with col2:
        if st.button("📑 Download as PDF", type="primary"):
            pdf_buffer = create_qa_session_pdf_export(
                st.session_state.qa_history,
                {"files_processed": st.session_state.processed_files}
            )

            if pdf_buffer:
                filename = create_download_filename("studymate_qa_session", "pdf")

                st.download_button(
                    label="💾 Download PDF File",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf",
                    key="download_qa_pdf"
                )
            else:
                st.error("❌ Failed to generate PDF. ReportLab library may not be installed.")

    st.divider()
    
    # Display history (most recent first)
    st.markdown("### 📋 Q&A History")

    for i, qa_item in enumerate(reversed(st.session_state.qa_history)):
        formatted_qa = format_qa_for_display(qa_item)

        # Determine input method icon
        input_method = qa_item.get('input_method', 'text')
        method_icon = "🎤" if input_method == "voice" else "⌨️"

        with st.expander(f"{method_icon} Q{len(st.session_state.qa_history) - i}: {formatted_qa['question'][:80]}...", expanded=False):
            st.markdown(f"**⏰ Time:** {formatted_qa['time']}")
            st.markdown(f"**❓ Question:** {formatted_qa['question']}")
            st.markdown(f"**🤖 Answer:** {formatted_qa['full_answer']}")

            if formatted_qa['sources']:
                st.markdown(f"**📖 Sources:** {formatted_qa['source_count']} references")

            # Voice replay option
            from voice_assistant import initialize_voice_assistant
            voice_assistant = initialize_voice_assistant()
            if voice_assistant and voice_assistant.is_available():
                if st.button(f"🔊 Play Answer", key=f"replay_history_{len(st.session_state.qa_history) - i}"):
                    tts_method = getattr(st.session_state, 'tts_method', 'Browser TTS (Free)')
                    voice_option = getattr(st.session_state, 'voice_option', 'browser')
                    play_answer_audio(formatted_qa['full_answer'], tts_method, voice_option)

            # Individual download options
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                # Create single Q&A text export
                single_qa_text = f"Question: {formatted_qa['question']}\n\nAnswer: {formatted_qa['full_answer']}\n\nTime: {formatted_qa['time']}"
                if formatted_qa['sources']:
                    single_qa_text += f"\nSources: {formatted_qa['source_count']} references"

                if single_qa_text and isinstance(single_qa_text, str):
                    st.download_button(
                        label="📄 Download as Text",
                        data=single_qa_text.encode('utf-8'),
                        file_name=f"qa_item_{len(st.session_state.qa_history) - i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        key=f"download_single_text_{len(st.session_state.qa_history) - i}"
                    )

            with col2:
                # Create single Q&A PDF export
                single_qa_pdf = create_qa_session_pdf_export(
                    [qa_item],
                    {"files_processed": st.session_state.processed_files}
                )

                if single_qa_pdf:
                    st.download_button(
                        label="📑 Download as PDF",
                        data=single_qa_pdf,
                        file_name=f"qa_item_{len(st.session_state.qa_history) - i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        key=f"download_single_pdf_{len(st.session_state.qa_history) - i}"
                    )
                else:
                    st.caption("PDF export not available")


def main():
    """Main application function."""
    # Load environment variables
    load_environment_variables()

    # Initialize session state
    initialize_session_state()

    # Check authentication first
    from login_ui import check_authentication, render_auth_interface

    if not check_authentication():
        # Show login interface if not authenticated
        st.markdown("### 🔐 Authentication Required")
        st.info("Please sign in to access StudyMate's features.")

        authenticated = render_auth_interface()
        if not authenticated:
            st.stop()  # Stop execution if not authenticated

    # User is authenticated - show gamified welcome message
    user_data = st.session_state.get('user_data', {})
    username = user_data.get('full_name') or user_data.get('username', 'User')
    user_id = user_data.get('user_id', 'demo_user')

    # Load user progress for welcome message
    from gamification import game_manager
    user_progress = game_manager.load_user_progress(user_id)

    # Check if this is a new user
    if user_progress.get('quizzes_completed', 0) == 0:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 165, 0, 0.1));
                    border: 2px solid rgba(255, 215, 0, 0.4);
                    border-radius: 15px;
                    padding: 20px;
                    text-align: center;
                    margin: 15px 0;">
            <h2 style="color: #FFD700; margin-top: 0;">🎮 Welcome to StudyMate, {username}!</h2>
            <p style="color: #EAEAEA; font-size: 1.1rem; margin: 10px 0;">
                Get ready for an epic learning adventure! Earn points, unlock badges, and climb the leaderboard! 🚀
            </p>
            <div style="display: flex; justify-content: center; gap: 20px; margin: 15px 0;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem;">💎</div>
                    <div style="color: #00D4AA; font-weight: bold;">Earn Points</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem;">🏆</div>
                    <div style="color: #00D4AA; font-weight: bold;">Unlock Badges</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem;">👑</div>
                    <div style="color: #00D4AA; font-weight: bold;">Top Leaderboard</div>
                </div>
            </div>
            <p style="color: #EAEAEA; opacity: 0.8; font-style: italic;">
                Complete your first quiz to earn the "First Steps" badge and start your journey! 🎯
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Returning user - show progress
        points = user_progress.get('total_points', 0)
        streak = user_progress.get('current_streak', 0)
        rank = game_manager.get_user_rank(user_id)

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 153, 204, 0.1));
                    border: 2px solid rgba(0, 212, 170, 0.3);
                    border-radius: 15px;
                    padding: 15px;
                    text-align: center;
                    margin: 15px 0;">
            <h3 style="color: #00D4AA; margin-top: 0;">🎓 Welcome back, {username}!</h3>
            <div style="display: flex; justify-content: center; gap: 20px; margin: 10px 0;">
                <div><strong>💎 {points} Points</strong></div>
                <div><strong>🏆 Rank #{rank}</strong></div>
                <div><strong>🔥 {streak} Day Streak</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Initialize AI clients if not already done
    if not st.session_state.watsonx_client and not st.session_state.huggingface_client:
        initialize_ai_clients()

    # Render the permanent AI switcher button at the top
    render_ai_switcher()

    # Display header
    display_header()

    # Display sidebar
    display_sidebar()

    # Check if user wants to view profile or settings
    if st.session_state.get('show_profile', False):
        from login_ui import render_user_profile_edit
        render_user_profile_edit()

        if st.button("🔙 Back to StudyMate", type="secondary"):
            st.session_state.show_profile = False
            st.rerun()
        return

    if st.session_state.get('show_settings', False):
        from login_ui import render_user_settings
        render_user_settings()

        if st.button("🔙 Back to StudyMate", type="secondary"):
            st.session_state.show_settings = False
            st.rerun()
        return

    # Mode selector
    st.markdown("### 📋 Select Mode")
    mode = st.radio(
        "Choose your study mode:",
        options=["📚 Q&A Mode", "🧠 Quiz Mode", "💬 General Chatbot", "🖼️ Image to Text"],
        index=0 if not st.session_state.quiz_mode else 1,
        horizontal=True
    )

    # Update quiz mode based on selection
    if mode == "🧠 Quiz Mode":
        st.session_state.quiz_mode = True
    else:
        st.session_state.quiz_mode = False

    st.markdown("---")

    # Main content area based on mode with beautiful layout
    if mode == "🖼️ Image to Text":
        # Image to Text Mode
        handle_image_upload()
    elif mode == "💬 General Chatbot":
        # General Chatbot Mode
        handle_general_chatbot()
    elif st.session_state.quiz_mode:
        # Quiz Mode
        if st.session_state.quiz_session and st.session_state.current_question_index < len(st.session_state.quiz_session.questions):
            # Active quiz
            display_quiz_interface()
        elif st.session_state.quiz_session and st.session_state.current_question_index >= len(st.session_state.quiz_session.questions):
            # Quiz completed - show results
            display_quiz_results()
        else:
            # Quiz generation
            handle_quiz_generation()
    else:
        # Q&A Mode - Beautiful Two-Column Layout
        display_beautiful_qa_interface()
    
    # Footer with enhanced styling
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Study Notes Export at bottom
    if st.session_state.qa_history:
        st.markdown("""
        <div class="study-card glow" style="text-align: center;">
            <h3 style="color: #00D4AA; margin-top: 0;">🎓 Export Your Study Session</h3>
            <p style="color: #EAEAEA; opacity: 0.8;">Download your Q&A session for future reference</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.session_state.qa_history:
                export_text = create_qa_session_export(
                    st.session_state.qa_history,
                    {"files_processed": st.session_state.processed_files}
                )
                if export_text and isinstance(export_text, str):
                    st.download_button(
                        "📚 Download Study Notes",
                        data=export_text.encode('utf-8'),
                        file_name="study_notes.txt",
                        mime="text/plain",
                        type="primary"
                    )
                else:
                    st.info("📝 No study notes available for download yet. Start asking questions to generate content!")
            else:
                st.info("📝 No study notes available for download yet. Start asking questions to generate content!")

    # Footer with educational theme
    st.markdown("""
    <div style="text-align: center; padding: 2rem; margin-top: 3rem; border-top: 1px solid rgba(0, 212, 170, 0.3);">
        <p style="color: #00D4AA; font-size: 1.2rem; margin: 0;">⚡ Crashed Compliers</p>
        <p style="color: #EAEAEA; opacity: 0.7; margin: 0.5rem 0;">Your AI-Powered Academic Assistant</p>
        <p style="color: #EAEAEA; opacity: 0.5; font-size: 0.9rem;">Built for students and learners</p>
        <p style="font-size: 1.5rem; margin: 1rem 0; opacity: 0.3;">🎓 📖 💡 🚀</p>
    </div>
    """, unsafe_allow_html=True)


def handle_quiz_generation():
    """Handle quiz generation interface."""
    if not st.session_state.chunks:
        st.info("📝 Please upload and process PDF documents first to generate quiz questions.")
        return

    st.header("🧠 Quiz Generator")
    st.markdown("Generate multiple choice questions for viva exam preparation!")

    # Show AI provider status
    ai_client = get_active_ai_client()
    if ai_client:
        if hasattr(ai_client, 'client_type') and ai_client.client_type == "demo":
            st.info("ℹ️ Using demo mode. Questions will be generated using fallback mechanism.")
        else:
            st.success("✅ AI provider ready for question generation.")
    else:
        st.warning("⚠️ No AI provider available. Will use fallback question generation.")

    # Quiz configuration
    col1, col2, col3 = st.columns(3)

    with col1:
        num_questions = st.selectbox(
            "Number of Questions",
            options=[3, 5, 10, 15, 20],
            index=1,  # Default to 5
            help="Select how many questions to generate"
        )

    with col2:
        difficulty = st.selectbox(
            "Difficulty Level",
            options=["easy", "medium", "hard"],
            index=1,  # Default to medium
            help="Choose the difficulty level for questions"
        )

    with col3:
        topic_focus = st.text_input(
            "Topic Focus (Optional)",
            placeholder="e.g., Python keywords, loops",
            help="Specify a particular topic to focus on"
        )

    # Show current document status
    if hasattr(st.session_state, 'processed_files') and st.session_state.processed_files:
        st.info(f"📄 **Current Document(s)**: {', '.join(st.session_state.processed_files)}")
        st.caption("Quiz questions will be generated based on the above document(s)")
    else:
        st.warning("⚠️ No documents uploaded. Please upload a PDF document first.")

    # Generate quiz button
    if st.button("🎯 Generate Quiz", type="primary"):
        if not get_active_ai_client():
            st.error("❌ Please initialize an AI provider first!")
            return

        # Check if documents are uploaded
        if not hasattr(st.session_state, 'current_document_chunks') or not st.session_state.current_document_chunks:
            if not st.session_state.chunks:
                st.error("❌ Please upload and process a PDF document first!")
                return
            else:
                st.warning("⚠️ Using previously uploaded documents. Upload a new document for document-specific questions.")
                # Use existing chunks as fallback
                st.session_state.current_document_chunks = st.session_state.chunks

        # Clear previous quiz session to ensure fresh questions
        st.session_state.quiz_session = None
        st.session_state.current_question_index = 0

        with st.spinner(f"Generating {num_questions} {difficulty} questions..."):
            # Get comprehensive context from current document
            if hasattr(st.session_state, 'current_document_chunks') and st.session_state.current_document_chunks:
                # Use more chunks for better document coverage
                chunk_count = min(20, len(st.session_state.current_document_chunks))
                selected_chunks = st.session_state.current_document_chunks[:chunk_count]
                context = format_retrieved_chunks(selected_chunks)

                # Add document metadata for context
                doc_names = st.session_state.processed_files if hasattr(st.session_state, 'processed_files') else ["Document"]
                document_info = f"Document(s): {', '.join(doc_names)}\n"
                document_info += f"Content sections: {len(selected_chunks)} sections\n"
                document_info += f"Total content length: {sum(len(chunk['text']) for chunk in selected_chunks)} characters\n\n"

            else:
                # Fallback to all chunks if current document chunks not available
                chunk_count = min(15, len(st.session_state.chunks)) if st.session_state.chunks else 0
                selected_chunks = st.session_state.chunks[:chunk_count] if st.session_state.chunks else []
                context = format_retrieved_chunks(selected_chunks) if selected_chunks else ""
                document_info = "Using available document content\n\n"

            # Create document-specific context
            full_context = f"{document_info}IMPORTANT: Generate questions SPECIFICALLY about the content below. "
            full_context += f"Questions must be directly related to the concepts, facts, and information in this document. "
            full_context += f"Do not use generic questions that could apply to any document.\n\n{context}"

            # Add topic focus to context if specified
            if topic_focus:
                full_context = f"TOPIC FOCUS: {topic_focus}\n\n{full_context}"

            # Generate questions with enhanced context
            ai_client = get_active_ai_client()
            questions = generate_mcqs_with_ai(ai_client, full_context, num_questions, difficulty, topic_focus)

            if questions:
                # Create quiz session
                st.session_state.quiz_session = create_quiz_session(questions)
                st.session_state.quiz_mode = True
                st.session_state.current_question_index = 0

                # Store quiz in history
                quiz_info = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "num_questions": len(questions),
                    "difficulty": difficulty,
                    "topic_focus": topic_focus or "General",
                    "generation_method": "Fallback" if questions and questions[0].topic in ["Programming Concepts", "Data Structures", "Algorithms", "General"] else "AI-Powered",
                    "source_documents": st.session_state.processed_files if hasattr(st.session_state, 'processed_files') else []
                }
                st.session_state.quiz_history.append(quiz_info)

                # Check if these are fallback questions
                if questions and questions[0].topic in ["Programming Concepts", "Data Structures", "Algorithms", "General"]:
                    st.info(f"ℹ️ Generated {len(questions)} **dynamic {difficulty}** questions using intelligent fallback mode. Questions change each time and are based on your document content.")
                    if topic_focus:
                        st.info(f"🎯 **Topic Focus**: {topic_focus}")
                else:
                    st.success(f"✅ Generated {len(questions)} **dynamic {difficulty}** AI-powered questions! Quiz is ready to start.")
                    if topic_focus:
                        st.success(f"🎯 **Topic Focus**: {topic_focus}")
                st.rerun()
            else:
                st.error("❌ Failed to generate quiz questions. Please try again.")


def display_quiz_interface():
    """Display the quiz taking interface."""
    if not st.session_state.quiz_session:
        return

    quiz = st.session_state.quiz_session
    current_idx = st.session_state.current_question_index

    if current_idx >= len(quiz.questions):
        # Set end time if not already set
        if not hasattr(quiz, 'end_time') or quiz.end_time is None:
            from datetime import datetime
            quiz.end_time = datetime.now()
        display_quiz_results()
        return

    question = quiz.questions[current_idx]

    # Quiz progress with timer
    col1, col2 = st.columns([3, 1])
    with col1:
        progress = (current_idx + 1) / len(quiz.questions)
        st.progress(progress)
        st.markdown(f"**Question {current_idx + 1} of {len(quiz.questions)}** | Difficulty: {question.difficulty.title()}")

    with col2:
        # Timer display
        try:
            if hasattr(quiz, 'start_time') and quiz.start_time is not None:
                from datetime import datetime
                import time
                # Handle datetime objects properly
                if isinstance(quiz.start_time, datetime):
                    # It's a datetime object
                    elapsed = int((datetime.now() - quiz.start_time).total_seconds())
                    st.markdown(f"**⏱️ {elapsed}s**")
                elif isinstance(quiz.start_time, (int, float)):
                    # It's a timestamp
                    elapsed = int(time.time() - quiz.start_time)
                    st.markdown(f"**⏱️ {elapsed}s**")
                else:
                    st.markdown(f"**⏱️ --s**")
        except (TypeError, ValueError, AttributeError):
            # Handle any errors gracefully
            st.markdown(f"**⏱️ --s**")

    # Gamified question display
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 153, 204, 0.1));
                border: 2px solid rgba(0, 212, 170, 0.3);
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;">
        <h3 style="color: #00D4AA; margin-top: 0;">🤔 {question.question}</h3>
        <div style="text-align: right; font-size: 0.9rem; color: #EAEAEA; opacity: 0.7;">
            💎 Points: {10 + (5 if question.difficulty.lower() == 'hard' else 3 if question.difficulty.lower() == 'medium' else 0)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Answer options
    option_labels = ["A", "B", "C", "D"]
    selected_option = None

    for i, option in enumerate(question.options):
        if st.button(f"{option_labels[i]}. {option.text}", key=f"option_{current_idx}_{i}"):
            # Record answer
            quiz.user_answers[current_idx] = i

            # Move to next question
            if current_idx + 1 < len(quiz.questions):
                st.session_state.current_question_index += 1
            else:
                # Quiz completed
                quiz.end_time = datetime.now()
                correct, total, percentage = calculate_quiz_score(quiz)
                quiz.score = correct

            st.rerun()

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if current_idx > 0:
            if st.button("⬅️ Previous"):
                st.session_state.current_question_index -= 1
                st.rerun()

    with col2:
        if st.button("🏁 Finish Quiz"):
            quiz.end_time = datetime.now()
            correct, total, percentage = calculate_quiz_score(quiz)
            quiz.score = correct
            st.session_state.current_question_index = len(quiz.questions)  # Go to results
            st.rerun()

    with col3:
        if current_idx < len(quiz.questions) - 1:
            if st.button("➡️ Skip"):
                st.session_state.current_question_index += 1
                st.rerun()


def display_quiz_results():
    """Display gamified quiz results with points, badges, and achievements."""
    if not st.session_state.quiz_session:
        return

    quiz = st.session_state.quiz_session
    correct, total, percentage = calculate_quiz_score(quiz)

    # Calculate time taken
    try:
        if hasattr(quiz, 'start_time') and quiz.start_time is not None:
            from datetime import datetime
            import time
            # Handle datetime objects properly
            if isinstance(quiz.start_time, datetime):
                # It's a datetime object
                if hasattr(quiz, 'end_time') and quiz.end_time:
                    time_taken = max(1, int((quiz.end_time - quiz.start_time).total_seconds()))
                else:
                    time_taken = max(1, int((datetime.now() - quiz.start_time).total_seconds()))
                quiz.time_taken = time_taken  # Store for future reference
            elif isinstance(quiz.start_time, (int, float)):
                # It's a timestamp
                time_taken = max(1, int(time.time() - quiz.start_time))
                quiz.time_taken = time_taken
            else:
                time_taken = getattr(quiz, 'time_taken', 60)  # Default fallback
        else:
            time_taken = getattr(quiz, 'time_taken', 60)  # Default to 60 seconds if not tracked
    except (TypeError, ValueError, AttributeError):
        # Handle any type errors gracefully
        time_taken = getattr(quiz, 'time_taken', 60)  # Default fallback

    # Determine subject from quiz topic or default
    subject = getattr(quiz, 'subject', 'General Knowledge')

    # Display gamified results
    from gamified_ui import display_quiz_results_gamified, display_leaderboard, display_next_challenge, display_motivational_message

    # Show gamified results
    display_quiz_results_gamified(correct, total, time_taken, subject)

    # Show leaderboard
    st.markdown("---")
    display_leaderboard()

    # Show next challenge
    st.markdown("---")
    display_next_challenge()

    # Show motivational message
    performance = {"accuracy": percentage}
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('user_id', 'demo_user')

    from gamification import game_manager
    user_progress = game_manager.load_user_progress(user_id)
    display_motivational_message(performance, user_progress)

    st.markdown("---")
    st.header("📋 Detailed Review")

    # Detailed feedback
    st.subheader("📋 Detailed Feedback")

    feedback = get_quiz_feedback(quiz)

    for item in feedback:
        with st.expander(f"Question {item['question_index'] + 1}: {'✅' if item['is_correct'] else '❌'}"):
            st.markdown(f"**Question:** {item['question']}")
            st.markdown(f"**Your Answer:** {item['user_answer']}")
            st.markdown(f"**Correct Answer:** {item['correct_answer']}")

            if item['explanation']:
                st.markdown(f"**Explanation:** {item['explanation']}")

            st.markdown(f"**Topic:** {item['topic']} | **Difficulty:** {item['difficulty'].title()}")

    # Download section
    st.subheader("📥 Download Quiz")

    download_col1, download_col2 = st.columns(2)

    with download_col1:
        st.markdown("**📄 With Answers**")
        if st.button("📄 Download Word (with answers)", key="word_with_answers"):
            word_buffer = generate_quiz_word_document(st.session_state.quiz_session, include_answers=True)
            if word_buffer:
                st.download_button(
                    label="💾 Download Word Document",
                    data=word_buffer,
                    file_name=f"quiz_with_answers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="download_word_with_answers"
                )
            else:
                st.error("❌ Failed to generate Word document")

        if st.button("📑 Download PDF (with answers)", key="pdf_with_answers"):
            pdf_buffer = generate_quiz_pdf_document(st.session_state.quiz_session, include_answers=True)
            if pdf_buffer:
                st.download_button(
                    label="💾 Download PDF Document",
                    data=pdf_buffer,
                    file_name=f"quiz_with_answers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_pdf_with_answers"
                )
            else:
                st.error("❌ Failed to generate PDF document")

    with download_col2:
        st.markdown("**❓ Questions Only**")
        if st.button("📄 Download Word (questions only)", key="word_questions_only"):
            word_buffer = generate_quiz_word_document(st.session_state.quiz_session, include_answers=False)
            if word_buffer:
                st.download_button(
                    label="💾 Download Word Document",
                    data=word_buffer,
                    file_name=f"quiz_questions_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="download_word_questions_only"
                )
            else:
                st.error("❌ Failed to generate Word document")

        if st.button("📑 Download PDF (questions only)", key="pdf_questions_only"):
            pdf_buffer = generate_quiz_pdf_document(st.session_state.quiz_session, include_answers=False)
            if pdf_buffer:
                st.download_button(
                    label="💾 Download PDF Document",
                    data=pdf_buffer,
                    file_name=f"quiz_questions_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_pdf_questions_only"
                )
            else:
                st.error("❌ Failed to generate PDF document")

    st.divider()

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Take Another Quiz"):
            st.session_state.quiz_session = None
            st.session_state.quiz_mode = False
            st.session_state.current_question_index = 0
            st.rerun()

    with col2:
        if st.button("📚 Back to Q&A"):
            st.session_state.quiz_mode = False
            st.rerun()


def handle_pdf_processing(uploaded_files):
    """Handle PDF processing with beautiful progress display."""
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("🔄 Starting PDF processing...")
        progress_bar.progress(10)

        # Process PDFs
        status_text.text("📄 Extracting text from PDFs...")
        chunks = process_uploaded_pdfs(uploaded_files)
        progress_bar.progress(60)

        if chunks:
            status_text.text("🔍 Building search index...")
            # Replace previous chunks with new ones
            st.session_state.chunks = chunks
            st.session_state.processed_files = [f.name for f in uploaded_files]
            st.session_state.current_document_chunks = chunks

            # Clear any existing quiz session
            if hasattr(st.session_state, 'quiz_session'):
                st.session_state.quiz_session = None
            if hasattr(st.session_state, 'current_question_index'):
                st.session_state.current_question_index = 0

            # Initialize retrieval system
            st.session_state.retriever = initialize_retrieval_system(chunks)
            progress_bar.progress(80)

            # Initialize AI client if not already done
            status_text.text("🤖 Initializing AI client...")
            if not st.session_state.watsonx_client:
                st.session_state.watsonx_client = initialize_watsonx_client()
            progress_bar.progress(100)

            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

            # Show success message
            st.success(f"✅ Successfully processed {len(uploaded_files)} files into {len(chunks)} chunks")

            log_user_action("pdf_upload", {"file_count": len(uploaded_files), "chunk_count": len(chunks)})
            st.rerun()

        else:
            progress_bar.empty()
            status_text.empty()
            st.error("❌ No text could be extracted from the uploaded files")
            st.warning("**Possible reasons:**")
            st.write("• The PDFs might be scanned images without text")
            st.write("• The PDFs might be password protected")
            st.write("• The files might be corrupted")

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Error processing PDFs: {str(e)}")


def handle_beautiful_question(question: str, ai_client):
    """Handle question with beautiful response display."""
    # Validate question
    validation = validate_question(question)

    if not validation["valid"]:
        st.error(validation["message"])
        return

    with st.spinner("🤖 Thinking..."):
        try:
            # Check if retriever exists
            if not st.session_state.retriever and st.session_state.chunks:
                st.session_state.retriever = initialize_retrieval_system(st.session_state.chunks)

            if not st.session_state.retriever:
                st.error("❌ No documents loaded")
                return

            # Retrieve relevant chunks
            relevant_chunks = st.session_state.retriever.retrieve_relevant_chunks(
                validation["cleaned_question"],
                top_k=3
            )

            if not relevant_chunks:
                st.warning("⚠️ No relevant content found in the documents")
                return

            # Format context for LLM
            context = format_retrieved_chunks(relevant_chunks)

            # Query AI provider
            response = query_ai_provider(
                ai_client,
                context,
                validation["cleaned_question"]
            )

            if response["success"]:
                # Create Q&A entry
                qa_entry = {
                    "question": validation["cleaned_question"],
                    "answer": response["answer"],
                    "sources": get_chunk_sources(relevant_chunks),
                    "timestamp": datetime.now(),
                    "input_method": "text"
                }

                # Add to history
                st.session_state.qa_history.append(qa_entry)

                log_user_action("question_answered", {"question_length": len(question)})
                st.rerun()

            else:
                error_msg = format_error_response(response.get("error", "Unknown error"))
                st.error(error_msg)

        except Exception as e:
            st.error(f"❌ Error processing question: {str(e)}")


def display_beautiful_history():
    """Display chat history with beautiful Streamlit styling."""
    st.subheader("🕒 Chat History")

    # Export options with metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 Export Text"):
            export_text = create_qa_session_export(
                st.session_state.qa_history,
                {"files_processed": st.session_state.processed_files}
            )

            filename = create_download_filename("studymate_session", "txt")
            if export_text and isinstance(export_text, str):
                st.download_button(
                    label="💾 Download",
                    data=export_text.encode('utf-8'),
                    file_name=filename,
                    mime="text/plain"
                )

    with col2:
        if st.button("📑 Export PDF"):
            pdf_buffer = create_qa_session_pdf_export(
                st.session_state.qa_history,
                {"files_processed": st.session_state.processed_files}
            )

            if pdf_buffer:
                filename = create_download_filename("studymate_qa_session", "pdf")
                st.download_button(
                    label="💾 Download",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf"
                )

    with col3:
        st.metric("📊 Total Q&As", len(st.session_state.qa_history))


if __name__ == "__main__":
    main()
