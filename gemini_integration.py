"""
Google Gemini Integration for StudyMate AI
Provides integration with Google's Gemini AI models
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI library not installed. Install with: pip install google-generativeai")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GeminiConfig:
    """Configuration for Gemini client."""
    api_key: str
    model: str = "gemini-1.5-flash"  # Default to Gemini 1.5 Flash for speed and efficiency
    max_tokens: int = 500
    temperature: float = 0.7


class GeminiClient:
    """Google Gemini client for AI integration."""
    
    def __init__(self, config: GeminiConfig):
        """
        Initialize Gemini client.
        
        Args:
            config: Gemini configuration
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI library not available. Install with: pip install google-generativeai")
        
        self.config = config
        self.model = None
        self.model_name = config.model
        
        try:
            # Configure Gemini API
            genai.configure(api_key=config.api_key)
            
            # Initialize the model
            generation_config = {
                "temperature": config.temperature,
                "max_output_tokens": config.max_tokens,
            }
            
            self.model = genai.GenerativeModel(
                model_name=config.model,
                generation_config=generation_config
            )
            
            # Test the connection
            self._test_connection()
            logger.info(f"Gemini client initialized successfully with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            raise
    
    def _test_connection(self):
        """Test the Gemini connection with quota-aware error handling."""
        try:
            # Make a simple test call
            response = self.model.generate_content("Hello")
            logger.info("Gemini connection test successful")
        except Exception as e:
            error_str = str(e)
            if "quota" in error_str.lower() or "429" in error_str:
                logger.warning(f"Gemini quota exceeded: {error_str}")
                # Don't raise for quota errors - client can still be used later
                return
            else:
                logger.error(f"Gemini connection test failed: {error_str}")
                raise
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate response using Google Gemini.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
            
        Returns:
            Dict containing the response and metadata
        """
        try:
            # Override config with any provided kwargs
            max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
            temperature = kwargs.get('temperature', self.config.temperature)
            
            # Update generation config if different from default
            if max_tokens != self.config.max_tokens or temperature != self.config.temperature:
                generation_config = {
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
                
                model = genai.GenerativeModel(
                    model_name=self.config.model,
                    generation_config=generation_config
                )
            else:
                model = self.model
            
            # Generate content
            response = model.generate_content(prompt)
            
            # Extract response text
            response_text = response.text if response.text else "No response generated"
            
            return {
                "success": True,
                "response": response_text,
                "model": self.config.model,
                "usage": {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0) if hasattr(response, 'usage_metadata') else 0
                },
                "finish_reason": getattr(response.candidates[0], 'finish_reason', 'STOP') if response.candidates else 'UNKNOWN'
            }
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "Sorry, I encountered an error while processing your request."
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "provider": "Google Gemini",
            "model_name": self.model_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "api_configured": bool(self.config.api_key),
            "model_initialized": self.model is not None
        }


def initialize_gemini_client() -> Optional[GeminiClient]:
    """
    Initialize Gemini client from environment variables.
    
    Returns:
        GeminiClient instance or None if initialization fails
    """
    if not GEMINI_AVAILABLE:
        logger.warning("Google Generative AI library not available")
        return None
    
    try:
        # Get configuration from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            return None
        
        model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', '500'))
        temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.7'))
        
        config = GeminiConfig(
            api_key=api_key,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return GeminiClient(config)
        
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {str(e)}")
        return None


def create_academic_prompt_gemini(context: str, question: str) -> str:
    """
    Create a structured prompt for academic Q&A optimized for Gemini models.
    
    Args:
        context: Retrieved context from documents
        question: User's question
        
    Returns:
        str: Formatted prompt for Gemini
    """
    prompt = f"""You are an expert academic assistant helping students understand their course materials. Answer the following question based strictly on the provided context from academic documents.

RESPONSE STRUCTURE:
1. **MAIN ANSWER**: Start with the direct, concise answer to the question
2. **ADDITIONAL DETAILS**: Then provide any related information, examples, or context

GUIDELINES:
- Use only the information provided in the context
- If the answer is not found in the context, clearly state "The answer is not found in the provided documents"
- Always put the main answer FIRST, then supporting details
- Be clear, concise, and suitable for students
- DO NOT mention "Context", "Section", or document references in your response
- Present information naturally without citing sources
- Avoid using outside knowledge not present in the documents

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""
    
    return prompt


def query_gemini(client: GeminiClient, 
                context: str, 
                question: str,
                max_tokens: int = 500,
                temperature: float = 0.7) -> Dict[str, Any]:
    """
    Query Gemini with context and question, return structured response.
    
    Args:
        client: Gemini client instance
        context: Retrieved context from documents
        question: User's question
        max_tokens: Maximum tokens for response
        temperature: Temperature for response generation
        
    Returns:
        Dict containing the response and metadata
    """
    if not client:
        return {
            "success": False,
            "error": "Gemini client not initialized",
            "response": "Gemini service is not available."
        }
    
    try:
        # Create academic prompt
        prompt = create_academic_prompt_gemini(context, question)
        
        # Generate response
        result = client.generate_response(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error querying Gemini: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "response": "Sorry, I encountered an error while processing your request."
        }
