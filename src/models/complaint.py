"""
Data models for the LLM Judge Agent system
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class RiskLevel(Enum):
    """Risk level enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationType(Enum):
    """Evaluation recommendation types"""
    APPROVE = "approve"
    REVISE = "revise"
    ESCALATE = "escalate"
    REJECT = "reject"


@dataclass
class Complaint:
    """Represents a banking complaint with its summary"""
    complaint_id: str
    customer_id: str
    original_complaint: str
    summary: str
    submission_date: datetime
    complaint_type: Optional[str] = None
    secondary_types: List[str] = field(default_factory=list)
    has_previous_complaints: bool = False
    previous_complaint_count: int = 0
    is_high_value_customer: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert complaint to dictionary"""
        return {
            'complaint_id': self.complaint_id,
            'customer_id': self.customer_id,
            'original_complaint': self.original_complaint,
            'summary': self.summary,
            'submission_date': self.submission_date.isoformat(),
            'complaint_type': self.complaint_type,
            'secondary_types': self.secondary_types,
            'has_previous_complaints': self.has_previous_complaints,
            'previous_complaint_count': self.previous_complaint_count,
            'is_high_value_customer': self.is_high_value_customer,
            'metadata': self.metadata
        }


@dataclass
class Metric:
    """Represents an evaluation metric"""
    metric_id: str
    name: str
    description: str
    weight: float
    scale: str
    
    def validate_weight(self) -> bool:
        """Validate metric weight is between 0 and 1"""
        return 0 <= self.weight <= 1


@dataclass
class MetricScore:
    """Represents a score for a specific metric"""
    metric_id: str
    metric_name: str
    score: float
    max_score: float = 5.0
    reasoning: str = ""
    evidence: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def normalized_score(self) -> float:
        """Return normalized score (0-1)"""
        return self.score / self.max_score if self.max_score > 0 else 0


@dataclass
class EvaluationResult:
    """Complete evaluation result for a complaint summary"""
    complaint_id: str
    complaint_type: str
    evaluation_timestamp: datetime
    metric_scores: List[MetricScore]
    aggregate_score: float
    weighted_score: float
    risk_level: RiskLevel
    recommendation: RecommendationType
    reasoning: str
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    requires_human_review: bool = False
    triggered_rules: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evaluation result to dictionary"""
        return {
            'complaint_id': self.complaint_id,
            'complaint_type': self.complaint_type,
            'evaluation_timestamp': self.evaluation_timestamp.isoformat(),
            'metric_scores': [
                {
                    'metric_id': ms.metric_id,
                    'metric_name': ms.metric_name,
                    'score': ms.score,
                    'normalized_score': ms.normalized_score(),
                    'reasoning': ms.reasoning,
                    'evidence': ms.evidence,
                    'suggestions': ms.suggestions
                }
                for ms in self.metric_scores
            ],
            'aggregate_score': self.aggregate_score,
            'weighted_score': self.weighted_score,
            'risk_level': self.risk_level.value,
            'recommendation': self.recommendation.value,
            'reasoning': self.reasoning,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'requires_human_review': self.requires_human_review,
            'triggered_rules': self.triggered_rules,
            'confidence_score': self.confidence_score
        }
    
    def get_failing_metrics(self, threshold: float = 5.0) -> List[MetricScore]:
        """Get metrics that scored below threshold"""
        return [ms for ms in self.metric_scores if ms.score < threshold]
    
    def get_top_metrics(self, n: int = 3) -> List[MetricScore]:
        """Get top N highest scoring metrics"""
        return sorted(self.metric_scores, key=lambda x: x.score, reverse=True)[:n]


@dataclass
class HumanReviewRequest:
    """Request for human review of a complaint evaluation"""
    request_id: str
    complaint_id: str
    complaint: Complaint
    evaluation_result: EvaluationResult
    priority_level: int
    executive_summary: str
    key_concerns: List[str]
    review_questions: List[str]
    recommended_actions: List[str]
    created_at: datetime
    assigned_to: Optional[str] = None
    review_deadline: Optional[datetime] = None
    status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert review request to dictionary"""
        return {
            'request_id': self.request_id,
            'complaint_id': self.complaint_id,
            'complaint': self.complaint.to_dict(),
            'evaluation_result': self.evaluation_result.to_dict(),
            'priority_level': self.priority_level,
            'executive_summary': self.executive_summary,
            'key_concerns': self.key_concerns,
            'review_questions': self.review_questions,
            'recommended_actions': self.recommended_actions,
            'created_at': self.created_at.isoformat(),
            'assigned_to': self.assigned_to,
            'review_deadline': self.review_deadline.isoformat() if self.review_deadline else None,
            'status': self.status
        }


@dataclass
class RiskAssessment:
    """Risk assessment for a complaint"""
    complaint_id: str
    financial_risk: float
    regulatory_risk: float
    reputational_risk: float
    operational_risk: float
    overall_risk_score: float
    risk_level: RiskLevel
    risk_factors: List[str] = field(default_factory=list)
    mitigation_suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert risk assessment to dictionary"""
        return {
            'complaint_id': self.complaint_id,
            'financial_risk': self.financial_risk,
            'regulatory_risk': self.regulatory_risk,
            'reputational_risk': self.reputational_risk,
            'operational_risk': self.operational_risk,
            'overall_risk_score': self.overall_risk_score,
            'risk_level': self.risk_level.value,
            'risk_factors': self.risk_factors,
            'mitigation_suggestions': self.mitigation_suggestions
        }


@dataclass
class ComplaintClassification:
    """Classification result for a complaint"""
    complaint_id: str
    primary_type: str
    secondary_types: List[str]
    confidence: float
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert classification to dictionary"""
        return {
            'complaint_id': self.complaint_id,
            'primary_type': self.primary_type,
            'secondary_types': self.secondary_types,
            'confidence': self.confidence,
            'reasoning': self.reasoning
        }
