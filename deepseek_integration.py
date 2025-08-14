#!/usr/bin/env python3
"""
DeepSeek API Integration Module
Provides free, high-quality AI responses using DeepSeek's API
"""

import os
import logging
import requests
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DeepSeekResponse:
    """Response from DeepSeek API."""
    content: str
    model: str
    usage: Dict[str, int]
    success: bool = True
    error: Optional[str] = None

class DeepSeekClient:
    """Client for interacting with DeepSeek API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize DeepSeek client.
        
        Args:
            api_key: DeepSeek API key
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"  # Default model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
        
    def is_available(self) -> bool:
        """Check if DeepSeek API is available."""
        return bool(self.api_key)
    
    def test_connection(self) -> bool:
        """Test the API connection."""
        if not self.is_available():
            return False

        try:
            response = self.generate_response("Hello", max_tokens=10)
            if not response.success and "Insufficient Balance" in str(response.error):
                logger.warning("DeepSeek account needs verification or balance top-up")
                return False
            return response.success
        except Exception as e:
            logger.error(f"DeepSeek connection test failed: {e}")
            return False
    
    def generate_response(
        self, 
        prompt: str, 
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_message: Optional[str] = None
    ) -> DeepSeekResponse:
        """
        Generate a response using DeepSeek API.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0.0-1.0)
            system_message: Optional system message
            
        Returns:
            DeepSeekResponse object
        """
        if not self.is_available():
            return DeepSeekResponse(
                content="",
                model="",
                usage={},
                success=False,
                error="DeepSeek API key not configured"
            )
        
        try:
            # Prepare messages
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                
                logger.info(f"DeepSeek response generated successfully: {len(content)} characters")
                
                return DeepSeekResponse(
                    content=content,
                    model=data.get("model", self.model),
                    usage=usage,
                    success=True
                )
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"

                # Provide specific error messages for common issues
                if response.status_code == 402:
                    if "Insufficient Balance" in response.text:
                        error_msg = "Account verification required. Please verify your DeepSeek account at https://platform.deepseek.com/"
                elif response.status_code == 401:
                    error_msg = "Invalid API key. Please check your DeepSeek API key."
                elif response.status_code == 429:
                    error_msg = "Rate limit exceeded. Please wait a moment and try again."

                logger.error(f"DeepSeek API error: {error_msg}")

                return DeepSeekResponse(
                    content="",
                    model="",
                    usage={},
                    success=False,
                    error=error_msg
                )
                
        except requests.exceptions.Timeout:
            error_msg = "API request timed out"
            logger.error(f"DeepSeek API timeout: {error_msg}")
            return DeepSeekResponse(
                content="",
                model="",
                usage={},
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"DeepSeek API error: {error_msg}")
            return DeepSeekResponse(
                content="",
                model="",
                usage={},
                success=False,
                error=error_msg
            )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "provider": "DeepSeek",
            "model_name": self.model,
            "description": "DeepSeek's advanced language model",
            "max_tokens": 4096,
            "supports_system_messages": True,
            "cost": "Free"
        }

def initialize_deepseek_client(api_key: Optional[str] = None):
    """
    Initialize DeepSeek client with OpenRouter fallback.

    Args:
        api_key: Optional API key override

    Returns:
        OpenRouter client or DeepSeek client or None if initialization fails
    """
    try:
        # First try OpenRouter (more reliable)
        try:
            from openrouter_integration import initialize_openrouter_client
            openrouter_client = initialize_openrouter_client()
            if openrouter_client:
                logger.info("Using OpenRouter for DeepSeek access")
                return openrouter_client
        except ImportError:
            logger.warning("OpenRouter integration not available")

        # Fallback to direct DeepSeek API
        client = DeepSeekClient(api_key)

        if not client.is_available():
            logger.warning("DeepSeek API key not configured")
            return None

        # Test the connection
        if client.test_connection():
            logger.info("DeepSeek client initialized successfully")
            return client
        else:
            logger.error("DeepSeek client test failed")
            return None

    except Exception as e:
        logger.error(f"Failed to initialize DeepSeek client: {e}")
        return None

def query_deepseek(
    client,  # Can be DeepSeekClient or OpenRouterClient
    prompt: str,
    context: str = "",
    max_tokens: int = 500,
    temperature: float = 0.7
) -> Optional[str]:
    """
    Query DeepSeek with context for Q&A.

    Args:
        client: DeepSeek or OpenRouter client instance
        prompt: User question
        context: Document context
        max_tokens: Maximum response tokens
        temperature: Response creativity

    Returns:
        Generated response or None if failed
    """
    try:
        # Check if it's an OpenRouter client
        if hasattr(client, 'base_url') and 'openrouter' in str(client.base_url):
            from openrouter_integration import query_openrouter_deepseek
            return query_openrouter_deepseek(client, context, prompt)

        # Handle direct DeepSeek client
        # Create system message with context
        system_message = f"""You are an intelligent academic assistant. Use the following context to answer questions accurately and helpfully.

Context:
{context}

Instructions:
- Answer based on the provided context
- If the context doesn't contain relevant information, say so clearly
- Provide detailed, educational responses
- Use examples when helpful
- Be concise but comprehensive"""

        response = client.generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            system_message=system_message
        )

        if response.success:
            return response.content
        else:
            logger.error(f"DeepSeek query failed: {response.error}")
            return None

    except Exception as e:
        logger.error(f"Error querying DeepSeek: {e}")
        return None

def generate_mcqs_with_deepseek(
    client,  # Can be DeepSeekClient or OpenRouterClient
    context: str,
    num_questions: int = 5,
    difficulty: str = "medium",
    topic_focus: str = ""
) -> Optional[str]:
    """
    Generate multiple choice questions using DeepSeek.
    
    Args:
        client: DeepSeek client instance
        context: Document context
        num_questions: Number of questions to generate
        difficulty: Question difficulty level
        topic_focus: Optional topic focus
        
    Returns:
        Generated MCQs in JSON format or None if failed
    """
    try:
        # Check if it's an OpenRouter client
        if hasattr(client, 'base_url') and 'openrouter' in str(client.base_url):
            from openrouter_integration import generate_mcqs_with_openrouter
            return generate_mcqs_with_openrouter(client, context, num_questions, difficulty, topic_focus)

        # Handle direct DeepSeek client
        # Create focused prompt for MCQ generation
        system_message = f"""You are an expert quiz generator. Create {num_questions} multiple choice questions based on the provided context.

Requirements:
- Difficulty level: {difficulty}
- {f"Focus on: {topic_focus}" if topic_focus else "Cover various topics from the content"}
- Each question should have 4 options (A, B, C, D)
- Only one correct answer per question
- Include brief explanations for correct answers
- Questions should test understanding, not just memorization

Format your response as valid JSON with this structure:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": {{
        "A": "Option A text",
        "B": "Option B text", 
        "C": "Option C text",
        "D": "Option D text"
      }},
      "correct_answer": "A",
      "explanation": "Brief explanation of why this is correct",
      "difficulty": "{difficulty}",
      "topic": "Main topic of the question"
    }}
  ]
}}"""

        prompt = f"""Based on this content, generate {num_questions} multiple choice questions:

{context}

{f"Focus specifically on: {topic_focus}" if topic_focus else ""}

Generate questions that test comprehension and application of the concepts."""

        response = client.generate_response(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.3,  # Lower temperature for more consistent formatting
            system_message=system_message
        )
        
        if response.success:
            return response.content
        else:
            logger.error(f"DeepSeek MCQ generation failed: {response.error}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating MCQs with DeepSeek: {e}")
        return None
