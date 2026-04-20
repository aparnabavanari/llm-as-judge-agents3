"""
Base agent class for LLM-based agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try importing ollama (optional dependency)
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class BaseLLMAgent(ABC):
    """Base class for all LLM-based agents"""
    
    def __init__(
        self, 
        model_name: str = "gpt-4-turbo", 
        api_key: Optional[str] = None,
        provider: str = "auto"
    ):
        """
        Initialize base agent
        
        Args:
            model_name: Name of the LLM model to use
            api_key: API key for LLM service (defaults to environment variable)
            provider: LLM provider ("openai", "ollama", or "auto")
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        # Auto-detect provider if set to "auto"
        if provider == "auto":
            if model_name in ["gemma3:1b", "gemma2:2b", "mistral", "llama2", "llama3"]:
                provider = "ollama"
            else:
                provider = "openai"
        
        self.provider = provider.lower()
        
        # Initialize appropriate client
        if self.provider == "ollama":
            if not OLLAMA_AVAILABLE:
                raise ImportError(
                    "Ollama package not found. Install with: pip install ollama"
                )
            print(f"[Ollama] Initializing with model: {self.model_name}")
            self.client = None
        elif self.provider == "openai":
            if not self.api_key:
                raise ValueError(
                    "OpenAI API key not found. Please set OPENAI_API_KEY in .env file or environment."
                )
            # Initialize OpenAI client
            self.client = OpenAI(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'openai', 'ollama', or 'auto'")
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the agent's main task"""
        pass
    
    def call_llm(
        self, 
        system_prompt: str, 
        user_prompt: str,
        temperature: float = 0.5,
        response_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Call LLM with prompts (supports OpenAI and Ollama)
        
        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM
            temperature: Temperature for response generation
            response_format: Expected response format ("json" or "text")
            
        Returns:
            Parsed response from LLM (as dictionary if JSON, or wrapped in dict if text)
        """
        if self.provider == "ollama":
            return self._call_ollama(system_prompt, user_prompt, temperature, response_format)
        else:
            return self._call_openai(system_prompt, user_prompt, temperature, response_format)
    
    def _call_ollama(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.5,
        response_format: str = "json"
    ) -> Dict[str, Any]:
        """Call local Ollama model"""
        try:
            # For JSON mode, ensure instructions are clear
            if response_format == "json":
                if "json" not in system_prompt.lower():
                    system_prompt = system_prompt + "\n\nIMPORTANT: You must respond with valid JSON format only. Do not include any text before or after the JSON."
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Call Ollama API
            print(f"[Ollama API Call] Model: {self.model_name}, Temp: {temperature}")
            
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": temperature,
                }
            )
            
            # Extract content
            content = response['message']['content']
            
            # Parse JSON if expected
            if response_format == "json":
                return self.parse_json_response(content)
            else:
                return {"response": content}
                
        except Exception as e:
            print(f"Error calling Ollama API: {e}")
            print(f"Make sure Ollama is running and model '{self.model_name}' is available.")
            print(f"Run: ollama pull {self.model_name}")
            raise
    
    def _call_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.5,
        response_format: str = "json"
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            # For JSON mode, ensure "json" appears in the messages (OpenAI requirement)
            if response_format == "json":
                if "json" not in system_prompt.lower() and "json" not in user_prompt.lower():
                    system_prompt = system_prompt + "\n\nYou must respond with valid JSON format."
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Call OpenAI API
            print(f"[OpenAI API Call] Model: {self.model_name}, Temp: {temperature}")
            
            if response_format == "json":
                # Use JSON mode for structured outputs
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
            else:
                # Regular text response
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature
                )
            
            # Extract content
            content = response.choices[0].message.content
            
            # Parse JSON if expected
            if response_format == "json":
                return self.parse_json_response(content)
            else:
                return {"response": content}
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            raise
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM
        
        Args:
            response: Response string from LLM
            
        Returns:
            Parsed JSON dictionary
        """
        try:
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Response: {response}")
            return {}
    
    def format_prompt(self, template: str, **kwargs) -> str:
        """
        Format prompt template with variables
        
        Args:
            template: Prompt template string
            **kwargs: Variables to substitute in template
            
        Returns:
            Formatted prompt string
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"Missing template variable: {e}")
            return template
