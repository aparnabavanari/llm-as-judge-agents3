"""
Example usage of the LLM Judge Agent System

This script demonstrates how to use the system to evaluate banking complaint summaries.
"""

from datetime import datetime
from src.main import LLMJudgeOrchestrator, create_sample_complaint


def main():
    """Run example evaluations"""
    
    print("\n" + "="*80)
    print("LLM JUDGE AGENT SYSTEM - Banking Complaint Evaluation")
    print("="*80 + "\n")
    
    # Initialize orchestrator
    print("Initializing LLM Judge Orchestrator...")
    orchestrator = LLMJudgeOrchestrator(
        model_name="gpt-4-turbo",
        output_dir="./output"
    )
    
    # Validate configurations
    print("\n" + "-"*80)
    if not orchestrator.validate_configuration():
        print("WARNING: Configuration validation failed. Please check the config files.")
    print("-"*80 + "\n")
    
    # Create sample complaints for different types
    complaints = [
        # High-risk fraud complaint
        create_sample_complaint(
            complaint_id="COMP_001",
            complaint_type="fraud",
            summary="""
            Customer reports unauthorized transactions totaling $5,432 on checking account 
            ending in 7890. Three suspicious wire transfers occurred on 04/06/2026 to 
            unfamiliar recipients. Customer claims no knowledge of these transactions and 
            noticed the issue when checking balance on 04/08/2026. Account has been 
            temporarily frozen pending investigation. Customer requests immediate refund 
            and investigation into security breach.
            """.strip(),
            original="""
            I just checked my account and there are three wire transfers I never authorized! 
            Someone stole over $5000 from my account! This happened two days ago and I had 
            no idea. I need this money back immediately and I want to know how this happened. 
            I'm very worried about my account security. Please help!
            """.strip()
        ),
        
        # Medium-risk fees dispute
        create_sample_complaint(
            complaint_id="COMP_002",
            complaint_type="fees_charges",
            summary="""
            Customer disputes overdraft fees totaling $175 charged on 04/05/2026. Claims 
            direct deposit was scheduled to arrive on 04/04/2026 but was delayed by the bank 
            until 04/06/2026, causing account to overdraft. Customer has been with bank for 
            8 years with no prior overdraft issues. Requesting fee reversal as the delay was 
            not customer's fault. Account currently shows positive balance after deposit.
            """.strip(),
            original="""
            I'm very frustrated with these overdraft fees. My paycheck was supposed to be 
            deposited on the 4th but didn't show up until the 6th, and in the meantime I got 
            hit with $175 in fees. This isn't fair - I've been a customer for 8 years and 
            never had this problem. Can you please reverse these fees?
            """.strip()
        ),
        
        # Low-risk customer service complaint
        create_sample_complaint(
            complaint_id="COMP_003",
            complaint_type="customer_service",
            summary="""
            Customer reports unsatisfactory experience with phone support on 04/07/2026. 
            Called regarding simple balance inquiry but was transferred three times and 
            waited 45 minutes total. Final representative was able to answer question but 
            customer felt the experience was inefficient. Customer suggests better training 
            for front-line staff to handle basic inquiries without multiple transfers.
            """.strip(),
            original="""
            I called yesterday just to check my balance and it took 45 minutes and three 
            different people to get an answer. This is ridiculous for such a simple question. 
            Your staff should be better trained to handle basic requests without transferring 
            people around. Very frustrating experience.
            """.strip()
        ),
        
        # Critical regulatory compliance issue
        create_sample_complaint(
            complaint_id="COMP_004",
            complaint_type="regulatory_compliance",
            summary="""
            Customer alleges violation of fair lending practices. Applied for mortgage 
            on 03/15/2026 with similar financial profile and credit score as colleague who 
            was approved. Customer's application denied on 04/01/2026 without clear explanation. 
            Customer believes denial may be discriminatory based on protected characteristics. 
            Requesting detailed written explanation of denial reasons and review of lending 
            practices. Matter may require regulatory review if not resolved satisfactorily.
            """.strip(),
            original="""
            I applied for a mortgage and was denied, but my colleague with similar income and 
            credit score got approved. I think I'm being discriminated against. I want a full 
            explanation of why I was denied and I'm considering filing a complaint with the 
            regulatory agency. This doesn't seem legal or fair.
            """.strip()
        ),
    ]
    
    # Evaluate all complaints
    results = orchestrator.evaluate_complaints_batch(complaints)
    
    # Print processing summary
    print("\n" + "="*80)
    print(f"PROCESSING COMPLETE - {len(results)} Complaints Evaluated")
    print("="*80)
    
    # Comprehensive complaint-wise results table
    print("\n" + "="*140)
    print("COMPLAINT-WISE EVALUATION RESULTS - COMPREHENSIVE SUMMARY")
    print("="*140)
    
    for i, result in enumerate(results, 1):
        complaint = result['complaint']
        evaluation = result['evaluation_result']
        
        print(f"\n{'─'*140}")
        print(f"COMPLAINT #{i}: {complaint.complaint_id}")
        print(f"{'─'*140}")
        
        # Basic information row
        print(f"{'Type:':<20} {complaint.complaint_type}")
        print(f"{'Summary:':<20} {complaint.summary[:95]}...")
        print(f"{'Submitted:':<20} {complaint.submission_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"{'Customer ID:':<20} {complaint.customer_id}")
        
        print(f"\n{'SCORES & EVALUATION':<50}")
        print("─"*140)
        
        # Evaluation metrics in compact table format
        print(f"{'Metric Name':<30} {'Score':>10} {'Weight':>10} {'Contribution':>15} {'Rating':>15}")
        print("─"*140)
        
        metrics = orchestrator._get_metrics_for_complaint(complaint)
        weight_map = {m.metric_id: m.weight for m in metrics}
        
        for ms in evaluation.metric_scores:
            weight = weight_map.get(ms.metric_id, 0)
            contribution = ms.normalized_score() * weight * 5.0
            
            # Rating based on score
            if ms.score >= 4.5:
                rating = "⭐ Excellent"
            elif ms.score >= 3.5:
                rating = "✓ Good"
            elif ms.score >= 2.5:
                rating = "○ Satisfactory"
            elif ms.score >= 1.5:
                rating = "⚠ Poor"
            else:
                rating = "✗ Inadequate"
            
            print(f"{ms.metric_name:<30} {ms.score:>10.2f}/5 {weight*100:>9.1f}% {contribution:>15.3f} {rating:>15}")
        
        print("─"*140)
        
        # Aggregate scores row
        print(f"{'AGGREGATE SCORE:':<30} {evaluation.aggregate_score:>10.2f}/5")
        print(f"{'WEIGHTED SCORE:':<30} {evaluation.weighted_score:>10.2f}/5")
        print("─"*140)
        
        # Risk and decision row
        risk_indicator = {
            'low': '🟢 LOW',
            'medium': '🟡 MEDIUM',
            'high': '🔴 HIGH',
            'critical': '⛔ CRITICAL'
        }.get(evaluation.risk_level.value, evaluation.risk_level.value.upper())
        
        recommendation_icon = {
            'approve': '✅ APPROVE',
            'revise': '📝 REVISE',
            'escalate': '⬆️ ESCALATE',
            'reject': '❌ REJECT'
        }.get(evaluation.recommendation.value, evaluation.recommendation.value.upper())
        
        print(f"{'RISK LEVEL:':<30} {risk_indicator}")
        print(f"{'RECOMMENDATION:':<30} {recommendation_icon}")
        print(f"{'HUMAN REVIEW REQUIRED:':<30} {'⚠️ YES' if evaluation.requires_human_review else '✓ NO'}")
        print(f"{'CONFIDENCE SCORE:':<30} {evaluation.confidence_score:>10.1f}%")
        
        print("─"*140)
        
        # Strengths and weaknesses
        if evaluation.strengths:
            print(f"\n{'STRENGTHS IDENTIFIED:':<30} ({len(evaluation.strengths)} items)")
            for idx, strength in enumerate(evaluation.strengths[:3], 1):
                print(f"  {idx}. ✓ {strength}")
            if len(evaluation.strengths) > 3:
                print(f"     ... and {len(evaluation.strengths) - 3} more")
        
        if evaluation.weaknesses:
            print(f"\n{'WEAKNESSES IDENTIFIED:':<30} ({len(evaluation.weaknesses)} items)")
            for idx, weakness in enumerate(evaluation.weaknesses[:3], 1):
                print(f"  {idx}. ✗ {weakness}")
            if len(evaluation.weaknesses) > 3:
                print(f"     ... and {len(evaluation.weaknesses) - 3} more")
        
        # Improvement suggestions from metrics
        all_suggestions = []
        for ms in evaluation.metric_scores:
            all_suggestions.extend(ms.suggestions)
        
        if all_suggestions:
            print(f"\n{'IMPROVEMENT SUGGESTIONS:':<30} ({len(all_suggestions)} items)")
            for idx, suggestion in enumerate(all_suggestions[:2], 1):
                print(f"  {idx}. → {suggestion}")
            if len(all_suggestions) > 2:
                print(f"     ... and {len(all_suggestions) - 2} more")
        
        print()
    
    print("="*140)
    
    # Quick reference summary table
    print("\n" + "="*120)
    print("QUICK REFERENCE SUMMARY")
    print("="*120)
    print(f"{'ID':<15} {'Type':<22} {'Weighted':>12} {'Risk':>12} {'Decision':>15} {'Review':>12} {'Confidence':>12}")
    print("-"*120)
    
    for result in results:
        complaint = result['complaint']
        evaluation = result['evaluation_result']
        print(
            f"{complaint.complaint_id:<15} "
            f"{complaint.complaint_type:<22} "
            f"{evaluation.weighted_score:>11.2f}/5 "
            f"{evaluation.risk_level.value:>12} "
            f"{evaluation.recommendation.value:>15} "
            f"{'YES' if evaluation.requires_human_review else 'NO':>12} "
            f"{evaluation.confidence_score:>11.1f}%"
        )
    
    print("="*120 + "\n")
    
    # Check for pending human reviews
    pending_reviews = orchestrator.get_pending_human_reviews()
    if pending_reviews:
        print(f"\n⚠ {len(pending_reviews)} PENDING HUMAN REVIEWS")
        print("─"*80)
        for review in pending_reviews:
            print(f"  • {review['request_id']} - Priority {review['priority_level']} - "
                  f"Complaint: {review['complaint_id']}")
        print()
    
    print("\nEvaluation complete. Results saved to ./output directory.")
    print("  - JSON results: ./output/evaluations/*_evaluation.json")
    print("  - Formatted reports: ./output/evaluations/*_report.txt")
    print("  - Human reviews: ./output/human_reviews/")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
