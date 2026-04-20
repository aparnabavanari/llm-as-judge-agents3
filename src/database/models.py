"""
SQLAlchemy models for dynamic configuration management
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class ComplaintType(Base):
    """Complaint type configuration"""
    __tablename__ = 'complaint_types'
    
    id = Column(Integer, primary_key=True)
    type_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    priority = Column(Integer, default=3)
    escalation_threshold = Column(Float, default=0.7)
    requires_human_review = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    evaluation_profiles = relationship("EvaluationProfile", back_populates="complaint_type", cascade="all, delete-orphan")
    business_rules = relationship("BusinessRule", back_populates="complaint_type", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'type_id': self.type_id,
            'name': self.name,
            'description': self.description,
            'risk_level': self.risk_level,
            'priority': self.priority,
            'escalation_threshold': self.escalation_threshold,
            'requires_human_review': self.requires_human_review,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class BusinessRule(Base):
    """Business rule configuration"""
    __tablename__ = 'business_rules'
    
    id = Column(Integer, primary_key=True)
    rule_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    complaint_type_id = Column(Integer, ForeignKey('complaint_types.id'), nullable=True)
    condition = Column(Text, nullable=False)
    action = Column(String(100), nullable=False)
    priority = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    complaint_type = relationship("ComplaintType", back_populates="business_rules")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            'complaint_type_id': self.complaint_type_id,
            'condition': self.condition,
            'action': self.action,
            'priority': self.priority,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EvaluationProfile(Base):
    """Evaluation profile (collection of metrics for a complaint type)"""
    __tablename__ = 'evaluation_profiles'
    
    id = Column(Integer, primary_key=True)
    complaint_type_id = Column(Integer, ForeignKey('complaint_types.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    complaint_type = relationship("ComplaintType", back_populates="evaluation_profiles")
    metrics = relationship("EvaluationMetric", back_populates="profile", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'complaint_type_id': self.complaint_type_id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'metrics': [m.to_dict() for m in self.metrics],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EvaluationMetric(Base):
    """Individual evaluation metric"""
    __tablename__ = 'evaluation_metrics'
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('evaluation_profiles.id'), nullable=False)
    metric_id = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    weight = Column(Float, nullable=False)
    scale = Column(String(20), default='1-5')
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    profile = relationship("EvaluationProfile", back_populates="metrics")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'metric_id': self.metric_id,
            'name': self.name,
            'description': self.description,
            'weight': self.weight,
            'scale': self.scale,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PromptTemplate(Base):
    """LLM prompt templates"""
    __tablename__ = 'prompt_templates'
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(100), nullable=False)  # e.g., 'complaint_classifier'
    prompt_type = Column(String(50), nullable=False)  # e.g., 'system_prompt', 'user_prompt_template'
    content = Column(Text, nullable=False)
    description = Column(Text)
    version = Column(String(20), default='1.0')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'agent_name': self.agent_name,
            'prompt_type': self.prompt_type,
            'content': self.content,
            'description': self.description,
            'version': self.version,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ConfigurationHistory(Base):
    """Audit log for configuration changes"""
    __tablename__ = 'configuration_history'
    
    id = Column(Integer, primary_key=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(String(20), nullable=False)  # create, update, delete
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(String(100), default='admin')
    changed_at = Column(DateTime, default=datetime.now)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'action': self.action,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'changed_by': self.changed_by,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None
        }
