"""
Database manager for configuration management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

from src.database.models import (
    Base, ComplaintType, BusinessRule, EvaluationProfile,
    EvaluationMetric, PromptTemplate, ConfigurationHistory
)


class DatabaseManager:
    """Manages database connection and operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = Path("./config/llm_judge.db")
        else:
            db_path = Path(db_path)
        
        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create engine
        self.db_path = str(db_path)
        self.engine = create_engine(
            f'sqlite:///{self.db_path}',
            echo=False,
            connect_args={'check_same_thread': False}
        )
        
        # Create session factory
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    def close_session(self, session):
        """Close a database session"""
        session.close()
    
    # ==================== Complaint Type Operations ====================
    
    def get_complaint_types(self, active_only: bool = True) -> List[ComplaintType]:
        """Get all complaint types"""
        session = self.get_session()
        try:
            query = session.query(ComplaintType)
            if active_only:
                query = query.filter(ComplaintType.is_active == True)
            return query.all()
        finally:
            self.close_session(session)
    
    def get_complaint_type(self, type_id: str) -> Optional[ComplaintType]:
        """Get complaint type by type_id"""
        session = self.get_session()
        try:
            return session.query(ComplaintType).filter(
                ComplaintType.type_id == type_id,
                ComplaintType.is_active == True
            ).first()
        finally:
            self.close_session(session)
    
    def create_complaint_type(self, data: Dict[str, Any]) -> ComplaintType:
        """Create new complaint type"""
        session = self.get_session()
        try:
            complaint_type = ComplaintType(**data)
            session.add(complaint_type)
            session.commit()
            session.refresh(complaint_type)
            
            # Log change
            self._log_change(session, 'complaint_types', complaint_type.id, 'create', None, complaint_type.to_dict())
            session.commit()
            
            return complaint_type
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    def update_complaint_type(self, type_id: str, data: Dict[str, Any]) -> ComplaintType:
        """Update complaint type"""
        session = self.get_session()
        try:
            complaint_type = session.query(ComplaintType).filter(
                ComplaintType.type_id == type_id
            ).first()
            
            if not complaint_type:
                raise ValueError(f"Complaint type '{type_id}' not found")
            
            old_value = complaint_type.to_dict()
            
            for key, value in data.items():
                if hasattr(complaint_type, key):
                    setattr(complaint_type, key, value)
            
            complaint_type.updated_at = datetime.now()
            session.commit()
            session.refresh(complaint_type)
            
            # Log change
            self._log_change(session, 'complaint_types', complaint_type.id, 'update', old_value, complaint_type.to_dict())
            session.commit()
            
            return complaint_type
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    def delete_complaint_type(self, type_id: str):
        """Soft delete complaint type"""
        session = self.get_session()
        try:
            complaint_type = session.query(ComplaintType).filter(
                ComplaintType.type_id == type_id
            ).first()
            
            if not complaint_type:
                raise ValueError(f"Complaint type '{type_id}' not found")
            
            old_value = complaint_type.to_dict()
            complaint_type.is_active = False
            complaint_type.updated_at = datetime.now()
            session.commit()
            
            # Log change
            self._log_change(session, 'complaint_types', complaint_type.id, 'delete', old_value, None)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    # ==================== Business Rule Operations ====================
    
    def get_business_rules(self, active_only: bool = True) -> List[BusinessRule]:
        """Get all business rules"""
        session = self.get_session()
        try:
            query = session.query(BusinessRule).options(joinedload(BusinessRule.complaint_type))
            if active_only:
                query = query.filter(BusinessRule.is_active == True)
            return query.order_by(BusinessRule.priority).all()
        finally:
            self.close_session(session)
    
    def create_business_rule(self, data: Dict[str, Any]) -> BusinessRule:
        """Create new business rule"""
        session = self.get_session()
        try:
            rule = BusinessRule(**data)
            session.add(rule)
            session.commit()
            session.refresh(rule)
            
            # Log change
            self._log_change(session, 'business_rules', rule.id, 'create', None, rule.to_dict())
            session.commit()
            
            return rule
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    def update_business_rule(self, rule_id: str, data: Dict[str, Any]) -> BusinessRule:
        """Update business rule"""
        session = self.get_session()
        try:
            rule = session.query(BusinessRule).filter(BusinessRule.rule_id == rule_id).first()
            
            if not rule:
                raise ValueError(f"Business rule '{rule_id}' not found")
            
            old_value = rule.to_dict()
            
            for key, value in data.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            rule.updated_at = datetime.now()
            session.commit()
            session.refresh(rule)
            
            # Log change
            self._log_change(session, 'business_rules', rule.id, 'update', old_value, rule.to_dict())
            session.commit()
            
            return rule
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    def delete_business_rule(self, rule_id: str):
        """Soft delete business rule"""
        session = self.get_session()
        try:
            rule = session.query(BusinessRule).filter(BusinessRule.rule_id == rule_id).first()
            
            if not rule:
                raise ValueError(f"Business rule '{rule_id}' not found")
            
            old_value = rule.to_dict()
            rule.is_active = False
            rule.updated_at = datetime.now()
            session.commit()
            
            # Log change
            self._log_change(session, 'business_rules', rule.id, 'delete', old_value, None)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    # ==================== Evaluation Profile Operations ====================
    
    def get_evaluation_profiles(self, complaint_type_id: Optional[int] = None, active_only: bool = True) -> List[EvaluationProfile]:
        """Get evaluation profiles"""
        session = self.get_session()
        try:
            query = session.query(EvaluationProfile).options(
                joinedload(EvaluationProfile.complaint_type),
                joinedload(EvaluationProfile.metrics)
            )
            if complaint_type_id:
                query = query.filter(EvaluationProfile.complaint_type_id == complaint_type_id)
            if active_only:
                query = query.filter(EvaluationProfile.is_active == True)
            return query.all()
        finally:
            self.close_session(session)
    
    def get_profile_by_complaint_type(self, type_id: str) -> Optional[EvaluationProfile]:
        """Get evaluation profile for a complaint type"""
        session = self.get_session()
        try:
            complaint_type = session.query(ComplaintType).filter(
                ComplaintType.type_id == type_id
            ).first()
            
            if not complaint_type:
                return None
            
            return session.query(EvaluationProfile).filter(
                EvaluationProfile.complaint_type_id == complaint_type.id,
                EvaluationProfile.is_active == True
            ).first()
        finally:
            self.close_session(session)
    
    def create_evaluation_profile(self, data: Dict[str, Any], metrics: List[Dict[str, Any]]) -> EvaluationProfile:
        """Create new evaluation profile with metrics"""
        session = self.get_session()
        try:
            profile = EvaluationProfile(**data)
            session.add(profile)
            session.flush()  # Get the profile ID
            
            # Add metrics
            for metric_data in metrics:
                metric = EvaluationMetric(profile_id=profile.id, **metric_data)
                session.add(metric)
            
            session.commit()
            session.refresh(profile)
            
            # Log change
            self._log_change(session, 'evaluation_profiles', profile.id, 'create', None, profile.to_dict())
            session.commit()
            
            return profile
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    # ==================== Evaluation Metric Operations ====================
    
    def create_evaluation_metric(self, data: Dict[str, Any]) -> EvaluationMetric:
        """Create new evaluation metric"""
        session = self.get_session()
        try:
            metric = EvaluationMetric(**data)
            session.add(metric)
            session.commit()
            session.refresh(metric)
            
            # Log change
            self._log_change(session, 'evaluation_metrics', metric.id, 'create', None, metric.to_dict())
            session.commit()
            
            return metric
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    def update_evaluation_metric(self, metric_id: int, data: Dict[str, Any]) -> EvaluationMetric:
        """Update evaluation metric"""
        session = self.get_session()
        try:
            metric = session.query(EvaluationMetric).filter(EvaluationMetric.id == metric_id).first()
            
            if not metric:
                raise ValueError(f"Metric ID '{metric_id}' not found")
            
            old_value = metric.to_dict()
            
            for key, value in data.items():
                if hasattr(metric, key):
                    setattr(metric, key, value)
            
            metric.updated_at = datetime.now()
            session.commit()
            session.refresh(metric)
            
            # Log change
            self._log_change(session, 'evaluation_metrics', metric.id, 'update', old_value, metric.to_dict())
            session.commit()
            
            return metric
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    def delete_evaluation_metric(self, metric_id: int):
        """Soft delete evaluation metric"""
        session = self.get_session()
        try:
            metric = session.query(EvaluationMetric).filter(EvaluationMetric.id == metric_id).first()
            
            if not metric:
                raise ValueError(f"Metric ID '{metric_id}' not found")
            
            old_value = metric.to_dict()
            metric.is_active = False
            metric.updated_at = datetime.now()
            session.commit()
            
            # Log change
            self._log_change(session, 'evaluation_metrics', metric.id, 'delete', old_value, None)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    # ==================== Prompt Template Operations ====================
    
    def get_prompt_templates(self, agent_name: Optional[str] = None, active_only: bool = True) -> List[PromptTemplate]:
        """Get prompt templates"""
        session = self.get_session()
        try:
            query = session.query(PromptTemplate)
            if agent_name:
                query = query.filter(PromptTemplate.agent_name == agent_name)
            if active_only:
                query = query.filter(PromptTemplate.is_active == True)
            return query.all()
        finally:
            self.close_session(session)
    
    def get_prompt_template(self, agent_name: str, prompt_type: str) -> Optional[PromptTemplate]:
        """Get specific prompt template"""
        session = self.get_session()
        try:
            return session.query(PromptTemplate).filter(
                PromptTemplate.agent_name == agent_name,
                PromptTemplate.prompt_type == prompt_type,
                PromptTemplate.is_active == True
            ).first()
        finally:
            self.close_session(session)
    
    def create_prompt_template(self, data: Dict[str, Any]) -> PromptTemplate:
        """Create new prompt template"""
        session = self.get_session()
        try:
            prompt = PromptTemplate(**data)
            session.add(prompt)
            session.commit()
            session.refresh(prompt)
            
            # Log change
            self._log_change(session, 'prompt_templates', prompt.id, 'create', None, prompt.to_dict())
            session.commit()
            
            return prompt
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    def update_prompt_template(self, template_id: int, data: Dict[str, Any]) -> PromptTemplate:
        """Update prompt template"""
        session = self.get_session()
        try:
            prompt = session.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
            
            if not prompt:
                raise ValueError(f"Prompt template ID '{template_id}' not found")
            
            old_value = prompt.to_dict()
            
            for key, value in data.items():
                if hasattr(prompt, key):
                    setattr(prompt, key, value)
            
            prompt.updated_at = datetime.now()
            session.commit()
            session.refresh(prompt)
            
            # Log change
            self._log_change(session, 'prompt_templates', prompt.id, 'update', old_value, prompt.to_dict())
            session.commit()
            
            return prompt
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    # ==================== Audit Log ====================
    
    def _log_change(self, session, table_name: str, record_id: int, action: str, 
                   old_value: Optional[Dict], new_value: Optional[Dict]):
        """Log configuration change"""
        history = ConfigurationHistory(
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_value=json.dumps(old_value) if old_value else None,
            new_value=json.dumps(new_value) if new_value else None
        )
        session.add(history)
    
    def get_change_history(self, table_name: Optional[str] = None, limit: int = 100) -> List[ConfigurationHistory]:
        """Get configuration change history"""
        session = self.get_session()
        try:
            query = session.query(ConfigurationHistory)
            if table_name:
                query = query.filter(ConfigurationHistory.table_name == table_name)
            return query.order_by(ConfigurationHistory.changed_at.desc()).limit(limit).all()
        finally:
            self.close_session(session)
