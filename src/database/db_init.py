"""
Database initialization and YAML migration script
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml
from typing import Dict, Any
from src.database.db_manager import DatabaseManager
from src.database.models import ComplaintType, BusinessRule, EvaluationProfile, EvaluationMetric, PromptTemplate


class DatabaseInitializer:
    """Initialize database and migrate YAML configurations"""
    
    def __init__(self, config_dir: str = "./config", db_path: str = None):
        """
        Initialize database initializer
        
        Args:
            config_dir: Path to YAML configuration directory
            db_path: Path to SQLite database
        """
        self.config_dir = Path(config_dir)
        self.db = DatabaseManager(db_path)
    
    def initialize(self, force_reimport: bool = False):
        """
        Initialize database and import YAML configs
        
        Args:
            force_reimport: If True, clear existing data and reimport
        """
        print("Initializing database...")
        
        if force_reimport:
            print("WARNING: Force reimport will clear existing data!")
            self._clear_database()
        
        # Check if data already exists
        existing_types = self.db.get_complaint_types(active_only=False)
        if existing_types and not force_reimport:
            print(f"Database already contains {len(existing_types)} complaint types. Skipping import.")
            print("Use force_reimport=True to clear and reimport.")
            return
        
        # Import YAML configurations
        self._import_business_rules()
        self._import_evaluation_profiles()
        self._import_prompts()
        
        print("Database initialization complete!")
    
    def _clear_database(self):
        """Clear all data from database"""
        session = self.db.get_session()
        try:
            session.query(EvaluationMetric).delete()
            session.query(EvaluationProfile).delete()
            session.query(BusinessRule).delete()
            session.query(ComplaintType).delete()
            session.query(PromptTemplate).delete()
            session.commit()
            print("Database cleared.")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    def _import_business_rules(self):
        """Import business rules from YAML"""
        yaml_file = self.config_dir / "business_rules.yaml"
        
        if not yaml_file.exists():
            print(f"Warning: {yaml_file} not found. Skipping business rules import.")
            return
        
        print(f"Importing business rules from {yaml_file}...")
        
        with open(yaml_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Import complaint types
        complaint_types = config.get('complaint_types', {})
        for type_id, type_config in complaint_types.items():
            try:
                self.db.create_complaint_type({
                    'type_id': type_id,
                    'name': type_config.get('name', type_id.replace('_', ' ').title()),
                    'description': type_config.get('description', ''),
                    'risk_level': type_config.get('risk_level', 'medium'),
                    'priority': type_config.get('priority', 3),
                    'escalation_threshold': type_config.get('escalation_threshold', 0.7),
                    'requires_human_review': type_config.get('requires_human_review', False)
                })
                print(f"  ✓ Created complaint type: {type_id}")
            except Exception as e:
                print(f"  ✗ Error creating complaint type {type_id}: {e}")
        
        # Import business rules
        rules = config.get('business_rules', [])
        for rule in rules:
            try:
                # Find complaint type ID if specified
                complaint_type_id = None
                if 'complaint_type' in rule:
                    ct = self.db.get_complaint_type(rule['complaint_type'])
                    if ct:
                        complaint_type_id = ct.id
                
                self.db.create_business_rule({
                    'rule_id': rule.get('rule_id'),
                    'name': rule.get('name'),
                    'description': rule.get('description', ''),
                    'complaint_type_id': complaint_type_id,
                    'condition': rule.get('condition'),
                    'action': rule.get('action'),
                    'priority': rule.get('priority', 5)
                })
                print(f"  ✓ Created business rule: {rule.get('rule_id')}")
            except Exception as e:
                print(f"  ✗ Error creating business rule {rule.get('rule_id')}: {e}")
    
    def _import_evaluation_profiles(self):
        """Import evaluation profiles from YAML"""
        yaml_file = self.config_dir / "evaluation_profiles.yaml"
        
        if not yaml_file.exists():
            print(f"Warning: {yaml_file} not found. Skipping evaluation profiles import.")
            return
        
        print(f"Importing evaluation profiles from {yaml_file}...")
        
        with open(yaml_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        profiles = config.get('evaluation_profiles', {})
        for type_id, profile_config in profiles.items():
            try:
                # Get complaint type
                complaint_type = self.db.get_complaint_type(type_id)
                if not complaint_type:
                    print(f"  ✗ Complaint type '{type_id}' not found. Skipping profile.")
                    continue
                
                # Prepare metrics
                metrics = []
                for metric in profile_config.get('metrics', []):
                    metrics.append({
                        'metric_id': metric.get('metric_id'),
                        'name': metric.get('name'),
                        'description': metric.get('description', ''),
                        'weight': metric.get('weight', 0.2),
                        'scale': metric.get('scale', '1-5'),
                        'display_order': metric.get('display_order', 0)
                    })
                
                # Create profile with metrics
                self.db.create_evaluation_profile(
                    data={
                        'complaint_type_id': complaint_type.id,
                        'name': f"{complaint_type.name} Evaluation Profile",
                        'description': profile_config.get('description', '')
                    },
                    metrics=metrics
                )
                print(f"  ✓ Created evaluation profile for: {type_id} ({len(metrics)} metrics)")
            except Exception as e:
                print(f"  ✗ Error creating evaluation profile for {type_id}: {e}")
    
    def _import_prompts(self):
        """Import prompt templates from YAML"""
        yaml_file = self.config_dir / "prompts.yaml"
        
        if not yaml_file.exists():
            print(f"Warning: {yaml_file} not found. Skipping prompts import.")
            return
        
        print(f"Importing prompts from {yaml_file}...")
        
        with open(yaml_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        prompts = config.get('prompts', {})
        for agent_name, agent_prompts in prompts.items():
            for prompt_type, content in agent_prompts.items():
                try:
                    self.db.create_prompt_template({
                        'agent_name': agent_name,
                        'prompt_type': prompt_type,
                        'content': content,
                        'description': f"{agent_name} - {prompt_type}"
                    })
                    print(f"  ✓ Created prompt: {agent_name}.{prompt_type}")
                except Exception as e:
                    print(f"  ✗ Error creating prompt {agent_name}.{prompt_type}: {e}")


def initialize_database(config_dir: str = "./config", db_path: str = None, force_reimport: bool = False):
    """
    Convenience function to initialize database
    
    Args:
        config_dir: Path to YAML configuration directory
        db_path: Path to SQLite database
        force_reimport: If True, clear existing data and reimport
    """
    initializer = DatabaseInitializer(config_dir, db_path)
    initializer.initialize(force_reimport)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize LLM Judge Agent database")
    parser.add_argument('--config-dir', default='./config', help='Path to YAML config directory')
    parser.add_argument('--db-path', default=None, help='Path to SQLite database')
    parser.add_argument('--force', action='store_true', help='Force reimport (clears existing data)')
    
    args = parser.parse_args()
    
    initialize_database(args.config_dir, args.db_path, args.force)
