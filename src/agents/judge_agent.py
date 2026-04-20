"""
Judge agent
Provides final judgment and recommendations based on evaluation results
"""
from typing import Dict, Any, List
from datetime import datetime
from src.agents.base_agent import BaseLLMAgent
from src.models.complaint import (
    Complaint, MetricScore, EvaluationResult, 
    RiskLevel, RecommendationType, Metric
)
from src.utils.config_loader import ConfigLoader
from src.utils.scoring_engine import ScoringEngine


class JudgeAgent(BaseLLMAgent):
    """Agent responsible for final judgment and recommendations"""
    
    def __init__(
        self, 
        config_loader: ConfigLoader,
        scoring_engine: ScoringEngine,
        model_name: str = "gpt-4",
        provider: str = "auto"
    ):
        """
        Initialize judge agent
        
        Args:
            config_loader: Configuration loader instance
            scoring_engine: Scoring engine instance
            model_name: LLM model name
            provider: LLM provider ("openai", "ollama", or "auto")
        """
        super().__init__(model_name, provider=provider)
        self.config = config_loader
        self.scoring_engine = scoring_engine
    
    def execute(
        self,
        complaint: Complaint,
        metric_scores: List[MetricScore],
        metrics: List[Metric]
    ) -> EvaluationResult:
        """
        Generate final evaluation result
        
        Args:
            complaint: Complaint being evaluated
            metric_scores: Individual metric scores
            metrics: Metric configurations with weights
            
        Returns:
            Complete evaluation result
        """
        # Calculate aggregate scores
        aggregate_score, weighted_score = self.scoring_engine.calculate_aggregate_score(
            metric_scores, metrics
        )
        
        # Get LLM judgment
        llm_judgment = self._get_llm_judgment(
            complaint, metric_scores, metrics, weighted_score
        )
        
        # Create initial evaluation result
        evaluation_result = EvaluationResult(
            complaint_id=complaint.complaint_id,
            complaint_type=complaint.complaint_type,
            evaluation_timestamp=datetime.now(),
            metric_scores=metric_scores,
            aggregate_score=aggregate_score,
            weighted_score=llm_judgment.get('agreed_score', weighted_score),
            risk_level=RiskLevel.MEDIUM,  # Will be updated
            recommendation=RecommendationType.APPROVE,  # Will be updated
            reasoning=llm_judgment.get('overall_assessment', ''),
            strengths=llm_judgment.get('strengths', []),
            weaknesses=llm_judgment.get('weaknesses', []),
            confidence_score=0.85
        )
        
        # Evaluate business rules
        triggered_rules = self.scoring_engine.evaluate_business_rules(
            complaint, evaluation_result
        )
        evaluation_result.triggered_rules = triggered_rules
        
        # Calculate risk
        risk_score = self.scoring_engine.calculate_risk_score(complaint, evaluation_result)
        risk_level = self.scoring_engine.determine_risk_level(risk_score)
        evaluation_result.risk_level = risk_level
        
        # Determine recommendation
        recommendation = self.scoring_engine.determine_recommendation(
            complaint, evaluation_result, triggered_rules
        )
        evaluation_result.recommendation = recommendation
        
        # Determine if human review is required
        evaluation_result.requires_human_review = self.scoring_engine.requires_human_review(
            complaint, evaluation_result, triggered_rules
        )
        
        return evaluation_result
    
    def _get_llm_judgment(
        self,
        complaint: Complaint,
        metric_scores: List[MetricScore],
        metrics: List[Metric],
        calculated_score: float
    ) -> Dict[str, Any]:
        """
        Get LLM judgment on the evaluation
        
        Args:
            complaint: Complaint being evaluated
            metric_scores: Individual metric scores
            metrics: Metric configurations
            calculated_score: Calculated weighted score
            
        Returns:
            LLM judgment dictionary
        """
        # Get prompts
        system_prompt = self.config.get_prompt_template('aggregate_scorer', 'system_prompt')
        user_prompt_template = self.config.get_prompt_template('aggregate_scorer', 'user_prompt_template')
        
        # Format metric scores for prompt
        metric_scores_text = self._format_metric_scores(metric_scores)
        metric_weights_text = self._format_metric_weights(metrics)
        
        # Format user prompt
        user_prompt = self.format_prompt(
            user_prompt_template,
            complaint_type=complaint.complaint_type,
            complaint_summary=complaint.summary,
            metric_scores=metric_scores_text,
            metric_weights=metric_weights_text,
            calculated_score=calculated_score
        )
        
        # Call LLM
        response = self.call_llm(system_prompt, user_prompt, temperature=0.6)
        
        return response
    
    def _format_metric_scores(self, metric_scores: List[MetricScore]) -> str:
        """Format metric scores for prompt"""
        lines = []
        for ms in metric_scores:
            lines.append(f"- {ms.metric_name}: {ms.score}/5")
            if ms.reasoning:
                lines.append(f"  Reasoning: {ms.reasoning}")
        return "\n".join(lines)
    
    def _format_metric_weights(self, metrics: List[Metric]) -> str:
        """Format metric weights for prompt"""
        lines = []
        for m in metrics:
            lines.append(f"- {m.name}: {m.weight * 100:.1f}%")
        return "\n".join(lines)
