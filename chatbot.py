"""
General Chatbot Module for StudyMate
Provides conversational AI without requiring PDF documents
"""

import streamlit as st
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatbotSession:
    """Manages a general chatbot conversation session."""
    
    def __init__(self):
        """Initialize chatbot session."""
        self.conversation_history = []
        self.session_start_time = datetime.now()
        self.total_messages = 0
        self.current_model = None
    
    def add_message(self, role: str, content: str, model: str = None):
        """Add a message to the conversation history."""
        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now(),
            "model": model if model else self.current_model
        }
        self.conversation_history.append(message)
        self.total_messages += 1
    
    def get_conversation_context(self, max_messages: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context for AI."""
        # Return last max_messages for context
        return self.conversation_history[-max_messages:] if self.conversation_history else []
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
        self.total_messages = 0
        self.session_start_time = datetime.now()
    
    def export_conversation(self) -> str:
        """Export conversation as text."""
        if not self.conversation_history:
            return "No conversation to export."
        
        export_lines = []
        export_lines.append("=" * 60)
        export_lines.append("StudyMate - General Chatbot Conversation")
        export_lines.append("=" * 60)
        export_lines.append(f"Session Start: {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        export_lines.append(f"Total Messages: {self.total_messages}")
        export_lines.append(f"Export Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        export_lines.append("")
        
        for i, message in enumerate(self.conversation_history, 1):
            role_icon = "👤" if message["role"] == "user" else "🤖"
            model_info = f" ({message.get('model', 'Unknown')})" if message["role"] == "assistant" else ""
            
            export_lines.append(f"Message {i} - {role_icon} {message['role'].title()}{model_info}")
            export_lines.append(f"Time: {message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            export_lines.append(f"Content: {message['content']}")
            export_lines.append("-" * 40)
        
        return "\n".join(export_lines)


def initialize_chatbot_session() -> ChatbotSession:
    """Initialize chatbot session in session state."""
    if 'chatbot_session' not in st.session_state or st.session_state.chatbot_session is None:
        st.session_state.chatbot_session = ChatbotSession()
    return st.session_state.chatbot_session


def query_general_ai_provider(ai_client, user_message: str, conversation_context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Query AI provider for general conversation without document context.
    
    Args:
        ai_client: The AI client to use
        user_message: User's message
        conversation_context: Previous conversation messages
        
    Returns:
        Dict with success status and response
    """
    try:
        # Build conversation context
        context_messages = []
        
        # Add system message for general conversation
        system_message = """You are StudyMate, a helpful AI assistant. You can discuss any topic, answer questions, help with learning, provide explanations, assist with homework, and engage in general conversation. Be friendly, informative, and helpful."""
        
        # Add conversation history for context
        if conversation_context:
            for msg in conversation_context:
                role = "user" if msg["role"] == "user" else "assistant"
                context_messages.append({"role": role, "content": msg["content"]})
        
        # Add current user message
        context_messages.append({"role": "user", "content": user_message})
        
        # Query based on client type - improved detection

        # Check for OpenRouter client (DeepSeek via OpenRouter)
        if hasattr(ai_client, 'base_url') and 'openrouter' in str(ai_client.base_url):
            # OpenRouter client - use requests directly
            import requests

            payload = {
                "model": getattr(ai_client, 'model', 'deepseek/deepseek-chat'),
                "messages": [{"role": "system", "content": system_message}] + context_messages,
                "max_tokens": 1500,
                "temperature": 0.7
            }

            response = requests.post(
                f"{ai_client.base_url}/chat/completions",
                headers=ai_client.headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('choices') and len(data['choices']) > 0:
                    return {
                        "success": True,
                        "answer": data['choices'][0]['message']['content'].strip()
                    }
            return {"success": False, "error": f"OpenRouter API error: {response.status_code}"}

        # Check for OpenAI-style client (OpenAI)
        elif hasattr(ai_client, 'client') and hasattr(ai_client.client, 'chat'):
            response = ai_client.client.chat.completions.create(
                model=getattr(ai_client, 'model_name', 'gpt-3.5-turbo'),
                messages=[{"role": "system", "content": system_message}] + context_messages,
                max_tokens=1500,
                temperature=0.7
            )

            if response.choices and len(response.choices) > 0:
                return {
                    "success": True,
                    "answer": response.choices[0].message.content.strip()
                }
            else:
                return {"success": False, "error": "No response from OpenAI"}

        # Check for Gemini client
        elif hasattr(ai_client, 'model') and hasattr(ai_client, 'config') and hasattr(ai_client.model, 'generate_content'):
            # Format conversation for Gemini
            conversation_text = system_message + "\n\n"
            if conversation_context:
                for msg in conversation_context:
                    role_label = "User" if msg["role"] == "user" else "Assistant"
                    conversation_text += f"{role_label}: {msg['content']}\n"
            conversation_text += f"User: {user_message}\nAssistant:"

            response = ai_client.model.generate_content(conversation_text)

            if response and hasattr(response, 'text'):
                return {
                    "success": True,
                    "answer": response.text.strip()
                }
            else:
                return {"success": False, "error": "No response from Gemini"}

        # Check for DeepSeek direct client
        elif hasattr(ai_client, 'api_key') and hasattr(ai_client, 'base_url') and 'deepseek' in str(ai_client.base_url):
            # Direct DeepSeek client
            import requests

            payload = {
                "model": getattr(ai_client, 'model', 'deepseek-chat'),
                "messages": [{"role": "system", "content": system_message}] + context_messages,
                "max_tokens": 1500,
                "temperature": 0.7
            }

            response = requests.post(
                f"{ai_client.base_url}/chat/completions",
                headers=ai_client.headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('choices') and len(data['choices']) > 0:
                    return {
                        "success": True,
                        "answer": data['choices'][0]['message']['content'].strip()
                    }
            return {"success": False, "error": f"DeepSeek API error: {response.status_code}"}

        # Check for Watsonx or HuggingFace client
        elif hasattr(ai_client, 'generate'):
            # Format conversation for these clients
            conversation_text = system_message + "\n\n"
            if conversation_context:
                for msg in conversation_context:
                    role_label = "User" if msg["role"] == "user" else "Assistant"
                    conversation_text += f"{role_label}: {msg['content']}\n"
            conversation_text += f"User: {user_message}\nAssistant:"

            response = ai_client.generate(conversation_text)

            if response and response.get("success"):
                return {
                    "success": True,
                    "answer": response.get("response", "").strip()
                }
            else:
                return {"success": False, "error": response.get("error", "Unknown error")}

        else:
            # Debug information
            client_type = type(ai_client).__name__
            client_attrs = [attr for attr in dir(ai_client) if not attr.startswith('_')]
            return {"success": False, "error": f"Unsupported AI client type: {client_type}. Available attributes: {client_attrs[:10]}"}
            
    except Exception as e:
        logger.error(f"Error querying general AI provider: {e}")
        return {"success": False, "error": str(e)}


def handle_general_chatbot():
    """Handle the general chatbot interface with vibrant dark theme."""
    # Header with enhanced styling
    st.markdown("""
    <div class="study-card glow education-bg">
        <h2 style="color: #00D4AA; margin-top: 0; text-align: center;">💬 General AI Chatbot</h2>
        <p style="color: #EAEAEA; opacity: 0.9; text-align: center; font-size: 1.1rem;">
            Chat with AI models without needing documents. Perfect for learning, homework help, and conversations!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chatbot session
    chatbot_session = initialize_chatbot_session()
    
    # Check AI client availability
    from streamlit_app import get_active_ai_client, get_ai_provider_info
    ai_client = get_active_ai_client()
    if not ai_client:
        st.error("❌ No AI client initialized. Please select and initialize an AI provider in the sidebar.")
        return
    
    # Display current AI provider status with enhanced styling
    provider_info = get_ai_provider_info()
    st.markdown(f"""
    <div class="answer-card" style="text-align: center; margin: 1rem 0;">
        <h4 style="color: #00D4AA; margin-top: 0;">🤖 Connected to {provider_info['name']}</h4>
        <p style="color: #EAEAEA; opacity: 0.8;">{provider_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Chat controls with beautiful metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💬 Messages", chatbot_session.total_messages)

    with col2:
        if st.button("🗑️ Clear Chat", help="Clear conversation history"):
            chatbot_session.clear_conversation()
            st.rerun()

    with col3:
        if chatbot_session.conversation_history:
            export_text = chatbot_session.export_conversation()
            st.download_button(
                label="📥 Export",
                data=export_text,
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

    with col4:
        if chatbot_session.conversation_history:
            st.metric("🕒 Session", f"{len(chatbot_session.conversation_history)//2} Q&As")
    
    st.divider()

    # Chat interface
    st.subheader("💭 Conversation")
    
    # Display conversation history
    if chatbot_session.conversation_history:
        # Create a container for the chat history
        chat_container = st.container()
        
        with chat_container:
            for message in chatbot_session.conversation_history:
                if message["role"] == "user":
                    # User message with enhanced dark theme styling
                    st.markdown(f"""
                    <div class="chat-user">
                        <strong>👤 You</strong> <span style="opacity: 0.7; font-size: 0.9rem;">({message['timestamp'].strftime('%H:%M')})</span><br>
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Assistant message with enhanced dark theme styling
                    model_name = message.get('model', 'AI')
                    st.markdown(f"""
                    <div class="chat-ai">
                        <strong>🤖 {model_name}</strong> <span style="opacity: 0.7; font-size: 0.9rem;">({message['timestamp'].strftime('%H:%M')})</span><br>
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="study-card" style="text-align: center; padding: 2rem;">
            <h4 style="color: #00D4AA;">👋 Welcome to AI Chat!</h4>
            <p style="color: #EAEAEA; opacity: 0.8;">Start a conversation! Ask me anything - I can help with learning, answer questions, or just chat.</p>
            <p style="font-size: 2rem; margin: 1rem 0;">🤖 💬 🎓</p>
        </div>
        """, unsafe_allow_html=True)

    # Message input with enhanced styling
    st.markdown("""
    <div class="study-card">
        <h3 style="color: #00D4AA; margin-top: 0;">✍️ Send Message</h3>
        <p style="color: #EAEAEA; opacity: 0.8;">Type your message or use voice input</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize voice assistant for chatbot
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
                    help="Choose how responses will be spoken",
                    key="chatbot_tts_method"
                )
            
            with col2:
                if tts_method == "OpenAI TTS (Requires API Key)":
                    voice_option = st.selectbox(
                        "Voice:",
                        ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                        help="Choose OpenAI TTS voice",
                        key="chatbot_voice_option"
                    )
                else:
                    voice_option = "browser"
            
            # Store voice settings in session state (only if not already set by widget)
            if "chatbot_tts_method" not in st.session_state:
                st.session_state.chatbot_tts_method = tts_method
            if "chatbot_voice_option" not in st.session_state:
                st.session_state.chatbot_voice_option = voice_option
        else:
            if "chatbot_tts_method" not in st.session_state:
                st.session_state.chatbot_tts_method = "Browser TTS (Free)"
            if "chatbot_voice_option" not in st.session_state:
                st.session_state.chatbot_voice_option = "browser"
    
    # Input methods
    if voice_assistant and voice_assistant.is_available():
        tab1, tab2 = st.tabs(["⌨️ Type Message", "🎤 Voice Message"])
        
        with tab1:
            user_input = st.text_area(
                "Type your message:",
                placeholder="Ask me anything! I can help with learning, answer questions, or just chat...",
                height=100,
                key="chatbot_text_input"
            )
            
            if st.button("Send Message", type="primary", key="send_text_message"):
                if user_input.strip():
                    handle_chatbot_message(user_input.strip(), ai_client, chatbot_session, provider_info['name'])
        
        with tab2:
            st.markdown("Click the button below and speak your message:")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Calibrate microphone button
                if st.button("🎚️ Calibrate Microphone", help="Adjust for background noise", key="chatbot_calibrate"):
                    with st.spinner("Calibrating microphone..."):
                        if voice_assistant.calibrate_microphone():
                            st.success("✅ Microphone calibrated!")
                        else:
                            st.error("❌ Failed to calibrate microphone")
                
                # Voice message button
                if st.button("🎤 Send Voice Message", type="primary", help="Click and speak your message", key="send_voice_message"):
                    handle_voice_chatbot_message(voice_assistant, ai_client, chatbot_session, provider_info['name'])
    else:
        # Text-only mode if voice not available
        user_input = st.text_area(
            "Type your message:",
            placeholder="Ask me anything! I can help with learning, answer questions, or just chat...",
            height=100
        )
        
        if st.button("Send Message", type="primary"):
            if user_input.strip():
                handle_chatbot_message(user_input.strip(), ai_client, chatbot_session, provider_info['name'])


def handle_chatbot_message(user_message: str, ai_client, chatbot_session: ChatbotSession, model_name: str):
    """Handle a chatbot message (text or voice)."""
    # Add user message to conversation
    chatbot_session.add_message("user", user_message)
    chatbot_session.current_model = model_name

    # Get conversation context
    conversation_context = chatbot_session.get_conversation_context(max_messages=10)

    # Query AI provider
    with st.spinner("🤖 Thinking..."):
        response = query_general_ai_provider(ai_client, user_message, conversation_context[:-1])  # Exclude current message

        if response["success"]:
            # Add assistant response to conversation
            chatbot_session.add_message("assistant", response["answer"], model_name)

            # Display the new response with voice option
            display_chatbot_response(response["answer"], model_name)

            # Log user action
            from utils import log_user_action
            log_user_action("chatbot_message", {
                "message_length": len(user_message),
                "response_length": len(response["answer"]),
                "model": model_name
            })

            # Rerun to update the conversation display
            st.rerun()

        else:
            st.error(f"❌ Error getting response: {response.get('error', 'Unknown error')}")


def handle_voice_chatbot_message(voice_assistant, ai_client, chatbot_session: ChatbotSession, model_name: str):
    """Handle a voice chatbot message."""
    # Step 1: Listen for speech
    with st.spinner("🎤 Listening... Please speak your message"):
        user_message = voice_assistant.listen_for_speech(timeout=10, phrase_time_limit=15)

    if not user_message:
        st.error("❌ Could not understand your message. Please try again.")
        return

    # Display transcribed message
    st.success(f"🎤 **You said:** {user_message}")

    # Process the message
    handle_chatbot_message(user_message, ai_client, chatbot_session, model_name)


def display_chatbot_response(response_text: str, model_name: str):
    """Display a chatbot response with optional voice output."""
    # Voice output if enabled and available
    if (hasattr(st.session_state, 'chatbot_tts_method') and
        hasattr(st.session_state, 'chatbot_voice_option')):

        from voice_assistant import initialize_voice_assistant
        voice_assistant = initialize_voice_assistant()

        if voice_assistant and voice_assistant.is_available():
            # Add voice output controls
            col1, col2 = st.columns([4, 1])

            with col2:
                if st.button("🔊 Play Response", key=f"play_chatbot_{len(st.session_state.chatbot_session.conversation_history)}"):
                    play_chatbot_audio(response_text, st.session_state.chatbot_tts_method, st.session_state.chatbot_voice_option)


def play_chatbot_audio(response_text: str, tts_method: str, voice_option: str):
    """Play chatbot response using TTS."""
    from voice_assistant import initialize_voice_assistant
    voice_assistant = initialize_voice_assistant()

    if not voice_assistant:
        st.error("❌ Voice assistant not available")
        return

    with st.spinner("🔊 Converting to speech..."):
        if tts_method == "OpenAI TTS (Requires API Key)":
            # Use OpenAI TTS
            audio_bytes = voice_assistant.text_to_speech_openai(response_text, voice_option)
            if audio_bytes:
                # Create audio player
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            else:
                st.warning("⚠️ OpenAI TTS failed, falling back to browser TTS")
                # Fallback to browser TTS
                js_code = voice_assistant.text_to_speech_browser(response_text)
                st.components.v1.html(js_code, height=0)
        else:
            # Use browser TTS
            js_code = voice_assistant.text_to_speech_browser(response_text)
            st.components.v1.html(js_code, height=0)
