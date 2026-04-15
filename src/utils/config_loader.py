"""
Configuration loader utility
Loads and manages YAML configuration files
"""
import yaml
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class ConfigLoader:
    """Loads and manages configuration from YAML files"""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize configuration loader
        
        Args:
            config_dir: Path to configuration directory
        """
        if config_dir is None:
            # Default to config directory relative to project root
            current_dir = Path(__file__).parent.parent.parent
            config_dir = current_dir / "config"
        
        self.config_dir = Path(config_dir)
        self._business_rules = None
        self._evaluation_profiles = None
        self._prompts = None
        
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file
        
        Args:
            filename: Name of the YAML file
            
        Returns:
            Parsed YAML content as dictionary
        """
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_business_rules(self) -> Dict[str, Any]:
        """Get business rules configuration"""
        if self._business_rules is None:
            self._business_rules = self.load_yaml('business_rules.yaml')
        return self._business_rules
    
    def get_evaluation_profiles(self) -> Dict[str, Any]:
        """Get evaluation profiles configuration"""
        if self._evaluation_profiles is None:
            self._evaluation_profiles = self.load_yaml('evaluation_profiles.yaml')
        return self._evaluation_profiles
    
    def get_prompts(self) -> Dict[str, Any]:
        """Get prompts configuration"""
        if self._prompts is None:
            self._prompts = self.load_yaml('prompts.yaml')
        return self._prompts
    
    def get_complaint_type_config(self, complaint_type: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific complaint type
        
        Args:
            complaint_type: Type of complaint
            
        Returns:
            Configuration dictionary for the complaint type
        """
        rules = self.get_business_rules()
        return rules.get('complaint_types', {}).get(complaint_type)
    
    def get_metrics_for_complaint_type(self, complaint_type: str) -> List[Dict[str, Any]]:
        """
        Get evaluation metrics for a specific complaint type
        
        Args:
            complaint_type: Type of complaint
            
        Returns:
            List of metric configurations
        """
        profiles = self.get_evaluation_profiles()
        
        # Get complaint-specific metrics or fall back to default
        complaint_profile = profiles.get('evaluation_profiles', {}).get(complaint_type)
        
        if complaint_profile:
            return complaint_profile.get('metrics', [])
        
        # Fallback to default profile
        default_profile = profiles.get('default_profile', {})
        return default_profile.get('metrics', [])
    
    def get_risk_level_config(self, risk_level: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific risk level
        
        Args:
            risk_level: Risk level (critical, high, medium, low)
            
        Returns:
            Risk level configuration
        """
        rules = self.get_business_rules()
        return rules.get('risk_levels', {}).get(risk_level)
    
    def get_prompt_template(self, agent_name: str, prompt_type: str = 'system_prompt') -> str:
        """
        Get prompt template for a specific agent
        
        Args:
            agent_name: Name of the agent
            prompt_type: Type of prompt (system_prompt, user_prompt_template)
            
        Returns:
            Prompt template string
        """
        prompts = self.get_prompts()
        agent_prompts = prompts.get('prompts', {}).get(agent_name, {})
        return agent_prompts.get(prompt_type, '')
    
    def get_business_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific business rule by ID
        
        Args:
            rule_id: Business rule identifier
            
        Returns:
            Business rule configuration
        """
        rules = self.get_business_rules()
        business_rules = rules.get('business_rules', [])
        
        for rule in business_rules:
            if rule.get('rule_id') == rule_id:
                return rule
        
        return None
    
    def get_all_complaint_types(self) -> List[str]:
        """
        Get list of all configured complaint types
        
        Returns:
            List of complaint type identifiers
        """
        rules = self.get_business_rules()
        return list(rules.get('complaint_types', {}).keys())
    
    def get_threshold(self, threshold_name: str) -> Optional[float]:
        """
        Get a specific threshold value
        
        Args:
            threshold_name: Name of the threshold
            
        Returns:
            Threshold value
        """
        rules = self.get_business_rules()
        return rules.get('thresholds', {}).get(threshold_name)
    
    def reload_configurations(self):
        """Reload all configuration files (useful for dynamic updates)"""
        self._business_rules = None
        self._evaluation_profiles = None
        self._prompts = None
    
    def validate_configurations(self) -> Dict[str, bool]:
        """
        Validate all configuration files
        
        Returns:
            Dictionary with validation results for each config file
        """
        results = {}
        
        try:
            self.get_business_rules()
            results['business_rules'] = True
        except Exception as e:
            results['business_rules'] = False
            print(f"Business rules validation failed: {e}")
        
        try:
            self.get_evaluation_profiles()
            results['evaluation_profiles'] = True
        except Exception as e:
            results['evaluation_profiles'] = False
            print(f"Evaluation profiles validation failed: {e}")
        
        try:
            self.get_prompts()
            results['prompts'] = True
        except Exception as e:
            results['prompts'] = False
            print(f"Prompts validation failed: {e}")
        
        return results
    
    def validate_metric_weights(self, complaint_type: str) -> bool:
        """
        Validate that metric weights for a complaint type sum to 1.0
        
        Args:
            complaint_type: Type of complaint
            
        Returns:
            True if weights are valid, False otherwise
        """
        metrics = self.get_metrics_for_complaint_type(complaint_type)
        total_weight = sum(metric.get('weight', 0) for metric in metrics)
        
        # Allow small tolerance for floating point arithmetic
        tolerance = self.get_threshold('metric_weight_tolerance') or 0.05
        return abs(total_weight - 1.0) <= tolerance


# Singleton instance
_config_loader_instance = None


def get_config_loader(config_dir: str = None) -> ConfigLoader:
    """
    Get singleton ConfigLoader instance
    
    Args:
        config_dir: Path to configuration directory
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader_instance
    
    if _config_loader_instance is None:
        _config_loader_instance = ConfigLoader(config_dir)
    
    return _config_loader_instance
