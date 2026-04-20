"""
LLM Judge Agent System - Main Orchestrator

This module orchestrates the entire evaluation pipeline for banking complaint summaries.
It coordinates multiple AI agents to classify, evaluate, score, and generate recommendations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from src.models.complaint import (
    Complaint, EvaluationResult, HumanReviewRequest,
    Metric, MetricScore, RiskLevel, RecommendationType
)
from src.agents.classifier_agent import ComplaintClassifierAgent
from src.agents.metric_evaluator_agent import MetricEvaluatorAgent
from src.agents.judge_agent import JudgeAgent
from src.agents.human_review_agent import HumanReviewAgent
from src.utils.config_loader import ConfigLoader, get_config_loader
from src.utils.scoring_engine import ScoringEngine


class LLMJudgeOrchestrator:
    """
    Main orchestrator for the LLM Judge Agent system.
    
    Coordinates the evaluation pipeline:
    1. Complaint classification
    2. Metric selection
    3. Metric evaluation
    4. Aggregate scoring
    5. Risk assessment
    6. Human review (if required)
    """
    
    def __init__(
        self,
        config_dir: Optional[str] = None,
        model_name: str = "gpt-4-turbo",
        output_dir: Optional[str] = None,
        provider: str = "auto"
    ):
        """
        Initialize the orchestrator
        
        Args:
            config_dir: Path to configuration directory
            model_name: LLM model to use for all agents (default: gpt-4-turbo)
            output_dir: Directory for output files (evaluations, reviews)
            provider: LLM provider ("openai", "ollama", or "auto" for auto-detection)
        """
        # Initialize configuration
        self.config = get_config_loader(config_dir)
        self.scoring_engine = ScoringEngine(self.config)
        self.model_name = model_name
        self.provider = provider
        
        # Initialize agents
        self.classifier_agent = ComplaintClassifierAgent(self.config, model_name, provider)
        self.evaluator_agent = MetricEvaluatorAgent(self.config, model_name, provider)
        self.judge_agent = JudgeAgent(self.config, self.scoring_engine, model_name, provider)
        self.review_agent = HumanReviewAgent(self.config, self.scoring_engine, model_name, provider)
        
        # Output directory
        self.output_dir = Path(output_dir) if output_dir else Path("./output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'approved': 0,
            'revise': 0,
            'escalated': 0,
            'rejected': 0,
            'human_reviews': 0
        }
    
    def evaluate_complaint(self, complaint: Complaint) -> Dict[str, Any]:
        """
        Evaluate a single complaint through the complete pipeline
        
        Args:
            complaint: Complaint to evaluate
            
        Returns:
            Dictionary containing evaluation results and review request (if applicable)
        """
        print(f"\n{'='*80}")
        print(f"Evaluating Complaint: {complaint.complaint_id}")
        print(f"{'='*80}\n")
        
        # Step 1: Classify complaint (if not already classified)
        if not complaint.complaint_type:
            print("Step 1: Classifying complaint...")
            classification = self.classifier_agent.execute(complaint)
            complaint.complaint_type = classification.primary_type
            complaint.secondary_types = classification.secondary_types
            print(f"  Primary Type: {classification.primary_type}")
            print(f"  Confidence: {classification.confidence:.2%}\n")
        else:
            print(f"Step 1: Using provided complaint type: {complaint.complaint_type}\n")
        
        # Step 2: Get metrics for complaint type
        print("Step 2: Loading evaluation metrics...")
        metrics = self._get_metrics_for_complaint(complaint)
        print(f"  Loaded {len(metrics)} metrics for '{complaint.complaint_type}'\n")
        
        # Step 3: Evaluate against metrics
        print("Step 3: Evaluating against metrics...")
        metric_scores = self.evaluator_agent.execute(complaint, metrics)
        for ms in metric_scores:
            print(f"  {ms.metric_name}: {ms.score:.1f}/5")
        print()
        
        # Step 4: Generate final judgment
        print("Step 4: Generating final judgment...")
        evaluation_result = self.judge_agent.execute(complaint, metric_scores, metrics)
        print(f"  Aggregate Score: {evaluation_result.aggregate_score:.2f}/5")
        print(f"  Weighted Score: {evaluation_result.weighted_score:.2f}/5")
        print(f"  Risk Level: {evaluation_result.risk_level.value}")
        print(f"  Recommendation: {evaluation_result.recommendation.value}")
        print(f"  Requires Human Review: {evaluation_result.requires_human_review}\n")
        
        # Display results table
        print(self._format_results_table(metric_scores, metrics, evaluation_result))
        
        # Step 5: Handle human review if required
        human_review_request = None
        if evaluation_result.requires_human_review:
            print("Step 5: Generating human review request...")
            human_review_request = self.review_agent.execute(complaint, evaluation_result)
            print(f"  Review Request ID: {human_review_request.request_id}")
            print(f"  Priority Level: {human_review_request.priority_level}")
            print(f"  Deadline: {human_review_request.review_deadline.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.stats['human_reviews'] += 1
        
        # Update statistics
        self._update_statistics(evaluation_result)
        
        # Save results
        self._save_evaluation_results(complaint, evaluation_result, human_review_request)
        
        return {
            'complaint': complaint,
            'evaluation_result': evaluation_result,
            'human_review_request': human_review_request
        }
    
    def evaluate_complaints_batch(
        self,
        complaints: List[Complaint]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate multiple complaints in batch
        
        Args:
            complaints: List of complaints to evaluate
            
        Returns:
            List of evaluation results
        """
        results = []
        
        print(f"\n{'='*80}")
        print(f"BATCH EVALUATION: Processing {len(complaints)} complaints")
        print(f"{'='*80}\n")
        
        for i, complaint in enumerate(complaints, 1):
            print(f"\nProcessing complaint {i}/{len(complaints)}...")
            result = self.evaluate_complaint(complaint)   # This will have the complaint type, metric scores, evaluation result, and human review request (if applicable)
            results.append(result)
        
        # Print summary statistics
        self.print_statistics()
        
        return results
    
    def _get_metrics_for_complaint(self, complaint: Complaint) -> List[Metric]:
        """
        Get evaluation metrics for a complaint
        
        Args:
            complaint: Complaint to get metrics for
            
        Returns:
            List of Metric objects
        """
        metric_configs = self.config.get_metrics_for_complaint_type(complaint.complaint_type)
        
        metrics = []
        for mc in metric_configs:
            metric = Metric(
                metric_id=mc.get('metric_id', ''),
                name=mc.get('name', ''),
                description=mc.get('description', ''),
                weight=mc.get('weight', 0.0),
                scale=mc.get('scale', '1-5')
            )
            metrics.append(metric)
        
        return metrics
    
    def _format_results_table(
        self,
        metric_scores: List[MetricScore],
        metrics: List[Metric],
        evaluation_result: EvaluationResult
    ) -> str:
        """
        Format evaluation results as a table
        
        Args:
            metric_scores: List of metric scores
            metrics: List of metric configurations
            evaluation_result: Complete evaluation result
            
        Returns:
            Formatted table string
        """
        # Create metric weight map
        weight_map = {m.metric_id: m.weight for m in metrics}
        
        # Table header
        lines = []
        lines.append("\n" + "="*95)
        lines.append("EVALUATION RESULTS TABLE")
        lines.append("="*95)
        lines.append(f"{'Metric':<30} {'Score':>8} {'Weight':>10} {'Weighted':>12} {'Max':>8}")
        lines.append("-"*95)
        
        # Metric rows
        for ms in metric_scores:
            weight = weight_map.get(ms.metric_id, 0)
            weighted_contrib = ms.normalized_score() * weight * 5.0  # Convert to 0-5 scale
            lines.append(
                f"{ms.metric_name:<30} {ms.score:>8.2f} {weight*100:>9.1f}% "
                f"{weighted_contrib:>12.3f} {ms.max_score:>8.1f}"
            )
        
        # Summary section
        lines.append("-"*95)
        lines.append(f"{'AGGREGATE SCORE (Unweighted)':<30} {evaluation_result.aggregate_score:>8.2f}/5")
        lines.append(f"{'WEIGHTED SCORE':<30} {evaluation_result.weighted_score:>8.2f}/5")
        lines.append("-"*95)
        lines.append(f"{'Risk Level':<30} {evaluation_result.risk_level.value.upper():>8}")
        lines.append(f"{'Recommendation':<30} {evaluation_result.recommendation.value.upper():>8}")
        lines.append(f"{'Human Review Required':<30} {'YES' if evaluation_result.requires_human_review else 'NO':>8}")
        lines.append("="*95)
        
        return "\n".join(lines)
    
    def _update_statistics(self, evaluation_result: EvaluationResult):
        """Update processing statistics"""
        self.stats['total_processed'] += 1
        
        if evaluation_result.recommendation == RecommendationType.APPROVE:
            self.stats['approved'] += 1
        elif evaluation_result.recommendation == RecommendationType.REVISE:
            self.stats['revise'] += 1
        elif evaluation_result.recommendation == RecommendationType.ESCALATE:
            self.stats['escalated'] += 1
        elif evaluation_result.recommendation == RecommendationType.REJECT:
            self.stats['rejected'] += 1
    
    def _save_evaluation_results(
        self,
        complaint: Complaint,
        evaluation_result: EvaluationResult,
        human_review_request: Optional[HumanReviewRequest]
    ):
        """
        Save evaluation results to output directory
        
        Args:
            complaint: Original complaint
            evaluation_result: Evaluation result
            human_review_request: Human review request (if applicable)
        """
        # Create output subdirectories
        evaluations_dir = self.output_dir / "evaluations"
        reviews_dir = self.output_dir / "human_reviews"
        evaluations_dir.mkdir(exist_ok=True)
        reviews_dir.mkdir(exist_ok=True)
        
        # Save evaluation result as JSON
        eval_filename = evaluations_dir / f"{complaint.complaint_id}_evaluation.json"
        with open(eval_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'complaint': complaint.to_dict(),
                'evaluation': evaluation_result.to_dict()
            }, f, indent=2, default=str)
        
        # Save evaluation result as formatted table
        metrics = self._get_metrics_for_complaint(complaint)
        table_filename = evaluations_dir / f"{complaint.complaint_id}_report.txt"
        with open(table_filename, 'w', encoding='utf-8') as f:
            f.write(f"COMPLAINT EVALUATION REPORT\\n")
            f.write(f"{'='*95}\\n\\n")
            f.write(f"Complaint ID: {complaint.complaint_id}\\n")
            f.write(f"Customer ID: {complaint.customer_id}\\n")
            f.write(f"Complaint Type: {complaint.complaint_type}\\n")
            f.write(f"Submission Date: {complaint.submission_date}\\n\\n")
            f.write(f"SUMMARY:\\n{'-'*95}\\n")
            f.write(f"{complaint.summary}\\n\\n")
            f.write(self._format_results_table(evaluation_result.metric_scores, metrics, evaluation_result))
            f.write(f"\\n\\nEvaluation Timestamp: {evaluation_result.evaluation_timestamp}\\n")
        
        # Save human review request if exists
        if human_review_request:
            review_filename = reviews_dir / f"{human_review_request.request_id}_review.json"
            with open(review_filename, 'w', encoding='utf-8') as f:
                json.dump(human_review_request.to_dict(), f, indent=2, default=str)
            
            # Also save human-readable version
            readable_filename = reviews_dir / f"{human_review_request.request_id}_review.txt"
            with open(readable_filename, 'w', encoding='utf-8') as f:
                f.write(self.review_agent.format_review_request_for_display(human_review_request))
    
    def print_statistics(self):
        """Print processing statistics"""
        total = self.stats['total_processed']
        if total == 0:
            print("\nNo complaints processed yet.")
            return
        
        print(f"\n{'='*80}")
        print("EVALUATION STATISTICS")
        print(f"{'='*80}")
        print(f"Total Processed: {total}")
        print(f"Approved: {self.stats['approved']} ({self.stats['approved']/total*100:.1f}%)")
        print(f"Revise: {self.stats['revise']} ({self.stats['revise']/total*100:.1f}%)")
        print(f"Escalated: {self.stats['escalated']} ({self.stats['escalated']/total*100:.1f}%)")
        print(f"Rejected: {self.stats['rejected']} ({self.stats['rejected']/total*100:.1f}%)")
        print(f"Human Reviews: {self.stats['human_reviews']} ({self.stats['human_reviews']/total*100:.1f}%)")
        print(f"{'='*80}\n")
    
    def get_pending_human_reviews(self) -> List[Dict[str, Any]]:
        """
        Get all pending human review requests
        
        Returns:
            List of pending review request data
        """
        reviews_dir = self.output_dir / "human_reviews"
        if not reviews_dir.exists():
            return []
        
        pending_reviews = []
        for review_file in reviews_dir.glob("*_review.json"):
            with open(review_file, 'r', encoding='utf-8') as f:
                review_data = json.load(f)
                if review_data.get('status') == 'pending':
                    pending_reviews.append(review_data)
        
        # Sort by priority and deadline
        pending_reviews.sort(key=lambda x: (x['priority_level'], x['created_at']))
        
        return pending_reviews
    
    def validate_configuration(self) -> bool:
        """
        Validate all configurations
        
        Returns:
            True if all configurations are valid
        """
        print("\nValidating configurations...")
        results = self.config.validate_configurations()
        
        all_valid = all(results.values())
        
        for config_name, is_valid in results.items():
            status = "✓ VALID" if is_valid else "✗ INVALID"
            print(f"  {config_name}: {status}")
        
        # Validate metric weights for all complaint types
        print("\nValidating metric weights...")
        complaint_types = self.config.get_all_complaint_types()
        
        for complaint_type in complaint_types:
            is_valid = self.config.validate_metric_weights(complaint_type)
            status = "✓" if is_valid else "✗"
            print(f"  {status} {complaint_type}")
            if not is_valid:
                all_valid = False
        
        print()
        return all_valid


def create_sample_complaint(
    complaint_id: str,
    summary: str,
    original: str,
    complaint_type: Optional[str] = None
) -> Complaint:
    """
    Create a sample complaint for testing
    
    Args:
        complaint_id: Complaint identifier
        summary: SCRIBE-generated summary
        original: Original complaint text
        complaint_type: Optional complaint type
        
    Returns:
        Complaint object
    """
    return Complaint(
        complaint_id=complaint_id,
        customer_id=f"CUST_{complaint_id}",
        original_complaint=original,
        summary=summary,
        submission_date=datetime.now(),
        complaint_type=complaint_type,
        has_previous_complaints=False,
        previous_complaint_count=0,
        is_high_value_customer=False
    )
