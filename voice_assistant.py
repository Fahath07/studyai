"""
Voice Assistant Module for StudyMate
Handles Speech-to-Text, Text-to-Speech, and voice-enabled Q&A
"""

import streamlit as st
import tempfile
import os
import io
import logging
from typing import Optional, Dict, Any, Tuple
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import required libraries
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("speech_recognition not available. Install with: pip install SpeechRecognition")

try:
    import pydub
    from pydub import AudioSegment
    from pydub.playback import play
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("pydub not available. Install with: pip install pydub")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("pyaudio not available. Install with: pip install pyaudio")


class VoiceAssistant:
    """Voice-enabled assistant for StudyMate."""
    
    def __init__(self):
        """Initialize the voice assistant."""
        self.recognizer = sr.Recognizer() if SPEECH_RECOGNITION_AVAILABLE else None
        self.microphone = sr.Microphone() if SPEECH_RECOGNITION_AVAILABLE and PYAUDIO_AVAILABLE else None
        self.conversation_history = []
        
        # Configure recognizer settings
        if self.recognizer:
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.operation_timeout = None
            self.recognizer.phrase_threshold = 0.3
            self.recognizer.non_speaking_duration = 0.8
    
    def is_available(self) -> bool:
        """Check if voice assistant is available."""
        return (SPEECH_RECOGNITION_AVAILABLE and 
                PYAUDIO_AVAILABLE and 
                self.recognizer is not None and 
                self.microphone is not None)
    
    def get_missing_dependencies(self) -> list:
        """Get list of missing dependencies."""
        missing = []
        if not SPEECH_RECOGNITION_AVAILABLE:
            missing.append("SpeechRecognition")
        if not PYAUDIO_AVAILABLE:
            missing.append("pyaudio")
        if not PYDUB_AVAILABLE:
            missing.append("pydub")
        return missing
    
    def calibrate_microphone(self) -> bool:
        """Calibrate microphone for ambient noise."""
        if not self.is_available():
            return False
        
        try:
            with self.microphone as source:
                logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            return True
        except Exception as e:
            logger.error(f"Error calibrating microphone: {e}")
            return False
    
    def listen_for_speech(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Listen for speech and convert to text.
        
        Args:
            timeout: Seconds to wait for speech to start
            phrase_time_limit: Maximum seconds for the phrase
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            with self.microphone as source:
                logger.info("Listening for speech...")
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            logger.info("Processing speech...")
            # Use Google Speech Recognition (free)
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout - no speech detected")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during speech recognition: {e}")
            return None
    
    def text_to_speech_openai(self, text: str, voice: str = "alloy") -> Optional[bytes]:
        """
        Convert text to speech using OpenAI TTS.
        
        Args:
            text: Text to convert
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            
        Returns:
            Audio bytes or None if failed
        """
        try:
            from openai import OpenAI
            
            # Get OpenAI API key from environment or session state
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key and hasattr(st.session_state, 'openai_api_key'):
                api_key = st.session_state.openai_api_key
            
            if not api_key:
                logger.error("OpenAI API key not found")
                return None
            
            client = OpenAI(api_key=api_key)
            
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text[:4096]  # Limit text length
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error with OpenAI TTS: {e}")
            return None
    
    def text_to_speech_browser(self, text: str) -> str:
        """
        Generate JavaScript code for browser-based TTS.
        
        Args:
            text: Text to speak
            
        Returns:
            JavaScript code for TTS
        """
        # Escape text for JavaScript
        escaped_text = text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
        
        js_code = f"""
        <script>
        function speakText() {{
            if ('speechSynthesis' in window) {{
                const utterance = new SpeechSynthesisUtterance('{escaped_text}');
                utterance.rate = 0.9;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                // Try to use a natural voice
                const voices = speechSynthesis.getVoices();
                const preferredVoices = voices.filter(voice => 
                    voice.lang.startsWith('en') && 
                    (voice.name.includes('Natural') || voice.name.includes('Neural'))
                );
                
                if (preferredVoices.length > 0) {{
                    utterance.voice = preferredVoices[0];
                }} else if (voices.length > 0) {{
                    utterance.voice = voices.find(voice => voice.lang.startsWith('en')) || voices[0];
                }}
                
                speechSynthesis.speak(utterance);
            }} else {{
                console.error('Speech synthesis not supported');
            }}
        }}
        
        // Auto-play the speech
        speakText();
        </script>
        """
        
        return js_code
    
    def play_audio_bytes(self, audio_bytes: bytes) -> bool:
        """
        Play audio from bytes.
        
        Args:
            audio_bytes: Audio data
            
        Returns:
            True if successful, False otherwise
        """
        if not PYDUB_AVAILABLE:
            return False
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            # Load and play audio
            audio = AudioSegment.from_mp3(tmp_file_path)
            play(audio)
            
            # Clean up
            os.unlink(tmp_file_path)
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
    
    def add_to_conversation_history(self, question: str, answer: str):
        """Add Q&A to conversation history."""
        self.conversation_history.append({
            "question": question,
            "answer": answer,
            "timestamp": time.time()
        })
        
        # Keep only last 10 conversations for context
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_conversation_context(self) -> str:
        """Get recent conversation context for AI."""
        if not self.conversation_history:
            return ""
        
        context_parts = []
        for item in self.conversation_history[-3:]:  # Last 3 conversations
            context_parts.append(f"Q: {item['question']}")
            context_parts.append(f"A: {item['answer'][:200]}...")  # Truncate long answers
        
        return "\n".join(context_parts)


def initialize_voice_assistant() -> VoiceAssistant:
    """Initialize voice assistant in session state."""
    if 'voice_assistant' not in st.session_state or st.session_state.voice_assistant is None:
        st.session_state.voice_assistant = VoiceAssistant()
    return st.session_state.voice_assistant


def display_voice_assistant_status():
    """Display voice assistant availability status."""
    assistant = initialize_voice_assistant()

    if assistant and assistant.is_available():
        st.success("🎤 Voice Assistant Ready!")
        return True
    else:
        missing_deps = assistant.get_missing_dependencies()
        st.warning(f"🎤 Voice Assistant Unavailable. Missing: {', '.join(missing_deps)}")
        
        with st.expander("📋 Installation Instructions"):
            st.markdown("""
            To enable voice features, install the required dependencies:
            
            ```bash
            pip install SpeechRecognition pyaudio pydub
            ```
            
            **Note:** On some systems, you may need additional setup:
            - **Windows**: pyaudio should install automatically
            - **macOS**: `brew install portaudio` then `pip install pyaudio`
            - **Linux**: `sudo apt-get install portaudio19-dev` then `pip install pyaudio`
            """)
        
        return False


def handle_voice_qa_interface():
    """Handle the voice-enabled Q&A interface."""
    st.header("🎤 Voice Assistant")

    # Initialize voice assistant
    assistant = initialize_voice_assistant()

    # Display status
    if not display_voice_assistant_status():
        return

    # Check if documents are loaded
    if not st.session_state.chunks:
        st.warning("⚠️ Please upload and process PDF files first")
        return

    # Check AI client availability
    from streamlit_app import get_active_ai_client
    ai_client = get_active_ai_client()
    if not ai_client:
        st.error("❌ No AI client initialized. Please select and initialize an AI provider in the sidebar.")
        return

    # Voice settings
    st.markdown("### 🔧 Voice Settings")
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

    st.divider()

    # Voice interaction area
    st.markdown("### 🎙️ Voice Interaction")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Calibrate microphone button
        if st.button("🎚️ Calibrate Microphone", help="Adjust for background noise"):
            with st.spinner("Calibrating microphone..."):
                if assistant.calibrate_microphone():
                    st.success("✅ Microphone calibrated!")
                else:
                    st.error("❌ Failed to calibrate microphone")

        # Main voice interaction button
        if st.button("🎤 Ask Question (Voice)", type="primary", help="Click and speak your question"):
            handle_voice_question(assistant, ai_client, tts_method, voice_option)

    # Display conversation history
    if assistant.conversation_history:
        st.markdown("### 📝 Voice Conversation History")

        for i, item in enumerate(reversed(assistant.conversation_history)):
            with st.expander(f"🎤 Voice Q&A {len(assistant.conversation_history) - i}"):
                st.markdown(f"**❓ Question:** {item['question']}")
                st.markdown(f"**🤖 Answer:** {item['answer']}")

                # Replay audio button
                if st.button(f"🔊 Replay Answer", key=f"replay_{len(assistant.conversation_history) - i}"):
                    replay_answer(item['answer'], tts_method, voice_option)


def handle_voice_question(assistant: VoiceAssistant, ai_client, tts_method: str, voice_option: str):
    """Handle a voice question interaction."""
    # Step 1: Listen for speech
    with st.spinner("🎤 Listening... Please speak your question"):
        question_text = assistant.listen_for_speech(timeout=10, phrase_time_limit=15)

    if not question_text:
        st.error("❌ Could not understand your question. Please try again.")
        return

    # Display transcribed question
    st.success(f"🎤 **You asked:** {question_text}")

    # Step 2: Process question with AI
    with st.spinner("🤖 Generating answer..."):
        try:
            # Import required functions
            from streamlit_app import query_ai_provider
            from embedding_retrieval import format_retrieved_chunks
            from utils import validate_question

            # Validate question
            validation = validate_question(question_text)
            if not validation["valid"]:
                st.error(validation["message"])
                return

            # Get conversation context
            context_history = assistant.get_conversation_context()

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

            # Add conversation context if available
            if context_history:
                context = f"Previous conversation:\n{context_history}\n\nDocument context:\n{context}"

            # Query AI provider
            response = query_ai_provider(
                ai_client,
                context,
                validation["cleaned_question"]
            )

            if not response["success"]:
                st.error(f"❌ Error generating answer: {response.get('error', 'Unknown error')}")
                return

            answer_text = response["answer"]

            # Display text answer
            st.markdown("### 🤖 Answer")
            st.markdown(answer_text)

            # Step 3: Convert to speech and play
            with st.spinner("🔊 Converting to speech..."):
                if tts_method == "OpenAI TTS (Requires API Key)":
                    # Use OpenAI TTS
                    audio_bytes = assistant.text_to_speech_openai(answer_text, voice_option)
                    if audio_bytes:
                        # Create audio player
                        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    else:
                        st.warning("⚠️ OpenAI TTS failed, falling back to browser TTS")
                        # Fallback to browser TTS
                        js_code = assistant.text_to_speech_browser(answer_text)
                        st.components.v1.html(js_code, height=0)
                else:
                    # Use browser TTS
                    js_code = assistant.text_to_speech_browser(answer_text)
                    st.components.v1.html(js_code, height=0)

            # Add to conversation history
            assistant.add_to_conversation_history(question_text, answer_text)

            # Log user action
            from utils import log_user_action
            log_user_action("voice_question_answered", {
                "question_length": len(question_text),
                "answer_length": len(answer_text),
                "tts_method": tts_method
            })

        except Exception as e:
            st.error(f"❌ Error processing voice question: {str(e)}")


def replay_answer(answer_text: str, tts_method: str, voice_option: str):
    """Replay an answer using TTS."""
    assistant = st.session_state.voice_assistant

    if tts_method == "OpenAI TTS (Requires API Key)":
        audio_bytes = assistant.text_to_speech_openai(answer_text, voice_option)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        else:
            # Fallback to browser TTS
            js_code = assistant.text_to_speech_browser(answer_text)
            st.components.v1.html(js_code, height=0)
    else:
        # Use browser TTS
        js_code = assistant.text_to_speech_browser(answer_text)
        st.components.v1.html(js_code, height=0)
