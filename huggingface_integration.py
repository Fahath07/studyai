"""
Hugging Face Integration for StudyMate
Free alternative to IBM Watsonx using Hugging Face models
"""

import os
import logging
from typing import Optional, Dict, Any
import requests
import json
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceClient:
    """
    Hugging Face client for text generation using local or API models.
    """
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium", use_api: bool = False):
        """
        Initialize Hugging Face client.
        
        Args:
            model_name: Name of the Hugging Face model to use
            use_api: Whether to use Hugging Face API (requires token) or local model
        """
        self.model_name = model_name
        self.use_api = use_api
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
        if use_api and not self.api_token:
            logger.warning("Hugging Face API token not found, falling back to local model")
            self.use_api = False
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the model based on configuration."""
        try:
            if self.use_api:
                self._initialize_api()
            else:
                self._initialize_local_model()
                
            logger.info(f"Hugging Face client initialized with {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face model: {e}")
            # Fallback to a smaller model
            self._initialize_fallback_model()
    
    def _initialize_api(self):
        """Initialize API-based model."""
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        logger.info("Using Hugging Face API")
    
    def _initialize_local_model(self):
        """Initialize local model."""
        try:
            # Use a lightweight model for better performance
            model_options = [
                "microsoft/DialoGPT-small",  # Lightweight conversational model
                "distilgpt2",                # Lightweight GPT-2 variant
                "gpt2"                       # Standard GPT-2
            ]
            
            for model_name in model_options:
                try:
                    logger.info(f"Trying to load {model_name}...")
                    
                    # Check if CUDA is available
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                    logger.info(f"Using device: {device}")
                    
                    # Load model and tokenizer
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                        device_map="auto" if device == "cuda" else None
                    )
                    
                    # Add padding token if not present
                    if self.tokenizer.pad_token is None:
                        self.tokenizer.pad_token = self.tokenizer.eos_token
                    
                    # Create text generation pipeline
                    self.pipeline = pipeline(
                        "text-generation",
                        model=self.model,
                        tokenizer=self.tokenizer,
                        device=0 if device == "cuda" else -1,
                        torch_dtype=torch.float16 if device == "cuda" else torch.float32
                    )
                    
                    self.model_name = model_name
                    logger.info(f"Successfully loaded {model_name}")
                    break
                    
                except Exception as e:
                    logger.warning(f"Failed to load {model_name}: {e}")
                    continue
            
            if self.pipeline is None:
                raise Exception("Failed to load any model")
                
        except Exception as e:
            logger.error(f"Local model initialization failed: {e}")
            raise
    
    def _initialize_fallback_model(self):
        """Initialize a simple fallback model."""
        try:
            logger.info("Initializing fallback model...")
            self.pipeline = pipeline("text-generation", model="distilgpt2")
            self.model_name = "distilgpt2"
            logger.info("Fallback model initialized")
        except Exception as e:
            logger.error(f"Fallback model failed: {e}")
            self.pipeline = None
    
    def generate_response(self, 
                         prompt: str,
                         max_new_tokens: int = 300,
                         temperature: float = 0.7,
                         **kwargs) -> Optional[str]:
        """
        Generate response using Hugging Face model.
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated response or None if failed
        """
        try:
            if self.use_api:
                return self._generate_api_response(prompt, max_new_tokens, temperature)
            else:
                return self._generate_local_response(prompt, max_new_tokens, temperature)
                
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return None
    
    def _generate_api_response(self, prompt: str, max_new_tokens: int, temperature: float) -> Optional[str]:
        """Generate response using Hugging Face API."""
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            
            return None
            
        except Exception as e:
            logger.error(f"API response generation failed: {e}")
            return None
    
    def _generate_local_response(self, prompt: str, max_new_tokens: int, temperature: float) -> Optional[str]:
        """Generate response using local model."""
        try:
            if not self.pipeline:
                return None
            
            # Truncate prompt if too long
            max_prompt_length = 512
            if len(prompt) > max_prompt_length:
                prompt = prompt[-max_prompt_length:]
            
            # Generate response
            outputs = self.pipeline(
                prompt,
                max_new_tokens=min(max_new_tokens, 200),  # Limit for performance
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                return_full_text=False,
                clean_up_tokenization_spaces=True
            )
            
            if outputs and len(outputs) > 0:
                generated_text = outputs[0]["generated_text"].strip()
                
                # Clean up the response
                generated_text = self._clean_response(generated_text)
                
                return generated_text
            
            return None
            
        except Exception as e:
            logger.error(f"Local response generation failed: {e}")
            return None
    
    def _clean_response(self, text: str) -> str:
        """Clean and format the generated response."""
        # Remove repetitive patterns
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and line not in cleaned_lines[-3:]:  # Avoid recent repetitions
                cleaned_lines.append(line)
        
        # Join and limit length
        cleaned_text = ' '.join(cleaned_lines)
        
        # Ensure it ends properly
        if cleaned_text and not cleaned_text.endswith(('.', '!', '?')):
            # Find last complete sentence
            for punct in ['.', '!', '?']:
                last_punct = cleaned_text.rfind(punct)
                if last_punct > len(cleaned_text) * 0.7:  # If punctuation is in last 30%
                    cleaned_text = cleaned_text[:last_punct + 1]
                    break
        
        return cleaned_text
    
    def test_connection(self) -> bool:
        """Test if the model is working."""
        try:
            test_response = self.generate_response("Hello, how are you?", max_new_tokens=10)
            return test_response is not None and len(test_response) > 0
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "model_name": self.model_name,
            "use_api": self.use_api,
            "api_token_configured": bool(self.api_token),
            "model_loaded": self.pipeline is not None,
            "device": "cuda" if torch.cuda.is_available() else "cpu"
        }


def initialize_huggingface_client() -> Optional[HuggingFaceClient]:
    """
    Initialize Hugging Face client.
    
    Returns:
        HuggingFaceClient or None if failed
    """
    try:
        # Check if API token is available
        api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        use_api = bool(api_token)
        
        if use_api:
            logger.info("Using Hugging Face API")
            client = HuggingFaceClient(
                model_name="microsoft/DialoGPT-medium",
                use_api=True
            )
        else:
            logger.info("Using local Hugging Face model")
            client = HuggingFaceClient(
                model_name="microsoft/DialoGPT-small",
                use_api=False
            )
        
        # Test connection
        if client.test_connection():
            logger.info("Hugging Face client initialized successfully")
            return client
        else:
            logger.error("Hugging Face client test failed")
            return None
            
    except Exception as e:
        logger.error(f"Failed to initialize Hugging Face client: {e}")
        return None


def create_academic_prompt_hf(context: str, question: str) -> str:
    """
    Create a prompt optimized for Hugging Face models.
    
    Args:
        context: Retrieved context from documents
        question: User's question
        
    Returns:
        Formatted prompt
    """
    prompt = f"""Based on the following academic content, please answer the question clearly and concisely. Do not mention "Context", "Section", or document references in your response.

Content: {context[:1000]}...

Question: {question}

Answer:"""
    
    return prompt
