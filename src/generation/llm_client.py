"""
Generation Module
Handles LLM calls and response generation using OpenAI
"""

from typing import List, Dict, Any
import os
from openai import OpenAI
from src.utils import get_logger


logger = get_logger(__name__)


class LLMClient:
    """
    Wrapper for OpenAI API calls
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1500
    ):
        """
        Initialize the LLM client
        
        Args:
            api_key: OpenAI API key
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not provided and not found in environment")
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.logger = logger
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        self.logger.info(f"Initialized LLM client with model: {self.model}")
    
    def generate(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Generate response from LLM
        
        Args:
            system_prompt: System prompt to set context
            user_message: User message/query
            temperature: Optional override for temperature
            max_tokens: Optional override for max tokens
        
        Returns:
            Generated response text
        """
        try:
            temp = temperature if temperature is not None else self.temperature
            tokens = max_tokens if max_tokens is not None else self.max_tokens
            
            self.logger.info(f"Generating response with model: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temp,
                max_tokens=tokens
            )
            
            generated_text = response.choices[0].message.content
            
            self.logger.info("Response generated successfully")
            return generated_text
        
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise
    
    def generate_with_context(
        self,
        system_prompt: str,
        context: str,
        user_query: str
    ) -> str:
        """
        Generate response using context (RAG pattern)
        
        Args:
            system_prompt: System prompt
            context: Retrieved context/documents
            user_query: User query
        
        Returns:
            Generated response
        """
        # Combine context and query
        combined_message = f"Context Information:\n{context}\n\nQuestion: {user_query}"
        
        return self.generate(
            system_prompt=system_prompt,
            user_message=combined_message
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            Dictionary with model information
        """
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }


class PromptBuilder:
    """
    Builds prompts for different query types
    """
    
    def __init__(self, prompts_config: Dict[str, str]):
        """
        Initialize prompt builder
        
        Args:
            prompts_config: Dictionary of prompt templates
        """
        self.prompts_config = prompts_config
        self.logger = logger
    
    def build_system_prompt(self) -> str:
        """
        Get system prompt
        
        Returns:
            System prompt string
        """
        return self.prompts_config.get(
            "system_prompt",
            "You are a helpful assistant for shrimp farming operations."
        )
    
    def build_query_prompt(
        self,
        query: str,
        context: str,
        prompt_type: str = "general"
    ) -> str:
        """
        Build prompt for a specific query
        
        Args:
            query: User query
            context: Retrieved context
            prompt_type: Type of prompt to use
        
        Returns:
            Formatted prompt string
        """
        prompt_template = self.prompts_config.get(
            f"{prompt_type}_prompt",
            self.prompts_config.get("general_prompt", "")
        )
        
        if not prompt_template:
            self.logger.warning(f"No prompt template found for type: {prompt_type}")
            prompt_template = "Based on the following context, answer the question:\n{context}\n\nQuestion: {query}"
        
        # Format template with context and query
        formatted_prompt = prompt_template.format(context=context, query=query)
        
        return formatted_prompt
    
    def detect_query_type(self, query: str) -> str:
        """
        Detect the type of query to determine which prompt to use
        
        Args:
            query: User query
        
        Returns:
            Query type string
        """
        query_lower = query.lower()
        
        # Map keywords to query types
        keyword_mapping = {
            "survival": "survival_analysis",
            "feed": "feed_conversion",
            "fcr": "feed_conversion",
            "biomass": "biomass",
            "stocking": "biomass",
            "performance": "pond_performance",
            "pond": "pond_performance",
        }
        
        for keyword, query_type in keyword_mapping.items():
            if keyword in query_lower:
                return query_type
        
        return "general"
