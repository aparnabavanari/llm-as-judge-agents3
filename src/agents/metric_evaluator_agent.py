"""
Metric evaluation agent
Evaluates complaint summaries against specific metrics
"""
from typing import List, Dict, Any
from src.agents.base_agent import BaseLLMAgent
from src.models.complaint import Complaint, Metric, MetricScore
from src.utils.config_loader import ConfigLoader


class MetricEvaluatorAgent(BaseLLMAgent):
    """Agent responsible for evaluating summaries against specific metrics"""
    
    def __init__(self, config_loader: ConfigLoader, model_name: str = "gpt-4", provider: str = "auto"):
        """
        Initialize metric evaluator agent
        
        Args:
            config_loader: Configuration loader instance
            model_name: LLM model name
            provider: LLM provider ("openai", "ollama", or "auto")
        """
        super().__init__(model_name, provider=provider)
        self.config = config_loader
    
    def execute(
        self, 
        complaint: Complaint, 
        metrics: List[Metric]
    ) -> List[MetricScore]:
        """
        Evaluate complaint summary against all metrics
        
        Args:
            complaint: Complaint with summary to evaluate
            metrics: List of metrics to evaluate against
            
        Returns:
            List of metric scores
        """
        metric_scores = []
        
        for metric in metrics:
            score = self.evaluate_single_metric(complaint, metric)
            metric_scores.append(score)
        
        return metric_scores
    
    def evaluate_single_metric(
        self, 
        complaint: Complaint, 
        metric: Metric
    ) -> MetricScore:
        """
        Evaluate complaint summary against a single metric
        
        Args:
            complaint: Complaint to evaluate
            metric: Metric to evaluate against
            
        Returns:
            MetricScore result
        """
        # Get prompts from configuration
        system_prompt = self.config.get_prompt_template('metric_evaluator', 'system_prompt')
        user_prompt_template = self.config.get_prompt_template('metric_evaluator', 'user_prompt_template')
        
        # Format user prompt
        user_prompt = self.format_prompt(
            user_prompt_template,
            complaint_summary=complaint.summary,
            original_complaint=complaint.original_complaint,
            metric_id=metric.metric_id,
            metric_name=metric.name,
            metric_description=metric.description,
            metric_scale=metric.scale
        )
        
        # Call LLM
        response = self.call_llm(system_prompt, user_prompt, temperature=0.5)
        
        # Parse response
        metric_score = self._parse_metric_score_response(response, metric)
        
        return metric_score
    
    def _parse_metric_score_response(
        self, 
        response: Dict[str, Any], 
        metric: Metric
    ) -> MetricScore:
        """
        Parse LLM response into MetricScore
        
        Args:
            response: LLM response
            metric: Metric being evaluated
            
        Returns:
            MetricScore object
        """
        # In production, parse actual response
        # For demonstration, return mock scores
        return MetricScore(
            metric_id=metric.metric_id,
            metric_name=metric.name,
            score=response.get('score', 3.5),
            max_score=5.0,
            reasoning=response.get('reasoning', f'Evaluation of {metric.name}'),
            evidence=response.get('evidence', []),
            suggestions=response.get('suggestions', [])
        )
    
    def batch_evaluate_metrics(
        self,
        complaints: List[Complaint],
        metrics: List[Metric]
    ) -> Dict[str, List[MetricScore]]:
        """
        Evaluate multiple complaints in batch
        
        Args:
            complaints: List of complaints to evaluate
            metrics: List of metrics to evaluate against
            
        Returns:
            Dictionary mapping complaint_id to list of metric scores
        """
        results = {}
        
        for complaint in complaints:
            results[complaint.complaint_id] = self.execute(complaint, metrics)
        
        return results
