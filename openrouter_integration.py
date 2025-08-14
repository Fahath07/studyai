"""
OpenRouter Integration for DeepSeek and other models
Provides access to DeepSeek through OpenRouter's unified API
"""

import os
import logging
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OpenRouterResponse:
    """Response from OpenRouter API."""
    content: str
    model: str
    usage: Dict[str, Any]
    success: bool
    error: Optional[str] = None

class OpenRouterClient:
    """Client for OpenRouter API to access DeepSeek and other models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek/deepseek-chat"):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key
            model: Model to use (default: deepseek/deepseek-chat)
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://studymate-ai.local",  # Optional: for analytics
            "X-Title": "StudyMate AI"  # Optional: for analytics
        }
        
        logger.info(f"OpenRouter client initialized with model: {self.model}")
    
    def is_available(self) -> bool:
        """Check if OpenRouter API is available."""
        return bool(self.api_key and self.api_key.startswith('sk-or-'))
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "provider": "OpenRouter",
            "model_name": self.model,
            "base_url": self.base_url,
            "available": self.is_available()
        }
    
    def generate_response(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> OpenRouterResponse:
        """
        Generate a response using OpenRouter API.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            OpenRouterResponse: Response from the API
        """
        if not self.is_available():
            return OpenRouterResponse(
                content="",
                model="",
                usage={},
                success=False,
                error="OpenRouter API key not configured"
            )
        
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            logger.info(f"Making OpenRouter API request to {self.model}")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response content
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})
                
                logger.info(f"OpenRouter API request successful")
                return OpenRouterResponse(
                    content=content,
                    model=self.model,
                    usage=usage,
                    success=True
                )
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                
                # Provide specific error messages for common issues
                if response.status_code == 401:
                    error_msg = "Invalid OpenRouter API key. Please check your API key."
                elif response.status_code == 429:
                    error_msg = "Rate limit exceeded. Please wait a moment and try again."
                elif response.status_code == 402:
                    error_msg = "Insufficient credits. Please check your OpenRouter account balance."
                
                logger.error(f"OpenRouter API error: {error_msg}")
                
                return OpenRouterResponse(
                    content="",
                    model="",
                    usage={},
                    success=False,
                    error=error_msg
                )
                
        except requests.exceptions.Timeout:
            error_msg = "Request timeout. Please try again."
            logger.error(f"OpenRouter API timeout: {error_msg}")
            return OpenRouterResponse(
                content="",
                model="",
                usage={},
                success=False,
                error=error_msg
            )
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(f"OpenRouter API network error: {error_msg}")
            return OpenRouterResponse(
                content="",
                model="",
                usage={},
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"OpenRouter API unexpected error: {error_msg}")
            return OpenRouterResponse(
                content="",
                model="",
                usage={},
                success=False,
                error=error_msg
            )
    
    def test_connection(self) -> bool:
        """Test the API connection."""
        if not self.is_available():
            return False
            
        try:
            response = self.generate_response("Hello", max_tokens=10)
            return response.success
        except Exception as e:
            logger.error(f"OpenRouter connection test failed: {e}")
            return False

def initialize_openrouter_client() -> Optional[OpenRouterClient]:
    """
    Initialize OpenRouter client for DeepSeek access.
    
    Returns:
        OpenRouterClient or None if initialization fails
    """
    try:
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            logger.warning("OpenRouter API key not configured")
            return None
        
        client = OpenRouterClient(api_key)
        
        if not client.is_available():
            logger.warning("OpenRouter client not available")
            return None
        
        # Test the connection
        if client.test_connection():
            logger.info("OpenRouter client initialized and tested successfully")
            return client
        else:
            logger.error("OpenRouter client test failed")
            return None
            
    except Exception as e:
        logger.error(f"Failed to initialize OpenRouter client: {e}")
        return None

def query_openrouter_deepseek(client: OpenRouterClient, context: str, question: str) -> str:
    """
    Query DeepSeek through OpenRouter for Q&A.
    
    Args:
        client: OpenRouter client
        context: Document context
        question: User question
        
    Returns:
        str: AI response
    """
    try:
        prompt = f"""Based on the following context, please answer the question accurately and concisely.

Context:
{context}

Question: {question}

Please provide a clear, informative answer based on the context provided."""

        response = client.generate_response(prompt, max_tokens=500, temperature=0.7)
        
        if response.success:
            return response.content
        else:
            logger.error(f"OpenRouter query failed: {response.error}")
            return f"I apologize, but I encountered an error: {response.error}"
            
    except Exception as e:
        logger.error(f"Error querying OpenRouter: {e}")
        return "I apologize, but I encountered an error while processing your question."

def generate_mcqs_with_openrouter(client: OpenRouterClient, context: str, num_questions: int = 5, 
                                 difficulty: str = "medium", topic_focus: str = "") -> str:
    """
    Generate MCQs using OpenRouter DeepSeek.
    
    Args:
        client: OpenRouter client
        context: Document context
        num_questions: Number of questions
        difficulty: Difficulty level
        topic_focus: Topic focus
        
    Returns:
        str: Generated MCQs in JSON format
    """
    try:
        topic_instruction = f"\n- Focus specifically on: {topic_focus}" if topic_focus else ""
        
        prompt = f"""You are an expert educator creating multiple choice questions for exam preparation. Generate {num_questions} high-quality questions based SPECIFICALLY on the provided document content.

CRITICAL REQUIREMENTS:
- Questions MUST be directly based on the specific content provided below
- DO NOT use generic questions that could apply to any document
- Extract specific facts, concepts, examples, and details from the document
- Reference specific names, dates, processes, or examples mentioned in the content
- Difficulty level: {difficulty}
- Each question should have exactly 4 options (A, B, C, D)
- Only ONE option should be correct
- Include a brief explanation referencing the document content{topic_instruction}

RESPONSE FORMAT (JSON):
{{
    "questions": [
        {{
            "question": "Question text here?",
            "options": [
                {{"text": "Option A", "is_correct": false}},
                {{"text": "Option B", "is_correct": true}},
                {{"text": "Option C", "is_correct": false}},
                {{"text": "Option D", "is_correct": false}}
            ],
            "difficulty": "{difficulty}",
            "topic": "Topic from document",
            "explanation": "Brief explanation referencing the document content"
        }}
    ]
}}

Document Content:
{context}

Generate {num_questions} questions in the exact JSON format shown above:"""

        response = client.generate_response(prompt, max_tokens=1500, temperature=0.3)
        
        if response.success:
            return response.content
        else:
            logger.error(f"OpenRouter MCQ generation failed: {response.error}")
            return ""
            
    except Exception as e:
        logger.error(f"Error generating MCQs with OpenRouter: {e}")
        return ""
