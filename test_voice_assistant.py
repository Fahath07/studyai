#!/usr/bin/env python3
"""
Test script for voice assistant functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from voice_assistant import VoiceAssistant, SPEECH_RECOGNITION_AVAILABLE, PYAUDIO_AVAILABLE, PYDUB_AVAILABLE

def test_voice_assistant_availability():
    """Test voice assistant availability and dependencies."""
    print("🧪 Testing Voice Assistant Availability")
    print("=" * 60)
    
    # Check dependencies
    print(f"📦 SpeechRecognition: {'✅ Available' if SPEECH_RECOGNITION_AVAILABLE else '❌ Missing'}")
    print(f"📦 PyAudio: {'✅ Available' if PYAUDIO_AVAILABLE else '❌ Missing'}")
    print(f"📦 Pydub: {'✅ Available' if PYDUB_AVAILABLE else '❌ Missing'}")
    
    # Initialize voice assistant
    assistant = VoiceAssistant()
    print(f"🎤 Voice Assistant: {'✅ Available' if assistant.is_available() else '❌ Unavailable'}")
    
    if not assistant.is_available():
        missing = assistant.get_missing_dependencies()
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("\n📋 Installation commands:")
        for dep in missing:
            if dep == "SpeechRecognition":
                print("   pip install SpeechRecognition")
            elif dep == "pyaudio":
                print("   pip install pyaudio")
            elif dep == "pydub":
                print("   pip install pydub")
    
    return assistant.is_available()


def test_text_to_speech():
    """Test text-to-speech functionality."""
    print("\n🧪 Testing Text-to-Speech")
    print("=" * 60)
    
    assistant = VoiceAssistant()
    test_text = "Hello! This is a test of the StudyMate voice assistant."
    
    # Test browser TTS
    print("🌐 Testing Browser TTS...")
    js_code = assistant.text_to_speech_browser(test_text)
    if js_code and "speechSynthesis" in js_code:
        print("✅ Browser TTS code generated successfully")
    else:
        print("❌ Browser TTS code generation failed")
    
    # Test OpenAI TTS (if API key available)
    print("\n🤖 Testing OpenAI TTS...")
    try:
        audio_bytes = assistant.text_to_speech_openai(test_text)
        if audio_bytes:
            print(f"✅ OpenAI TTS generated {len(audio_bytes)} bytes of audio")
        else:
            print("⚠️ OpenAI TTS failed (likely missing API key)")
    except Exception as e:
        print(f"⚠️ OpenAI TTS error: {e}")


def test_conversation_history():
    """Test conversation history functionality."""
    print("\n🧪 Testing Conversation History")
    print("=" * 60)
    
    assistant = VoiceAssistant()
    
    # Add test conversations
    test_conversations = [
        ("What is Python?", "Python is a high-level programming language known for its simplicity and readability."),
        ("How do you define variables?", "In Python, you define variables by simply assigning a value to a name."),
        ("What are data types?", "Python has several built-in data types including int, float, str, list, dict, and more.")
    ]
    
    for question, answer in test_conversations:
        assistant.add_to_conversation_history(question, answer)
    
    print(f"✅ Added {len(test_conversations)} conversations to history")
    print(f"📝 History length: {len(assistant.conversation_history)}")
    
    # Test context generation
    context = assistant.get_conversation_context()
    if context:
        print(f"✅ Generated context: {len(context)} characters")
        print(f"📄 Context preview: {context[:100]}...")
    else:
        print("❌ No context generated")


def test_microphone_calibration():
    """Test microphone calibration (if available)."""
    print("\n🧪 Testing Microphone Calibration")
    print("=" * 60)
    
    assistant = VoiceAssistant()
    
    if not assistant.is_available():
        print("⚠️ Voice assistant not available - skipping microphone test")
        return
    
    print("🎚️ Attempting microphone calibration...")
    try:
        success = assistant.calibrate_microphone()
        if success:
            print("✅ Microphone calibrated successfully")
        else:
            print("❌ Microphone calibration failed")
    except Exception as e:
        print(f"❌ Microphone calibration error: {e}")


def main():
    """Run all voice assistant tests."""
    print("🎤 StudyMate Voice Assistant Test Suite")
    print("=" * 60)
    
    # Test 1: Availability
    available = test_voice_assistant_availability()
    
    # Test 2: Text-to-Speech
    test_text_to_speech()
    
    # Test 3: Conversation History
    test_conversation_history()
    
    # Test 4: Microphone (if available)
    if available:
        test_microphone_calibration()
    
    print("\n" + "=" * 60)
    print("🎉 Voice Assistant Test Suite Completed!")
    
    if available:
        print("✅ Voice assistant is ready for use")
        print("\n🚀 Next steps:")
        print("   1. Run the main StudyMate application")
        print("   2. Select '🎤 Voice Assistant' mode")
        print("   3. Upload a PDF document")
        print("   4. Click 'Ask Question (Voice)' and speak")
    else:
        print("❌ Voice assistant requires additional setup")
        print("\n📋 Installation required:")
        print("   pip install SpeechRecognition pyaudio pydub")


if __name__ == "__main__":
    main()
