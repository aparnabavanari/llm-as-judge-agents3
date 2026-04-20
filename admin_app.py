"""
Admin UI for LLM Judge Agent Configuration Management
Streamlit application for managing business rules, evaluation profiles, and prompts
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from src.database.db_manager import DatabaseManager
from src.database.db_init import DatabaseInitializer

# Page configuration
st.set_page_config(
    page_title="LLM Judge Admin",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database manager
@st.cache_resource
def get_db_manager():
    """Get or create database manager instance"""
    return DatabaseManager()

db = get_db_manager()

# Sidebar navigation
st.sidebar.title("⚙️ Admin Panel")
page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📋 Complaint Types",
        "📜 Business Rules",
        "📊 Evaluation Profiles",
        "💬 Prompt Templates",
        "📖 Audit Log",
        "🔄 Database Management"
    ]
)

# ==================== Dashboard Page ====================
if page == "🏠 Dashboard":
    st.title("🏠 Configuration Dashboard")
    st.markdown("### System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        complaint_types = db.get_complaint_types(active_only=True)
        st.metric("Complaint Types", len(complaint_types))
    
    with col2:
        rules = db.get_business_rules(active_only=True)
        st.metric("Business Rules", len(rules))
    
    with col3:
        profiles = db.get_evaluation_profiles(active_only=True)
        st.metric("Evaluation Profiles", len(profiles))
    
    with col4:
        prompts = db.get_prompt_templates(active_only=True)
        st.metric("Prompt Templates", len(prompts))
    
    st.markdown("---")
    
    # Recent changes
    st.markdown("### 📝 Recent Changes")
    history = db.get_change_history(limit=10)
    if history:
        history_data = []
        for h in history:
            history_data.append({
                'Time': h.changed_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Table': h.table_name,
                'Record ID': h.record_id,
                'Action': h.action.upper(),
                'Changed By': h.changed_by
            })
        st.dataframe(pd.DataFrame(history_data), width='stretch')
    else:
        st.info("No recent changes")

# ==================== Complaint Types Page ====================
elif page == "📋 Complaint Types":
    st.title("📋 Complaint Type Management")
    
    tab1, tab2 = st.tabs(["View/Edit", "Create New"])
    
    with tab1:
        complaint_types = db.get_complaint_types(active_only=False)
        
        if complaint_types:
            # Display as table
            type_data = []
            for ct in complaint_types:
                type_data.append({
                    'Type ID': ct.type_id,
                    'Name': ct.name,
                    'Risk Level': ct.risk_level,
                    'Priority': ct.priority,
                    'Human Review': '✓' if ct.requires_human_review else '✗',
                    'Active': '✓' if ct.is_active else '✗'
                })
            
            st.dataframe(pd.DataFrame(type_data), width='stretch')
            
            # Edit section
            st.markdown("### Edit Complaint Type")
            selected_type = st.selectbox(
                "Select complaint type to edit",
                [ct.type_id for ct in complaint_types]
            )
            
            if selected_type:
                ct = next((c for c in complaint_types if c.type_id == selected_type), None)
                
                with st.form(f"edit_complaint_type_{selected_type}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        name = st.text_input("Name", value=ct.name)
                        risk_level = st.selectbox(
                            "Risk Level",
                            ["low", "medium", "high", "critical"],
                            index=["low", "medium", "high", "critical"].index(ct.risk_level)
                        )
                        priority = st.number_input("Priority", min_value=1, max_value=10, value=ct.priority)
                    
                    with col2:
                        description = st.text_area("Description", value=ct.description or "")
                        escalation_threshold = st.slider("Escalation Threshold", 0.0, 1.0, ct.escalation_threshold)
                        requires_review = st.checkbox("Requires Human Review", value=ct.requires_human_review)
                        is_active = st.checkbox("Active", value=ct.is_active)
                    
                    submitted = st.form_submit_button("Update")
                    
                    if submitted:
                        try:
                            db.update_complaint_type(selected_type, {
                                'name': name,
                                'description': description,
                                'risk_level': risk_level,
                                'priority': priority,
                                'escalation_threshold': escalation_threshold,
                                'requires_human_review': requires_review,
                                'is_active': is_active
                            })
                            st.success(f"✅ Updated complaint type: {selected_type}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
        else:
            st.info("No complaint types found")
    
    with tab2:
        st.markdown("### Create New Complaint Type")
        
        with st.form("create_complaint_type"):
            col1, col2 = st.columns(2)
            
            with col1:
                type_id = st.text_input("Type ID", placeholder="e.g., fraud_complaint")
                name = st.text_input("Name", placeholder="e.g., Fraud Complaint")
                risk_level = st.selectbox("Risk Level", ["low", "medium", "high", "critical"])
                priority = st.number_input("Priority", min_value=1, max_value=10, value=3)
            
            with col2:
                description = st.text_area("Description")
                escalation_threshold = st.slider("Escalation Threshold", 0.0, 1.0, 0.7)
                requires_review = st.checkbox("Requires Human Review", value=False)
            
            submitted = st.form_submit_button("Create")
            
            if submitted:
                if not type_id or not name:
                    st.error("Type ID and Name are required")
                else:
                    try:
                        db.create_complaint_type({
                            'type_id': type_id,
                            'name': name,
                            'description': description,
                            'risk_level': risk_level,
                            'priority': priority,
                            'escalation_threshold': escalation_threshold,
                            'requires_human_review': requires_review
                        })
                        st.success(f"✅ Created complaint type: {type_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# ==================== Business Rules Page ====================
elif page == "📜 Business Rules":
    st.title("📜 Business Rules Management")
    
    tab1, tab2 = st.tabs(["View/Edit", "Create New"])
    
    with tab1:
        rules = db.get_business_rules(active_only=False)
        
        if rules:
            # Display as table
            rule_data = []
            for rule in rules:
                rule_data.append({
                    'Rule ID': rule.rule_id,
                    'Name': rule.name,
                    'Complaint Type': rule.complaint_type.type_id if rule.complaint_type else 'All',
                    'Priority': rule.priority,
                    'Active': '✓' if rule.is_active else '✗'
                })
            
            st.dataframe(pd.DataFrame(rule_data), width='stretch')
            
            # Edit section
            st.markdown("### Edit Business Rule")
            selected_rule = st.selectbox(
                "Select rule to edit",
                [r.rule_id for r in rules]
            )
            
            if selected_rule:
                rule = next((r for r in rules if r.rule_id == selected_rule), None)
                
                with st.form(f"edit_rule_{selected_rule}"):
                    name = st.text_input("Name", value=rule.name)
                    description = st.text_area("Description", value=rule.description or "")
                    
                    complaint_types = db.get_complaint_types()
                    ct_options = ["None"] + [ct.type_id for ct in complaint_types]
                    ct_index = 0
                    if rule.complaint_type:
                        try:
                            ct_index = ct_options.index(rule.complaint_type.type_id)
                        except ValueError:
                            ct_index = 0
                    
                    complaint_type = st.selectbox("Complaint Type", ct_options, index=ct_index)
                    
                    condition = st.text_area("Condition", value=rule.condition)
                    action = st.text_input("Action", value=rule.action)
                    priority = st.number_input("Priority", min_value=1, max_value=10, value=rule.priority)
                    is_active = st.checkbox("Active", value=rule.is_active)
                    
                    submitted = st.form_submit_button("Update")
                    
                    if submitted:
                        try:
                            # Get complaint type ID
                            complaint_type_id = None
                            if complaint_type != "None":
                                ct = db.get_complaint_type(complaint_type)
                                if ct:
                                    complaint_type_id = ct.id
                            
                            db.update_business_rule(selected_rule, {
                                'name': name,
                                'description': description,
                                'complaint_type_id': complaint_type_id,
                                'condition': condition,
                                'action': action,
                                'priority': priority,
                                'is_active': is_active
                            })
                            st.success(f"✅ Updated rule: {selected_rule}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
        else:
            st.info("No business rules found")
    
    with tab2:
        st.markdown("### Create New Business Rule")
        
        with st.form("create_rule"):
            rule_id = st.text_input("Rule ID", placeholder="e.g., high_value_escalation")
            name = st.text_input("Name", placeholder="e.g., High Value Transaction Escalation")
            description = st.text_area("Description")
            
            complaint_types = db.get_complaint_types()
            ct_options = ["None"] + [ct.type_id for ct in complaint_types]
            complaint_type = st.selectbox("Complaint Type", ct_options)
            
            condition = st.text_area("Condition", placeholder="e.g., amount > 10000")
            action = st.text_input("Action", placeholder="e.g., escalate_to_manager")
            priority = st.number_input("Priority", min_value=1, max_value=10, value=5)
            
            submitted = st.form_submit_button("Create")
            
            if submitted:
                if not rule_id or not name or not condition or not action:
                    st.error("Rule ID, Name, Condition, and Action are required")
                else:
                    try:
                        # Get complaint type ID
                        complaint_type_id = None
                        if complaint_type != "None":
                            ct = db.get_complaint_type(complaint_type)
                            if ct:
                                complaint_type_id = ct.id
                        
                        db.create_business_rule({
                            'rule_id': rule_id,
                            'name': name,
                            'description': description,
                            'complaint_type_id': complaint_type_id,
                            'condition': condition,
                            'action': action,
                            'priority': priority
                        })
                        st.success(f"✅ Created rule: {rule_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# ==================== Evaluation Profiles Page ====================
elif page == "📊 Evaluation Profiles":
    st.title("📊 Evaluation Profile Management")
    
    profiles = db.get_evaluation_profiles(active_only=False)
    
    if profiles:
        # Select profile
        profile_names = [f"{p.complaint_type.type_id} - {p.name}" for p in profiles]
        selected_profile = st.selectbox("Select Profile", profile_names)
        
        if selected_profile:
            profile = profiles[profile_names.index(selected_profile)]
            
            st.markdown(f"### {profile.name}")
            st.write(f"**Complaint Type:** {profile.complaint_type.name}")
            st.write(f"**Description:** {profile.description}")
            
            st.markdown("#### Metrics")
            
            if profile.metrics:
                metric_data = []
                for m in sorted(profile.metrics, key=lambda x: x.display_order):
                    if m.is_active:
                        metric_data.append({
                            'Metric ID': m.metric_id,
                            'Name': m.name,
                            'Weight': m.weight,
                            'Scale': m.scale,
                            'Order': m.display_order
                        })
                
                st.dataframe(pd.DataFrame(metric_data), width='stretch')
                
                # Edit metric
                st.markdown("##### Edit Metric")
                metric_options = [m.metric_id for m in profile.metrics if m.is_active]
                selected_metric = st.selectbox("Select metric to edit", metric_options)
                
                if selected_metric:
                    metric = next((m for m in profile.metrics if m.metric_id == selected_metric), None)
                    
                    with st.form(f"edit_metric_{metric.id}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            name = st.text_input("Name", value=metric.name)
                            weight = st.number_input("Weight", min_value=0.0, max_value=1.0, value=metric.weight, step=0.1)
                        
                        with col2:
                            description = st.text_area("Description", value=metric.description or "")
                            display_order = st.number_input("Display Order", min_value=0, value=metric.display_order)
                        
                        scale = st.text_input("Scale", value=metric.scale)
                        is_active = st.checkbox("Active", value=metric.is_active)
                        
                        submitted = st.form_submit_button("Update")
                        
                        if submitted:
                            try:
                                db.update_evaluation_metric(metric.id, {
                                    'name': name,
                                    'description': description,
                                    'weight': weight,
                                    'scale': scale,
                                    'display_order': display_order,
                                    'is_active': is_active
                                })
                                st.success(f"✅ Updated metric: {selected_metric}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
            else:
                st.info("No metrics found for this profile")
    else:
        st.info("No evaluation profiles found")

# ==================== Prompt Templates Page ====================
elif page == "💬 Prompt Templates":
    st.title("💬 Prompt Template Management")
    
    tab1, tab2 = st.tabs(["View/Edit", "Create New"])
    
    with tab1:
        prompts = db.get_prompt_templates(active_only=False)
        
        if prompts:
            # Group by agent
            agents = list(set(p.agent_name for p in prompts))
            selected_agent = st.selectbox("Select Agent", agents)
            
            if selected_agent:
                agent_prompts = [p for p in prompts if p.agent_name == selected_agent]
                
                for prompt in agent_prompts:
                    with st.expander(f"{prompt.prompt_type} (v{prompt.version}) {'✓' if prompt.is_active else '✗'}"):
                        st.write(f"**Description:** {prompt.description}")
                        
                        with st.form(f"edit_prompt_{prompt.id}"):
                            description = st.text_input("Description", value=prompt.description or "")
                            content = st.text_area("Content", value=prompt.content, height=300)
                            version = st.text_input("Version", value=prompt.version)
                            is_active = st.checkbox("Active", value=prompt.is_active)
                            
                            submitted = st.form_submit_button("Update")
                            
                            if submitted:
                                try:
                                    db.update_prompt_template(prompt.id, {
                                        'description': description,
                                        'content': content,
                                        'version': version,
                                        'is_active': is_active
                                    })
                                    st.success(f"✅ Updated prompt: {prompt.agent_name}.{prompt.prompt_type}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
        else:
            st.info("No prompt templates found")
    
    with tab2:
        st.markdown("### Create New Prompt Template")
        
        with st.form("create_prompt"):
            agent_name = st.text_input("Agent Name", placeholder="e.g., complaint_classifier")
            prompt_type = st.text_input("Prompt Type", placeholder="e.g., system_prompt")
            description = st.text_input("Description")
            content = st.text_area("Content", height=300)
            version = st.text_input("Version", value="1.0")
            
            submitted = st.form_submit_button("Create")
            
            if submitted:
                if not agent_name or not prompt_type or not content:
                    st.error("Agent Name, Prompt Type, and Content are required")
                else:
                    try:
                        db.create_prompt_template({
                            'agent_name': agent_name,
                            'prompt_type': prompt_type,
                            'description': description,
                            'content': content,
                            'version': version
                        })
                        st.success(f"✅ Created prompt: {agent_name}.{prompt_type}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# ==================== Audit Log Page ====================
elif page == "📖 Audit Log":
    st.title("📖 Configuration Audit Log")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        table_filter = st.selectbox(
            "Filter by Table",
            ["All", "complaint_types", "business_rules", "evaluation_profiles", "evaluation_metrics", "prompt_templates"]
        )
    with col2:
        limit = st.number_input("Number of records", min_value=10, max_value=1000, value=50)
    
    # Get history
    if table_filter == "All":
        history = db.get_change_history(limit=limit)
    else:
        history = db.get_change_history(table_name=table_filter, limit=limit)
    
    if history:
        history_data = []
        for h in history:
            history_data.append({
                'Time': h.changed_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Table': h.table_name,
                'Record ID': h.record_id,
                'Action': h.action.upper(),
                'Changed By': h.changed_by
            })
        
        st.dataframe(pd.DataFrame(history_data), width='stretch')
        
        # Detail view
        if st.checkbox("Show detailed changes"):
            selected_idx = st.number_input("Select row (0-based index)", min_value=0, max_value=len(history)-1, value=0)
            if 0 <= selected_idx < len(history):
                h = history[selected_idx]
                st.markdown("### Change Details")
                st.write(f"**Table:** {h.table_name}")
                st.write(f"**Record ID:** {h.record_id}")
                st.write(f"**Action:** {h.action.upper()}")
                st.write(f"**Time:** {h.changed_at}")
                st.write(f"**Changed By:** {h.changed_by}")
                
                if h.old_value:
                    st.markdown("**Old Value:**")
                    st.json(h.old_value)
                
                if h.new_value:
                    st.markdown("**New Value:**")
                    st.json(h.new_value)
    else:
        st.info("No audit log entries found")

# ==================== Database Management Page ====================
elif page == "🔄 Database Management":
    st.title("🔄 Database Management")
    
    st.markdown("### Import from YAML")
    st.info("Import configurations from YAML files into the database")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        force_reimport = st.checkbox("Force Reimport (clears existing data)", value=False)
    
    with col2:
        if st.button("Import from YAML"):
            with st.spinner("Importing configurations..."):
                try:
                    initializer = DatabaseInitializer(config_dir="./config")
                    initializer.initialize(force_reimport=force_reimport)
                    st.success("✅ Import completed successfully!")
                except Exception as e:
                    st.error(f"❌ Import failed: {e}")
    
    st.markdown("---")
    
    st.markdown("### Database Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Database Path", db.db_path)
    
    with col2:
        import os
        if os.path.exists(db.db_path):
            size = os.path.getsize(db.db_path)
            st.metric("Database Size", f"{size / 1024:.2f} KB")
    
    st.markdown("---")
    
    st.markdown("### Export Configuration")
    st.info("Export current database configuration to YAML format")
    
    if st.button("Export to YAML"):
        st.warning("Export functionality not yet implemented")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "**LLM Judge Admin Panel**\n\n"
    "Manage dynamic configurations for the LLM Judge Agent System"
)
