"""
Streamlit UI for LLM Judge Agent System

Interactive interface for evaluating banking complaint summaries
using AI-powered judge agents.
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import json
import os
from typing import Optional, Dict, Any, List

from src.main import LLMJudgeOrchestrator, create_sample_complaint
from src.models.complaint import Complaint, RiskLevel, RecommendationType


# Page configuration
st.set_page_config(
    page_title="LLM Judge Agent System",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .danger-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables"""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None
    if 'evaluation_history' not in st.session_state:
        st.session_state.evaluation_history = []
    if 'current_evaluation' not in st.session_state:
        st.session_state.current_evaluation = None


def initialize_orchestrator(model_name: str = "gpt-4-turbo", provider: str = "auto", use_database: bool = True):
    """Initialize or get the orchestrator"""
    if st.session_state.orchestrator is None:
        with st.spinner("Initializing LLM Judge Orchestrator..."):
            st.session_state.orchestrator = LLMJudgeOrchestrator(
                model_name=model_name,
                output_dir="./output",
                provider=provider,
                use_database=use_database
            )
        st.success("✅ Orchestrator initialized successfully!")
    return st.session_state.orchestrator


def get_risk_level_color(risk_level: RiskLevel) -> str:
    """Get color for risk level"""
    colors = {
        RiskLevel.CRITICAL: "#dc3545",
        RiskLevel.HIGH: "#fd7e14",
        RiskLevel.MEDIUM: "#ffc107",
        RiskLevel.LOW: "#28a745"
    }
    return colors.get(risk_level, "#6c757d")


def get_recommendation_style(recommendation: RecommendationType) -> str:
    """Get CSS class for recommendation"""
    styles = {
        RecommendationType.APPROVE: "success-box",
        RecommendationType.REVISE: "warning-box",
        RecommendationType.ESCALATE: "danger-box",
        RecommendationType.REJECT: "danger-box"
    }
    return styles.get(recommendation, "info-box")


def render_sidebar():
    """Render the sidebar navigation"""
    st.sidebar.markdown("## ⚖️ LLM Judge System")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📝 Evaluate Complaint", "📊 View Results", "⚙️ Settings", "📈 Statistics"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### System Info")
    if st.session_state.orchestrator:
        st.sidebar.success("🟢 Orchestrator Active")
        stats = st.session_state.orchestrator.stats
        st.sidebar.metric("Total Processed", stats.get('total_processed', 0))
        st.sidebar.metric("Human Reviews", stats.get('human_reviews', 0))
    else:
        st.sidebar.warning("🔴 Not Initialized")
    
    return page


def render_home_page():
    """Render the home page"""
    st.markdown('<div class="main-header">⚖️ LLM Judge Agent System</div>', unsafe_allow_html=True)
    st.markdown("### Banking Complaint Summary Evaluation Platform")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🤖 AI-Powered")
        st.write("Leverages advanced LLMs for intelligent complaint evaluation")
    
    with col2:
        st.markdown("#### 📊 Multi-Agent")
        st.write("Classifier, Evaluator, Judge, and Review agents working together")
    
    with col3:
        st.markdown("#### ⚡ Fast & Accurate")
        st.write("Rapid evaluation with detailed scoring and recommendations")
    
    st.markdown("---")
    
    # Quick start guide
    st.markdown("### 🚀 Quick Start")
    
    with st.expander("1️⃣ Initialize the System", expanded=True):
        # Provider selection
        provider_choice = st.radio(
            "Select Provider",
            ["OpenAI (Cloud)", "Ollama (Local)"],
            horizontal=True
        )
        
        if "OpenAI" in provider_choice:
            model_options = ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-4o"]
            selected_model = st.selectbox("Select OpenAI Model", model_options)
            provider = "openai"
            
            # Check for API key
            if not os.getenv('OPENAI_API_KEY'):
                st.warning("⚠️ OPENAI_API_KEY environment variable not set. Please set it before initializing.")
        else:
            model_options = ["gemma3:1b", "mistral", "llama3", "llama2"]
            selected_model = st.selectbox("Select Ollama Model", model_options)
            provider = "ollama"
            
            st.info("💡 Make sure Ollama is running and the model is downloaded. Run: `ollama pull " + selected_model + "`")
        
        if st.button("Initialize Orchestrator", type="primary"):
            try:
                initialize_orchestrator(selected_model, provider)
            except Exception as e:
                st.error(f"❌ Initialization failed: {str(e)}")
                if "ollama" in str(e).lower():
                    st.info("Make sure Ollama is running: `ollama serve`")
    
    with st.expander("2️⃣ Evaluate Complaints"):
        st.write("Navigate to **📝 Evaluate Complaint** to submit and evaluate complaints")
        st.write("- Enter complaint details manually")
        st.write("- Or use sample complaints for testing")
    
    with st.expander("3️⃣ View Results"):
        st.write("Check **📊 View Results** to see evaluation history and detailed reports")
    
    # System overview
    st.markdown("---")
    st.markdown("### 🔄 Evaluation Pipeline")
    
    pipeline_steps = """
    ```
    📥 Complaint Input
         ↓
    🏷️ Classification Agent → Categorize complaint type
         ↓
    📐 Metric Evaluator Agent → Score against quality metrics
         ↓
    ⚖️ Judge Agent → Aggregate scoring & risk assessment
         ↓
    👤 Human Review Agent → Generate review request (if needed)
         ↓
    ✅ Final Recommendation
    ```
    """
    st.markdown(pipeline_steps)


def render_evaluation_page():
    """Render the complaint evaluation page"""
    st.markdown("## 📝 Evaluate Banking Complaint")
    
    # Ensure orchestrator is initialized
    if st.session_state.orchestrator is None:
        st.warning("⚠️ Please initialize the orchestrator first from the Home page")
        return
    
    orchestrator = st.session_state.orchestrator
    
    # Input method selection
    input_method = st.radio(
        "Input Method",
        ["Manual Entry", "Sample Complaints", "JSON Upload"],
        horizontal=True
    )
    
    complaint = None
    
    if input_method == "Manual Entry":
        st.markdown("### Enter Complaint Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            complaint_id = st.text_input("Complaint ID", value=f"COMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            customer_id = st.text_input("Customer ID", value=f"CUST_{datetime.now().strftime('%H%M%S')}")
            complaint_type = st.selectbox(
                "Complaint Type (Optional)",
                ["", "fraud", "service_quality", "billing_dispute", "account_access", "loan_issue", "other"]
            )
        
        with col2:
            is_high_value = st.checkbox("High Value Customer")
            has_previous = st.checkbox("Has Previous Complaints")
            previous_count = st.number_input("Previous Complaint Count", min_value=0, value=0) if has_previous else 0
        
        original_complaint = st.text_area(
            "Original Complaint",
            placeholder="Enter the customer's original complaint text...",
            height=150
        )
        
        summary = st.text_area(
            "Complaint Summary",
            placeholder="Enter the summarized version of the complaint...",
            height=150
        )
        
        if st.button("🔍 Evaluate Complaint", type="primary"):
            if not original_complaint or not summary:
                st.error("Please provide both original complaint and summary")
            else:
                complaint = Complaint(
                    complaint_id=complaint_id,
                    customer_id=customer_id,
                    original_complaint=original_complaint,
                    summary=summary,
                    submission_date=datetime.now(),
                    complaint_type=complaint_type if complaint_type else None,
                    has_previous_complaints=has_previous,
                    previous_complaint_count=previous_count,
                    is_high_value_customer=is_high_value
                )
    
    elif input_method == "Sample Complaints":
        st.markdown("### Select Sample Complaint")
        
        sample_types = {
            "🚨 Fraud - High Risk": "fraud_high_risk",
            "💰 Billing Dispute": "billing_dispute",
            "🔒 Account Access Issue": "account_access",
            "⭐ Service Quality": "service_quality"
        }
        
        selected_sample = st.selectbox("Choose Sample", list(sample_types.keys()))
        
        if st.button("Load Sample", type="primary"):
            sample_type = sample_types[selected_sample]
            # Generate appropriate sample based on type
            if "fraud" in sample_type.lower():
                summary = "Customer reports unauthorized transactions totaling $5,432 on checking account ending in 7890. Three suspicious wire transfers occurred to unfamiliar recipients. Customer claims no knowledge of these transactions."
                original = "I just checked my account and there are three wire transfers I never authorized! Someone stole over $5000 from my account! This happened two days ago and I had no idea. I need this money back immediately!"
            elif "billing" in sample_type.lower():
                summary = "Customer disputes monthly service fees of $35 charged incorrectly for three consecutive months. Account should be fee-free based on balance requirements. Requesting full refund."
                original = "Why am I being charged $35 every month? My account should be fee-free since I maintain the minimum balance. This has been going on for 3 months. I want my money back!"
            elif "account" in sample_type.lower():
                summary = "Customer unable to access online banking for 5 days. Multiple password reset attempts failed. Unable to pay bills or check balance. Requests immediate resolution."
                original = "I can't log into my online banking! I've tried resetting my password 3 times and it's still not working. It's been almost a week and I need to pay my bills. This is unacceptable!"
            else:
                summary = "Customer reports poor service experience at branch. Long wait times, unhelpful staff, and incomplete transaction processing. Requests service improvement and compensation."
                original = "I waited 45 minutes at the branch today just to deposit a check. The staff was rude and didn't help me properly. My transaction wasn't even completed correctly. This is terrible service!"
            
            complaint = create_sample_complaint(
                complaint_id=f"SAMPLE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                summary=summary,
                original=original,
                complaint_type=sample_type.split('_')[0] if '_' in sample_type else sample_type
            )
    
    elif input_method == "JSON Upload":
        st.markdown("### Upload Complaint JSON")
        uploaded_file = st.file_uploader("Choose a JSON file", type=['json'])
        
        if uploaded_file:
            try:
                complaint_data = json.load(uploaded_file)
                complaint = Complaint(
                    complaint_id=complaint_data['complaint_id'],
                    customer_id=complaint_data['customer_id'],
                    original_complaint=complaint_data['original_complaint'],
                    summary=complaint_data['summary'],
                    submission_date=datetime.fromisoformat(complaint_data.get('submission_date', datetime.now().isoformat())),
                    complaint_type=complaint_data.get('complaint_type'),
                    has_previous_complaints=complaint_data.get('has_previous_complaints', False),
                    previous_complaint_count=complaint_data.get('previous_complaint_count', 0),
                    is_high_value_customer=complaint_data.get('is_high_value_customer', False)
                )
                st.success("✅ Complaint loaded successfully")
                
                if st.button("🔍 Evaluate Complaint", type="primary"):
                    pass  # Will be processed below
            except Exception as e:
                st.error(f"Error loading JSON: {str(e)}")
    
    # Process evaluation
    if complaint:
        with st.spinner("🔄 Evaluating complaint... This may take a moment..."):
            try:
                # Create progress indicator
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Step 1/5: Classifying complaint...")
                progress_bar.progress(20)
                
                # Run evaluation
                result = orchestrator.evaluate_complaint(complaint)
                
                progress_bar.progress(100)
                status_text.text("✅ Evaluation complete!")
                
                # Store in session state
                st.session_state.current_evaluation = result
                st.session_state.evaluation_history.append(result)
                
                # Display results
                st.success("✅ Evaluation Complete!")
                display_evaluation_results(result)
                
            except Exception as e:
                st.error(f"❌ Error during evaluation: {str(e)}")
                st.exception(e)


def display_evaluation_results(result: Dict[str, Any]):
    """Display evaluation results in a formatted manner"""
    complaint = result['complaint']
    evaluation = result['evaluation_result']
    review_request = result.get('human_review_request')
    
    st.markdown("---")
    st.markdown("## 📊 Evaluation Results")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Complaint ID", complaint.complaint_id)
    
    with col2:
        st.metric("Complaint Type", evaluation.complaint_type.upper())
    
    with col3:
        risk_color = get_risk_level_color(evaluation.risk_level)
        st.markdown(f"**Risk Level**")
        st.markdown(f'<div style="background-color: {risk_color}; color: white; padding: 0.5rem; border-radius: 0.5rem; text-align: center; font-weight: bold;">{evaluation.risk_level.value.upper()}</div>', unsafe_allow_html=True)
    
    with col4:
        st.metric("Aggregate Score", f"{evaluation.aggregate_score:.2f}/5.00")
    
    # Recommendation
    st.markdown("### 📋 Recommendation")
    rec_style = get_recommendation_style(evaluation.recommendation)
    st.markdown(f'<div class="{rec_style}"><h3>{evaluation.recommendation.value.upper()}</h3><p>{evaluation.reasoning}</p></div>', unsafe_allow_html=True)
    
    # Metric Scores
    st.markdown("### 📏 Metric Scores")
    
    for metric_score in evaluation.metric_scores:
        with st.expander(f"**{metric_score.metric_name}** - Score: {metric_score.score:.1f}/{metric_score.max_score}"):
            st.write(f"**Reasoning:** {metric_score.reasoning}")
            
            if metric_score.evidence:
                st.write("**Evidence:**")
                for evidence in metric_score.evidence:
                    st.write(f"- {evidence}")
            
            if metric_score.suggestions:
                st.write("**Suggestions:**")
                for suggestion in metric_score.suggestions:
                    st.write(f"- {suggestion}")
    
    # Strengths and Areas for Improvement
    col1, col2 = st.columns(2)
    
    with col1:
        if evaluation.strengths:
            st.markdown("### ✅ Strengths")
            for strength in evaluation.strengths:
                st.success(strength)
    
    with col2:
        if evaluation.weaknesses:
            st.markdown("### 🔍 Areas for Improvement")
            for area in evaluation.weaknesses:
                st.warning(area)
    
    # Human Review Request
    if review_request:
        st.markdown("### 👤 Human Review Required")
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.write(f"**Request ID:** {review_request.request_id}")
        st.write(f"**Priority:** {review_request.priority_level}")
        st.write(f"**Deadline:** {review_request.review_deadline.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Reason:** {review_request.review_reason}")
        
        if review_request.focus_areas:
            st.write("**Focus Areas:**")
            for area in review_request.focus_areas:
                st.write(f"- {area}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Raw data expander
    with st.expander("📄 View Raw Data"):
        st.json({
            'complaint': complaint.to_dict(),
            'evaluation': {
                'aggregate_score': evaluation.aggregate_score,
                'weighted_score': evaluation.weighted_score,
                'risk_level': evaluation.risk_level.value,
                'recommendation': evaluation.recommendation.value,
                'requires_human_review': evaluation.requires_human_review,
                'reasoning': evaluation.reasoning
            }
        })


def render_results_page():
    """Render the results viewing page"""
    st.markdown("## 📊 Evaluation Results & History")
    
    if not st.session_state.evaluation_history:
        st.info("No evaluations yet. Go to the Evaluate Complaint page to get started!")
        return
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📜 Recent Evaluations", "📁 Saved Results", "🔍 Search"])
    
    with tab1:
        st.markdown("### Recent Evaluations (Current Session)")
        
        for i, result in enumerate(reversed(st.session_state.evaluation_history)):
            evaluation = result['evaluation_result']
            complaint = result['complaint']
            
            with st.expander(f"**{complaint.complaint_id}** - {evaluation.recommendation.value.upper()} ({evaluation.risk_level.value})"):
                display_evaluation_results(result)
    
    with tab2:
        st.markdown("### Saved Evaluation Files")
        
        output_dir = Path("./output/evaluations")
        if output_dir.exists():
            json_files = list(output_dir.glob("*_evaluation.json"))
            
            if json_files:
                for json_file in sorted(json_files, reverse=True)[:10]:  # Show latest 10
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                        
                        complaint_id = data.get('complaint_id', json_file.stem)
                        recommendation = data.get('recommendation', 'N/A')
                        risk_level = data.get('risk_level', 'N/A')
                        
                        with st.expander(f"**{complaint_id}** - {recommendation} ({risk_level})"):
                            st.json(data)
                    except Exception as e:
                        st.error(f"Error loading {json_file.name}: {str(e)}")
            else:
                st.info("No saved evaluations found")
        else:
            st.info("Output directory not found")
    
    with tab3:
        st.markdown("### Search Evaluations")
        st.info("🚧 Search functionality coming soon!")


def render_settings_page():
    """Render the settings page"""
    st.markdown("## ⚙️ System Settings")
    
    tab1, tab2, tab3 = st.tabs(["🤖 Model Settings", "📋 Configuration", "📂 Output"])
    
    with tab1:
        st.markdown("### LLM Model Configuration")
        
        if st.session_state.orchestrator:
            current_model = st.session_state.orchestrator.model_name
            current_provider = st.session_state.orchestrator.provider
            st.info(f"Current Model: **{current_model}** (Provider: {current_provider})")
        else:
            st.info("Current Model: **Not initialized**")
        
        st.markdown("#### Reinitialize with Different Model")
        
        # Provider selection
        provider_choice = st.radio(
            "Select Provider",
            ["OpenAI (Cloud)", "Ollama (Local)"],
            horizontal=True,
            key="settings_provider"
        )
        
        if "OpenAI" in provider_choice:
            model_options = ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-4o"]
            new_model = st.selectbox("Select OpenAI Model", model_options, key="settings_openai_model")
            provider = "openai"
        else:
            model_options = ["gemma3:1b", "mistral", "llama3", "llama2"]
            new_model = st.selectbox("Select Ollama Model", model_options, key="settings_ollama_model")
            provider = "ollama"
            st.info("💡 Make sure Ollama is running and model is pulled: `ollama pull " + new_model + "`")
        
        if st.button("Reinitialize Orchestrator"):
            st.session_state.orchestrator = None
            try:
                initialize_orchestrator(new_model, provider)
            except Exception as e:
                st.error(f"❌ Initialization failed: {str(e)}")
    
    with tab2:
        st.markdown("### Configuration Files")
        
        config_files = {
            "Business Rules": "config/business_rules.yaml",
            "Evaluation Profiles": "config/evaluation_profiles.yaml",
            "Prompts": "config/prompts.yaml"
        }
        
        for name, path in config_files.items():
            with st.expander(f"📄 {name}"):
                file_path = Path(path)
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        content = f.read()
                    st.code(content, language='yaml')
                else:
                    st.warning(f"File not found: {path}")
    
    with tab3:
        st.markdown("### Output Directory")
        
        output_dir = Path("./output")
        st.info(f"Output Location: `{output_dir.absolute()}`")
        
        if output_dir.exists():
            subdirs = [d for d in output_dir.iterdir() if d.is_dir()]
            st.write(f"Found {len(subdirs)} subdirectories:")
            for subdir in subdirs:
                file_count = len(list(subdir.iterdir()))
                st.write(f"- `{subdir.name}`: {file_count} files")


def render_statistics_page():
    """Render the statistics page"""
    st.markdown("## 📈 System Statistics")
    
    if st.session_state.orchestrator is None:
        st.warning("Initialize the orchestrator to view statistics")
        return
    
    stats = st.session_state.orchestrator.stats
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Processed", stats.get('total_processed', 0))
    
    with col2:
        st.metric("Approved", stats.get('approved', 0))
    
    with col3:
        st.metric("Needs Revision", stats.get('revise', 0))
    
    with col4:
        st.metric("Human Reviews", stats.get('human_reviews', 0))
    
    # More detailed statistics
    st.markdown("### Detailed Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Escalated", stats.get('escalated', 0))
    
    with col2:
        st.metric("Rejected", stats.get('rejected', 0))
    
    # Session statistics
    st.markdown("### Session Statistics")
    st.info(f"Evaluations in current session: {len(st.session_state.evaluation_history)}")


def main():
    """Main application entry point"""
    init_session_state()
    
    # Render sidebar and get current page
    page = render_sidebar()
    
    # Route to appropriate page
    if page == "🏠 Home":
        render_home_page()
    elif page == "📝 Evaluate Complaint":
        render_evaluation_page()
    elif page == "📊 View Results":
        render_results_page()
    elif page == "⚙️ Settings":
        render_settings_page()
    elif page == "📈 Statistics":
        render_statistics_page()


if __name__ == "__main__":
    main()
