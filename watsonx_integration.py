"""
IBM Watsonx Integration Module for StudyMate
Handles LLM API connection and query processing
"""

import os
from typing import Dict, Any, Optional
import logging
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import Credentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WatsonxClient:
    """
    Client for interacting with IBM Watsonx.ai LLM services.
    """
    
    def __init__(self, 
                 api_key: str = None,
                 project_id: str = None,
                 url: str = None,
                 model_id: str = "mistralai/mixtral-8x7b-instruct-v01"):
        """
        Initialize Watsonx client.
        
        Args:
            api_key: IBM Cloud API key
            project_id: Watsonx project ID
            url: Watsonx instance URL
            model_id: Model identifier to use
        """
        self.api_key = api_key or os.getenv("IBM_API_KEY")
        self.project_id = project_id or os.getenv("IBM_PROJECT_ID")
        self.url = url or os.getenv("IBM_URL")
        self.model_id = model_id or os.getenv("MODEL_ID", "mistralai/mixtral-8x7b-instruct-v01")
        
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Watsonx model client."""
        try:
            if not all([self.api_key, self.project_id, self.url]):
                raise ValueError("Missing required credentials: API_KEY, PROJECT_ID, or URL")
            
            # Set up credentials
            credentials = Credentials(
                url=self.url,
                api_key=self.api_key
            )
            
            # Initialize model
            self.model = Model(
                model_id=self.model_id,
                credentials=credentials,
                project_id=self.project_id
            )
            
            logger.info(f"Successfully initialized Watsonx client with model: {self.model_id}")
            
        except Exception as e:
            logger.error(f"Error initializing Watsonx client: {str(e)}")
            raise
    
    def generate_response(self, 
                         prompt: str,
                         max_new_tokens: int = 300,
                         temperature: float = 0.5,
                         decoding_method: str = "greedy") -> Optional[str]:
        """
        Generate response from Watsonx LLM.
        
        Args:
            prompt: Input prompt for the model
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            decoding_method: Decoding method ("greedy" or "sample")
            
        Returns:
            str: Generated response or None if error
        """
        if not self.model:
            logger.error("Watsonx model not initialized")
            return None
        
        if not prompt.strip():
            logger.warning("Empty prompt provided")
            return None
        
        try:
            # Set generation parameters
            generate_params = {
                GenParams.MAX_NEW_TOKENS: max_new_tokens,
                GenParams.TEMPERATURE: temperature,
                GenParams.DECODING_METHOD: decoding_method
            }
            
            # Generate response
            response = self.model.generate_text(
                prompt=prompt,
                params=generate_params
            )
            
            if response:
                logger.info(f"Successfully generated response ({len(response)} characters)")
                return response.strip()
            else:
                logger.warning("Empty response from model")
                return None
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test the connection to Watsonx.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            test_prompt = "Hello, this is a test."
            response = self.generate_response(
                prompt=test_prompt,
                max_new_tokens=10,
                temperature=0.1
            )
            
            if response:
                logger.info("Watsonx connection test successful")
                return True
            else:
                logger.error("Watsonx connection test failed - no response")
                return False
                
        except Exception as e:
            logger.error(f"Watsonx connection test failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration.
        
        Returns:
            Dict: Model configuration information
        """
        return {
            "model_id": self.model_id,
            "url": self.url,
            "project_id": self.project_id,
            "api_key_configured": bool(self.api_key),
            "model_initialized": self.model is not None
        }


def create_academic_prompt(context: str, question: str) -> str:
    """
    Create a structured prompt for academic Q&A.

    Args:
        context: Retrieved context from documents
        question: User's question

    Returns:
        str: Formatted prompt for the LLM
    """
    prompt = f"""You are an academic assistant helping students understand their course materials. Answer the following question strictly based on the provided context from academic documents.

IMPORTANT: Structure your response as follows:
1. **MAIN ANSWER**: Start with the direct, concise answer to the question
2. **ADDITIONAL DETAILS**: Then provide any related information, examples, or context

Guidelines:
- Use only the information provided in the context
- If the answer is not found in the context, clearly state "The answer is not found in the provided documents"
- Always put the main answer FIRST, then supporting details
- Be clear and concise, suitable for students
- DO NOT mention "Context", "Section", or document references in your response
- Present information naturally without citing sources
- Avoid using outside knowledge not present in the documents

Context:
{context}

Question:
{question}

Answer:"""

    return prompt


def query_watsonx(client: WatsonxClient, 
                  context: str, 
                  question: str,
                  max_tokens: int = 300,
                  temperature: float = 0.5) -> Dict[str, Any]:
    """
    Query Watsonx with context and question, return structured response.
    
    Args:
        client: Initialized WatsonxClient
        context: Retrieved document context
        question: User's question
        max_tokens: Maximum tokens for response
        temperature: Sampling temperature
        
    Returns:
        Dict: Response with answer, success status, and metadata
    """
    result = {
        "answer": None,
        "success": False,
        "error": None,
        "prompt_length": 0,
        "response_length": 0
    }
    
    try:
        # Create prompt
        prompt = create_academic_prompt(context, question)
        result["prompt_length"] = len(prompt)
        
        # Check prompt length (rough token estimation: 1 token ≈ 4 characters)
        estimated_tokens = len(prompt) // 4
        if estimated_tokens > 3000:  # Leave room for response
            logger.warning(f"Prompt may be too long: ~{estimated_tokens} tokens")
        
        # Generate response
        response = client.generate_response(
            prompt=prompt,
            max_new_tokens=max_tokens,
            temperature=temperature
        )
        
        if response:
            result["answer"] = response
            result["success"] = True
            result["response_length"] = len(response)
            logger.info("Successfully generated academic response")
        else:
            result["error"] = "No response generated from model"
            logger.error("Failed to generate response")
            
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Error in query_watsonx: {str(e)}")
    
    return result


def initialize_watsonx_client() -> Optional[WatsonxClient]:
    """
    Initialize Watsonx client with environment variables.

    Returns:
        WatsonxClient: Initialized client or None if failed
    """
    try:
        # Check if credentials are properly configured
        api_key = os.getenv("IBM_API_KEY")
        project_id = os.getenv("IBM_PROJECT_ID")
        url = os.getenv("IBM_URL")

        # Check for placeholder values
        if (not api_key or api_key == "your_api_key_here" or
            not project_id or project_id == "your_project_id_here" or
            not url or url == "your_instance_url_here"):
            logger.warning("IBM Watsonx credentials not configured - using demo mode")
            return DemoWatsonxClient()

        client = WatsonxClient()

        # Test connection
        if client.test_connection():
            logger.info("Watsonx client initialized and tested successfully")
            return client
        else:
            logger.error("Watsonx client initialization failed connection test - using demo mode")
            return DemoWatsonxClient()

    except Exception as e:
        logger.error(f"Failed to initialize Watsonx client: {str(e)} - using demo mode")
        return DemoWatsonxClient()


class DemoWatsonxClient:
    """
    Demo client that provides sample responses when IBM Watsonx is not available.
    """

    def __init__(self):
        self.model_id = "demo-mode"
        logger.info("Initialized demo Watsonx client")

    def generate_response(self,
                         prompt: str,
                         max_new_tokens: int = 300,
                         temperature: float = 0.5,
                         decoding_method: str = "greedy") -> Optional[str]:
        """
        Generate a demo response based on the prompt and context.

        Args:
            prompt: Input prompt for the model (includes context and question)
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            decoding_method: Decoding method ("greedy" or "sample")

        Returns:
            str: Demo response based on context
        """
        logger.info("Generating demo response based on context")

        # Extract context and question from prompt
        context = ""
        question = ""

        if "Context:" in prompt and "Question:" in prompt:
            # Split by Context: and Question: markers
            try:
                # Find the context section
                context_start = prompt.find("Context:")
                question_start = prompt.find("Question:")

                if context_start != -1 and question_start != -1 and question_start > context_start:
                    # Extract context (everything between "Context:" and "Question:")
                    context_section = prompt[context_start + len("Context:"):question_start].strip()
                    # Remove any guidelines or instructions from context
                    context_lines = context_section.split('\n')
                    context_lines = [line.strip() for line in context_lines if line.strip() and not line.startswith('-') and not line.startswith('Guidelines')]
                    context = '\n'.join(context_lines).strip()

                    # Extract question (everything after "Question:")
                    question_section = prompt[question_start + len("Question:"):].strip()
                    # Remove "Answer:" if present
                    if "Answer:" in question_section:
                        question = question_section.split("Answer:")[0].strip()
                    else:
                        question = question_section.strip()

            except Exception as e:
                logger.warning(f"Error parsing prompt: {e}")
                question = prompt.strip()
        else:
            question = prompt.strip()

        # If we have context from the PDFs, use it to generate a response
        if context and len(context.strip()) > 10:
            response = self._generate_context_based_response(question, context)
        else:
            # Fallback to generic responses
            response = self._generate_generic_response(question)

        # Add demo disclaimer
        response += "\n\n*Note: This is a demo response based on your uploaded documents. For full AI-powered answers, please configure IBM Watsonx credentials.*"

        return response

    def _generate_context_based_response(self, question: str, context: str) -> str:
        """Generate a response based on the provided context from PDFs."""

        # Extract key information from context
        context_words = context.lower().split()
        question_words = question.lower().split()

        # Find relevant sentences in context
        sentences = context.split('.')
        relevant_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            # Check if sentence contains question keywords
            sentence_lower = sentence.lower()
            relevance_score = 0

            for word in question_words:
                if len(word) > 3 and word in sentence_lower:
                    relevance_score += 1

            if relevance_score > 0:
                relevant_sentences.append((sentence, relevance_score))

        # Sort by relevance and take top sentences
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)

        if relevant_sentences:
            # Build response from most relevant sentences
            response_parts = []
            for sentence, score in relevant_sentences[:3]:  # Top 3 sentences
                if sentence not in response_parts:
                    response_parts.append(sentence.strip())

            if response_parts:
                response = "Based on the uploaded documents:\n\n"
                response += ". ".join(response_parts)
                if not response.endswith('.'):
                    response += "."
                return response

        # If no relevant sentences found, provide a summary
        if len(context) > 100:
            # Take first few sentences as summary
            summary_sentences = sentences[:2]
            response = "Based on the uploaded documents, here's what I found:\n\n"
            response += ". ".join([s.strip() for s in summary_sentences if len(s.strip()) > 10])
            if not response.endswith('.'):
                response += "."
            return response

        return "I found relevant content in your documents, but I need more specific information to provide a detailed answer."

    def _generate_generic_response(self, question: str) -> str:
        """Generate a generic response when no context is available."""

        question_lower = question.lower()

        # Common academic question patterns
        if any(word in question_lower for word in ["what is", "define", "definition"]):
            return f"I can help define concepts, but I need access to your uploaded documents to provide specific definitions. Please ensure your PDFs have been processed successfully."

        elif any(word in question_lower for word in ["how", "explain", "describe"]):
            return f"I can explain concepts based on your uploaded documents. Please make sure your PDFs contain relevant information about your question."

        elif any(word in question_lower for word in ["why", "reason", "because"]):
            return f"I can help explain reasons and causes based on the content in your uploaded documents."

        elif any(word in question_lower for word in ["when", "time", "date"]):
            return f"I can help with temporal information if it's available in your uploaded documents."

        elif any(word in question_lower for word in ["where", "location", "place"]):
            return f"I can help with location-based information from your documents."

        elif any(word in question_lower for word in ["who", "person", "people"]):
            return f"I can help identify people or entities mentioned in your uploaded documents."

        else:
            return f"I can help answer questions about your uploaded documents. Please make sure your PDFs have been processed and contain relevant information about: {question}"

    def test_connection(self) -> bool:
        """Test connection (always returns True for demo)."""
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """Get demo model information."""
        return {
            "model_id": self.model_id,
            "url": "demo-mode",
            "project_id": "demo-mode",
            "api_key_configured": False,
            "model_initialized": True
        }


def format_error_response(error_msg: str) -> str:
    """
    Format error message for user display.
    
    Args:
        error_msg: Error message
        
    Returns:
        str: User-friendly error message
    """
    if "credentials" in error_msg.lower() or "api_key" in error_msg.lower():
        return "❌ **Authentication Error**: Please check your IBM Watsonx credentials in the .env file."
    elif "connection" in error_msg.lower() or "network" in error_msg.lower():
        return "❌ **Connection Error**: Unable to connect to IBM Watsonx. Please check your internet connection."
    elif "timeout" in error_msg.lower():
        return "❌ **Timeout Error**: The request took too long. Please try again with a shorter question."
    else:
        return f"❌ **Error**: {error_msg}"
