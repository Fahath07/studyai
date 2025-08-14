"""
OpenAI Integration for StudyMate AI
Provides integration with OpenAI's ChatGPT models (GPT-4, GPT-3.5-turbo)
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not installed. Install with: pip install openai")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OpenAIConfig:
    """Configuration for OpenAI client."""
    api_key: str
    model: str = "gpt-3.5-turbo"  # Default to GPT-3.5-turbo for cost efficiency
    max_tokens: int = 500
    temperature: float = 0.7
    organization: Optional[str] = None


class OpenAIClient:
    """OpenAI client for ChatGPT integration."""
    
    def __init__(self, config: OpenAIConfig):
        """
        Initialize OpenAI client.
        
        Args:
            config: OpenAI configuration
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        self.config = config
        self.client = None
        self.model_name = config.model
        
        try:
            # Initialize OpenAI client
            self.client = OpenAI(
                api_key=config.api_key,
                organization=config.organization
            )
            
            # Test the connection
            self._test_connection()
            logger.info(f"OpenAI client initialized successfully with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise
    
    def _test_connection(self):
        """Test the OpenAI connection with quota-aware error handling."""
        try:
            # Make a simple test call
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            logger.info("OpenAI connection test successful")
        except Exception as e:
            error_str = str(e)
            if "quota" in error_str.lower() or "429" in error_str:
                logger.warning(f"OpenAI quota exceeded: {error_str}")
                # Don't raise for quota errors - client can still be used later
                return
            else:
                logger.error(f"OpenAI connection test failed: {error_str}")
                raise
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate response using OpenAI ChatGPT.
        
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
            
            # Create chat completion
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful academic assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract response text
            response_text = response.choices[0].message.content
            
            return {
                "success": True,
                "response": response_text,
                "model": self.config.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "Sorry, I encountered an error while processing your request."
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "provider": "OpenAI",
            "model_name": self.model_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "api_configured": bool(self.config.api_key),
            "client_initialized": self.client is not None
        }


def initialize_openai_client() -> Optional[OpenAIClient]:
    """
    Initialize OpenAI client from environment variables.
    
    Returns:
        OpenAIClient instance or None if initialization fails
    """
    if not OPENAI_AVAILABLE:
        logger.warning("OpenAI library not available")
        return None
    
    try:
        # Get configuration from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            return None
        
        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '500'))
        temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
        organization = os.getenv('OPENAI_ORGANIZATION')
        
        config = OpenAIConfig(
            api_key=api_key,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            organization=organization
        )
        
        return OpenAIClient(config)
        
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        return None


def create_academic_prompt_openai(context: str, question: str) -> str:
    """
    Create a structured prompt for academic Q&A optimized for OpenAI models.

    Args:
        context: Retrieved context from documents
        question: User's question

    Returns:
        str: Formatted prompt for OpenAI
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


def query_openai(client: OpenAIClient, 
                context: str, 
                question: str,
                max_tokens: int = 500,
                temperature: float = 0.7) -> Dict[str, Any]:
    """
    Query OpenAI with context and question, return structured response.
    
    Args:
        client: OpenAI client instance
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
            "error": "OpenAI client not initialized",
            "response": "OpenAI service is not available."
        }
    
    try:
        # Create academic prompt
        prompt = create_academic_prompt_openai(context, question)
        
        # Generate response
        result = client.generate_response(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error querying OpenAI: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "response": "Sorry, I encountered an error while processing your request."
        }
