"""
Scoring engine for calculating aggregate scores and evaluating business rules
"""
from typing import List, Dict, Any, Tuple
from src.models.complaint import (
    MetricScore, EvaluationResult, Metric, RiskLevel, 
    RecommendationType, Complaint
)
from src.utils.config_loader import ConfigLoader
from datetime import datetime


class ScoringEngine:
    """Handles scoring calculations and business rule evaluations"""
    
    def __init__(self, config_loader: ConfigLoader = None):
        """
        Initialize scoring engine
        
        Args:
            config_loader: Configuration loader instance
        """
        self.config = config_loader or ConfigLoader()
    
    def calculate_aggregate_score(
        self, 
        metric_scores: List[MetricScore], 
        metrics: List[Metric]
    ) -> Tuple[float, float]:
        """
        Calculate aggregate scores from individual metric scores
        
        Args:
            metric_scores: List of metric scores
            metrics: List of metric configurations with weights
            
        Returns:
            Tuple of (unweighted_average, weighted_average)
        """
        if not metric_scores:
            return 0.0, 0.0
        
        # Create metric weight map
        weight_map = {m.metric_id: m.weight for m in metrics}
        
        # Calculate unweighted average
        total_score = sum(ms.score for ms in metric_scores)
        unweighted_avg = total_score / len(metric_scores)
        
        # Calculate weighted average
        weighted_sum = sum(
            ms.normalized_score() * weight_map.get(ms.metric_id, 0)
            for ms in metric_scores
        )
        
        # Weighted score is already normalized (0-1), convert to 0-5 scale
        weighted_avg = weighted_sum * 5.0
        
        return unweighted_avg, weighted_avg
    
    def evaluate_business_rules(
        self,
        complaint: Complaint,
        evaluation_result: EvaluationResult
    ) -> List[str]:
        """
        Evaluate business rules and return triggered rule IDs
        
        Args:
            complaint: Complaint being evaluated
            evaluation_result: Evaluation result
            
        Returns:
            List of triggered rule IDs
        """
        triggered_rules = []
        business_rules = self.config.get_business_rules().get('business_rules', [])
        complaint_config = self.config.get_complaint_type_config(complaint.complaint_type)
        
        if not complaint_config:
            return triggered_rules
        
        risk_level = complaint_config.get('risk_level', 'low')
        escalation_threshold = complaint_config.get('escalation_threshold', 0.8)
        
        for rule in business_rules:
            rule_id = rule.get('rule_id')
            condition = rule.get('condition', '')
            
            # Evaluate condition (simplified evaluation)
            if self._evaluate_condition(
                condition,
                complaint,
                evaluation_result,
                risk_level,
                escalation_threshold
            ):
                triggered_rules.append(rule_id)
        
        return triggered_rules
    
    def _evaluate_condition(
        self,
        condition: str,
        complaint: Complaint,
        evaluation_result: EvaluationResult,
        risk_level: str,
        escalation_threshold: float
    ) -> bool:
        """
        Evaluate a business rule condition
        
        Args:
            condition: Condition string
            complaint: Complaint data
            evaluation_result: Evaluation result
            risk_level: Risk level from config
            escalation_threshold: Escalation threshold
            
        Returns:
            True if condition is met, False otherwise
        """
        # Create evaluation context
        context = {
            'risk_level': risk_level,
            'complaint_type': complaint.complaint_type,
            'aggregate_score': evaluation_result.weighted_score / 5.0,  # Normalize to 0-1
            'escalation_threshold': escalation_threshold,
            'confidence_score': evaluation_result.confidence_score,
            'detected_types_count': 1 + len(complaint.secondary_types)
        }
        
        try:
            # Simple condition evaluation
            # BR001: High Risk Auto-Escalation
            if "risk_level in ['critical', 'high']" in condition:
                if context['risk_level'] in ['critical', 'high'] and \
                   context['aggregate_score'] >= context['escalation_threshold']:
                    return True
            
            # BR002: Fraud Pattern Detection
            if "complaint_type == 'fraud'" in condition:
                if context['complaint_type'] == 'fraud' and \
                   context['confidence_score'] >= 0.8:
                    return True
            
            # BR003: Regulatory Compliance Alert
            if "complaint_type == 'regulatory_compliance'" in condition:
                if context['complaint_type'] == 'regulatory_compliance':
                    return True
            
            # BR004: Quality Threshold Check
            if "aggregate_score < 0.4" in condition:
                if context['aggregate_score'] < 0.4:
                    return True
            
            # BR005: Multiple Complaint Types
            if "detected_types_count > 1" in condition:
                if context['detected_types_count'] > 1:
                    return True
            
        except Exception as e:
            print(f"Error evaluating condition '{condition}': {e}")
            return False
        
        return False
    
    def determine_recommendation(
        self,
        complaint: Complaint,
        evaluation_result: EvaluationResult,
        triggered_rules: List[str]
    ) -> RecommendationType:
        """
        Determine recommendation based on evaluation and triggered rules
        
        Args:
            complaint: Complaint being evaluated
            evaluation_result: Evaluation result
            triggered_rules: List of triggered rule IDs
            
        Returns:
            Recommendation type
        """
        complaint_config = self.config.get_complaint_type_config(complaint.complaint_type)
        
        # Check for escalation rules
        if 'BR001' in triggered_rules or 'BR002' in triggered_rules or 'BR003' in triggered_rules:
            return RecommendationType.ESCALATE
        
        # Check for quality issues
        if 'BR004' in triggered_rules:
            return RecommendationType.REVISE
        
        # Check weighted score
        normalized_score = evaluation_result.weighted_score / 5.0
        
        if normalized_score >= 0.8:
            return RecommendationType.APPROVE
        elif normalized_score >= 0.6:
            # Check if human review is required
            if complaint_config and complaint_config.get('requires_human_review', False):
                return RecommendationType.ESCALATE
            return RecommendationType.APPROVE
        elif normalized_score >= 0.4:
            return RecommendationType.REVISE
        else:
            return RecommendationType.REJECT
    
    def calculate_risk_score(
        self,
        complaint: Complaint,
        evaluation_result: EvaluationResult
    ) -> float:
        """
        Calculate overall risk score
        
        Args:
            complaint: Complaint data
            evaluation_result: Evaluation result
            
        Returns:
            Risk score (0-1)
        """
        complaint_config = self.config.get_complaint_type_config(complaint.complaint_type)
        
        if not complaint_config:
            return 0.0
        
        # Base risk from complaint type
        risk_level = complaint_config.get('risk_level', 'low')
        risk_level_config = self.config.get_risk_level_config(risk_level)
        
        base_risk = risk_level_config.get('score_threshold', 0.3) if risk_level_config else 0.3
        
        # Adjust based on evaluation quality (poor quality increases risk)
        quality_factor = 1.0 - (evaluation_result.weighted_score / 5.0)
        
        # Adjust for previous complaints
        history_factor = min(complaint.previous_complaint_count * 0.05, 0.2)
        
        # Calculate final risk score
        risk_score = min(base_risk + (quality_factor * 0.3) + history_factor, 1.0)
        
        return risk_score
    
    def determine_risk_level(self, risk_score: float) -> RiskLevel:
        """
        Determine risk level from risk score
        
        Args:
            risk_score: Risk score (0-1)
            
        Returns:
            Risk level enum
        """
        if risk_score >= 0.9:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.7:
            return RiskLevel.HIGH
        elif risk_score >= 0.5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def requires_human_review(
        self,
        complaint: Complaint,
        evaluation_result: EvaluationResult,
        triggered_rules: List[str]
    ) -> bool:
        """
        Determine if human review is required
        
        Args:
            complaint: Complaint data
            evaluation_result: Evaluation result
            triggered_rules: Triggered rule IDs
            
        Returns:
            True if human review is required
        """
        complaint_config = self.config.get_complaint_type_config(complaint.complaint_type)
        
        # Check complaint type configuration
        if complaint_config and complaint_config.get('requires_human_review', False):
            return True
        
        # Check risk level
        if evaluation_result.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            return True
        
        # Check triggered rules
        escalation_rules = ['BR001', 'BR002', 'BR003']
        if any(rule in triggered_rules for rule in escalation_rules):
            return True
        
        # Check confidence score
        confidence_threshold = self.config.get_threshold('human_review_confidence_threshold') or 0.6
        if evaluation_result.confidence_score < confidence_threshold:
            return True
        
        return False
    
    def calculate_priority_level(
        self,
        complaint: Complaint,
        evaluation_result: EvaluationResult
    ) -> int:
        """
        Calculate priority level for human review (1-5, 1 being highest)
        
        Args:
            complaint: Complaint data
            evaluation_result: Evaluation result
            
        Returns:
            Priority level (1-5)
        """
        complaint_config = self.config.get_complaint_type_config(complaint.complaint_type)
        
        if not complaint_config:
            return 3
        
        base_priority = complaint_config.get('priority', 3)
        
        # Adjust for risk level
        if evaluation_result.risk_level == RiskLevel.CRITICAL:
            base_priority = 1
        elif evaluation_result.risk_level == RiskLevel.HIGH:
            base_priority = min(base_priority, 2)
        
        # Adjust for high-value customers
        if complaint.is_high_value_customer:
            base_priority = max(1, base_priority - 1)
        
        return base_priority
