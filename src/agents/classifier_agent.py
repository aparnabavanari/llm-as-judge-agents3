"""
Complaint classifier agent
Classifies complaints into appropriate types
"""
from typing import Dict, Any
from src.agents.base_agent import BaseLLMAgent
from src.models.complaint import Complaint, ComplaintClassification
from src.utils.config_loader import ConfigLoader


class ComplaintClassifierAgent(BaseLLMAgent):
    """Agent responsible for classifying complaint summaries"""
    
    def __init__(self, config_loader: ConfigLoader, model_name: str = "gpt-4", provider: str = "auto"):
        """
        Initialize complaint classifier agent
        
        Args:
            config_loader: Configuration loader instance
            model_name: LLM model name
            provider: LLM provider ("openai", "ollama", or "auto")
        """
        super().__init__(model_name, provider=provider)
        self.config = config_loader
    
    def execute(self, complaint: Complaint) -> ComplaintClassification:
        """
        Classify a complaint summary
        
        Args:
            complaint: Complaint to classify
            
        Returns:
            ComplaintClassification result
        """
        # Get prompts from configuration
        system_prompt = self.config.get_prompt_template('complaint_classifier', 'system_prompt')
        user_prompt_template = self.config.get_prompt_template('complaint_classifier', 'user_prompt_template')
        
        # Format user prompt
        user_prompt = self.format_prompt(
            user_prompt_template,
            complaint_summary=complaint.summary,
            customer_id=complaint.customer_id,
            submission_date=complaint.submission_date.strftime('%Y-%m-%d'),
            has_previous_complaints=complaint.has_previous_complaints
        )
        
        # Call LLM
        response = self.call_llm(system_prompt, user_prompt, temperature=0.3)
        
        # Parse response
        classification = self._parse_classification_response(response, complaint.complaint_id)
        print(f"  Classified as: {classification.primary_type} (Confidence: {classification.confidence:.2f})")
        
        return classification
    
    def _parse_classification_response(
        self, 
        response: Dict[str, Any], 
        complaint_id: str
    ) -> ComplaintClassification:
        """
        Parse LLM response into ComplaintClassification
        
        Args:
            response: LLM response
            complaint_id: Complaint identifier
            
        Returns:
            ComplaintClassification object
        """
        # In production, parse actual response
        # For demonstration, return default classification
        return ComplaintClassification(
            complaint_id=complaint_id,
            primary_type=response.get('primary_type', 'customer_service'),
            secondary_types=response.get('secondary_types', []),
            confidence=response.get('confidence', 0.85),
            reasoning=response.get('reasoning', 'Classification based on complaint content')
        )
