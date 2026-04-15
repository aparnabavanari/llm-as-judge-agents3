"""
Human review agent
Generates human review requests for high-risk complaints
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import uuid
from src.agents.base_agent import BaseLLMAgent
from src.models.complaint import Complaint, EvaluationResult, HumanReviewRequest
from src.utils.config_loader import ConfigLoader
from src.utils.scoring_engine import ScoringEngine


class HumanReviewAgent(BaseLLMAgent):
    """Agent responsible for generating human review requests"""
    
    def __init__(
        self,
        config_loader: ConfigLoader,
        scoring_engine: ScoringEngine,
        model_name: str = "gpt-4"
    ):
        """
        Initialize human review agent
        
        Args:
            config_loader: Configuration loader instance
            scoring_engine: Scoring engine instance
            model_name: LLM model name
        """
        super().__init__(model_name)
        self.config = config_loader
        self.scoring_engine = scoring_engine
    
    def execute(
        self,
        complaint: Complaint,
        evaluation_result: EvaluationResult
    ) -> HumanReviewRequest:
        """
        Generate human review request
        
        Args:
            complaint: Complaint requiring review
            evaluation_result: Evaluation result
            
        Returns:
            HumanReviewRequest object
        """
        # Get LLM-generated review request content
        review_content = self._generate_review_content(complaint, evaluation_result)
        
        # Calculate priority
        priority = self.scoring_engine.calculate_priority_level(complaint, evaluation_result)
        
        # Calculate deadline based on priority
        deadline = self._calculate_review_deadline(priority)
        
        # Create review request
        review_request = HumanReviewRequest(
            request_id=str(uuid.uuid4()),
            complaint_id=complaint.complaint_id,
            complaint=complaint,
            evaluation_result=evaluation_result,
            priority_level=priority,
            executive_summary=review_content.get('executive_summary', ''),
            key_concerns=review_content.get('key_concerns', []),
            review_questions=review_content.get('review_questions', []),
            recommended_actions=review_content.get('recommended_actions', []),
            created_at=datetime.now(),
            review_deadline=deadline,
            status='pending'
        )
        
        return review_request
    
    def _generate_review_content(
        self,
        complaint: Complaint,
        evaluation_result: EvaluationResult
    ) -> Dict[str, Any]:
        """
        Generate review request content using LLM
        
        Args:
            complaint: Complaint data
            evaluation_result: Evaluation result
            
        Returns:
            Dictionary with review request content
        """
        # Get prompts
        system_prompt = self.config.get_prompt_template('human_review_request', 'system_prompt')
        user_prompt_template = self.config.get_prompt_template('human_review_request', 'user_prompt_template')
        
        # Format evaluation results
        eval_results_text = self._format_evaluation_results(evaluation_result)
        triggered_rules_text = self._format_triggered_rules(evaluation_result.triggered_rules)
        
        # Format user prompt
        user_prompt = self.format_prompt(
            user_prompt_template,
            complaint_summary=complaint.summary,
            complaint_type=complaint.complaint_type,
            risk_level=evaluation_result.risk_level.value,
            aggregate_score=evaluation_result.weighted_score,
            evaluation_results=eval_results_text,
            triggered_rules=triggered_rules_text
        )
        
        # Call LLM
        response = self.call_llm(system_prompt, user_prompt, temperature=0.7)
        
        # Parse response - in production, this would parse actual LLM response
        return {
            'executive_summary': response.get(
                'executive_summary',
                f'High-risk {complaint.complaint_type} complaint requiring expert review'
            ),
            'key_concerns': response.get(
                'key_concerns',
                ['Risk level assessment', 'Regulatory implications', 'Customer impact']
            ),
            'review_questions': response.get(
                'review_questions',
                ['Is the risk assessment accurate?', 'Are there immediate actions required?']
            ),
            'recommended_actions': response.get(
                'recommended_actions',
                ['Review complaint details', 'Verify facts', 'Determine resolution path']
            )
        }
    
    def _format_evaluation_results(self, evaluation_result: EvaluationResult) -> str:
        """Format evaluation results for prompt"""
        lines = [
            f"Aggregate Score: {evaluation_result.aggregate_score:.2f}/5",
            f"Weighted Score: {evaluation_result.weighted_score:.2f}/5",
            f"Risk Level: {evaluation_result.risk_level.value}",
            f"Recommendation: {evaluation_result.recommendation.value}",
            "",
            "Strengths:",
        ]
        for strength in evaluation_result.strengths:
            lines.append(f"  - {strength}")
        
        lines.append("")
        lines.append("Weaknesses:")
        for weakness in evaluation_result.weaknesses:
            lines.append(f"  - {weakness}")
        
        return "\n".join(lines)
    
    def _format_triggered_rules(self, triggered_rules: List[str]) -> str:
        """Format triggered rules for prompt"""
        if not triggered_rules:
            return "No business rules triggered"
        
        lines = []
        for rule_id in triggered_rules:
            rule = self.config.get_business_rule(rule_id)
            if rule:
                lines.append(f"- {rule_id}: {rule.get('name', 'Unknown')} - {rule.get('action', '')}")
            else:
                lines.append(f"- {rule_id}")
        
        return "\n".join(lines)
    
    def _calculate_review_deadline(self, priority: int) -> datetime:
        """
        Calculate review deadline based on priority
        
        Args:
            priority: Priority level (1-5)
            
        Returns:
            Deadline datetime
        """
        # Priority 1: 2 hours
        # Priority 2: 4 hours
        # Priority 3: 1 day
        # Priority 4: 2 days
        # Priority 5: 3 days
        
        hours_map = {
            1: 2,
            2: 4,
            3: 24,
            4: 48,
            5: 72
        }
        
        hours = hours_map.get(priority, 24)
        return datetime.now() + timedelta(hours=hours)
    
    def format_review_request_for_display(
        self,
        review_request: HumanReviewRequest
    ) -> str:
        """
        Format review request for human-readable display
        
        Args:
            review_request: Review request to format
            
        Returns:
            Formatted string
        """
        lines = [
            "=" * 80,
            "HUMAN REVIEW REQUEST",
            "=" * 80,
            f"Request ID: {review_request.request_id}",
            f"Complaint ID: {review_request.complaint_id}",
            f"Priority: {review_request.priority_level} (1=Highest, 5=Lowest)",
            f"Created: {review_request.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Deadline: {review_request.review_deadline.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Status: {review_request.status}",
            "",
            "EXECUTIVE SUMMARY:",
            "-" * 80,
            review_request.executive_summary,
            "",
            "KEY CONCERNS:",
            "-" * 80,
        ]
        
        for concern in review_request.key_concerns:
            lines.append(f"  • {concern}")
        
        lines.extend([
            "",
            "REVIEW QUESTIONS:",
            "-" * 80,
        ])
        
        for question in review_request.review_questions:
            lines.append(f"  ? {question}")
        
        lines.extend([
            "",
            "RECOMMENDED ACTIONS:",
            "-" * 80,
        ])
        
        for action in review_request.recommended_actions:
            lines.append(f"  ✓ {action}")
        
        lines.extend([
            "",
            "EVALUATION SUMMARY:",
            "-" * 80,
            f"Risk Level: {review_request.evaluation_result.risk_level.value.upper()}",
            f"Aggregate Score: {review_request.evaluation_result.weighted_score:.2f}/5",
            f"Recommendation: {review_request.evaluation_result.recommendation.value.upper()}",
            "=" * 80,
        ])
        
        return "\n".join(lines)
