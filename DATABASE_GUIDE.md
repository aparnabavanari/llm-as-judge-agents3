# Dynamic Configuration Management Guide

## Overview

The LLM Judge Agent System now features **dynamic configuration management** powered by SQLite database. This allows administrators to modify business rules, evaluation profiles, and prompt templates at runtime without code changes or redeployment.

## Architecture

### Database Backend

- **Technology**: SQLite database with SQLAlchemy ORM
- **Location**: `config/llm_judge.db`
- **Schema**: Normalized relational design with audit logging
- **Migrations**: Managed by Alembic

### Configuration Types

1. **Complaint Types**
   - Define different categories of complaints (fraud, billing, etc.)
   - Set risk levels, priorities, and escalation thresholds
   - Control human review requirements

2. **Business Rules**
   - Conditional logic for complaint processing
   - Priority-based execution
   - Optional complaint type association

3. **Evaluation Profiles**
   - Metric collections for each complaint type
   - Weighted scoring system
   - Customizable evaluation criteria

4. **Prompt Templates**
   - LLM prompts for each agent
   - Versioned prompt management
   - Easy testing and rollback

## Quick Start

### 1. Initialize Database

Run the database initialization script to migrate existing YAML configurations:

```bash
# PowerShell
python src\database\db_init.py --config-dir ./config

# Or force reimport (clears existing data)
python src\database\db_init.py --force
```

### 2. Launch Admin UI

```bash
# Windows Batch
launch_admin.bat

# Or PowerShell
.\launch_admin.ps1

# Or directly
streamlit run admin_app.py --server.port=8502
```

The admin panel will open at `http://localhost:8502`

### 3. Configure System

Use the admin UI to:

- ✅ View and edit complaint types
- ✅ Create and manage business rules
- ✅ Modify evaluation profiles and metrics
- ✅ Update prompt templates
- ✅ Review audit logs

## Database Schema

### Tables

#### complaint_types

- `id`: Primary key
- `type_id`: Unique identifier (e.g., "fraud_complaint")
- `name`: Display name
- `description`: Description
- `risk_level`: low | medium | high | critical
- `priority`: 1-10
- `escalation_threshold`: 0.0-1.0
- `requires_human_review`: Boolean
- `is_active`: Boolean
- `created_at`, `updated_at`: Timestamps

#### business_rules

- `id`: Primary key
- `rule_id`: Unique identifier
- `name`: Rule name
- `description`: Description
- `complaint_type_id`: Foreign key (optional)
- `condition`: Condition expression
- `action`: Action to take
- `priority`: Execution order
- `is_active`: Boolean
- `created_at`, `updated_at`: Timestamps

#### evaluation_profiles

- `id`: Primary key
- `complaint_type_id`: Foreign key
- `name`: Profile name
- `description`: Description
- `is_active`: Boolean
- `created_at`, `updated_at`: Timestamps

#### evaluation_metrics

- `id`: Primary key
- `profile_id`: Foreign key
- `metric_id`: Identifier
- `name`: Metric name
- `description`: Description
- `weight`: Metric weight (0.0-1.0)
- `scale`: Scoring scale (e.g., "1-5")
- `display_order`: Display order
- `is_active`: Boolean
- `created_at`, `updated_at`: Timestamps

#### prompt_templates

- `id`: Primary key
- `agent_name`: Agent identifier
- `prompt_type`: Type (system_prompt, user_prompt_template)
- `content`: Prompt text
- `description`: Description
- `version`: Version number
- `is_active`: Boolean
- `created_at`, `updated_at`: Timestamps

#### configuration_history

- `id`: Primary key
- `table_name`: Modified table
- `record_id`: Modified record ID
- `action`: create | update | delete
- `old_value`: JSON of old values
- `new_value`: JSON of new values
- `changed_by`: User identifier
- `changed_at`: Timestamp

## Admin UI Features

### Dashboard

- System overview with metrics
- Recent configuration changes
- Quick access to all sections

### Complaint Types

- View all complaint types in table format
- Create new complaint types
- Edit existing types (name, risk level, thresholds, etc.)
- Soft delete (deactivate)

### Business Rules

- List all business rules with filters
- Create conditional rules
- Associate rules with complaint types
- Set execution priority
- Enable/disable rules

### Evaluation Profiles

- View profiles by complaint type
- Edit metric weights and descriptions
- Reorder metrics
- Add/remove metrics

### Prompt Templates

- Browse prompts by agent
- Edit prompt content
- Version management
- Test different prompts

### Audit Log

- Complete change history
- Filter by table, date, user
- View before/after values
- Track configuration evolution

### Database Management

- Import YAML to database
- Export database to YAML
- Database statistics
- Force reimport option

## Configuration Loader

The system automatically uses database configurations when available:

```python
from src.utils.config_loader import ConfigLoader

# Use database (default)
config = ConfigLoader(use_database=True)

# Fallback to YAML
config = ConfigLoader(use_database=False)

# Custom database path
config = ConfigLoader(use_database=True, db_path="path/to/db.sqlite")
```

### Backward Compatibility

The system maintains full backward compatibility with YAML files:

- If database initialization fails, automatically falls back to YAML
- Existing YAML files remain functional
- Migration is optional but recommended

## Integration with Main Application

### Streamlit UI

The main Streamlit application automatically uses database configurations:

```python
# streamlit_app.py
orchestrator = initialize_orchestrator(
    model_name="gpt-4-turbo",
    provider="auto",
    use_database=True  # Enable database configuration
)
```

### Python API

```python
from src.main import LLMJudgeOrchestrator

# With database
orchestrator = LLMJudgeOrchestrator(
    model_name="gpt-4-turbo",
    use_database=True
)

# With YAML (legacy)
orchestrator = LLMJudgeOrchestrator(
    model_name="gpt-4-turbo",
    use_database=False
)
```

## Best Practices

### 1. Configuration Changes

- Test changes in development first
- Use descriptive rule/metric names
- Document complex business rules
- Review audit log regularly

### 2. Prompt Engineering

- Version prompts before major changes
- Keep multiple versions active for A/B testing
- Document expected behavior
- Monitor evaluation quality

### 3. Database Maintenance

- Regular backups of `config/llm_judge.db`
- Review audit logs for anomalies
- Archive old configurations periodically
- Use soft deletes (is_active=False)

### 4. Migration Strategy

1. Initialize database from YAML
2. Verify all configurations loaded correctly
3. Test with sample complaints
4. Switch main app to database mode
5. Keep YAML as backup

## Troubleshooting

### Database Not Initializing

```bash
# Check if SQLite is accessible
python -c "import sqlite3; print(sqlite3.sqlite_version)"

# Verify SQLAlchemy installation
pip install --upgrade sqlalchemy alembic

# Force reimport
python src/database/db_init.py --force
```

### Admin UI Not Loading

```bash
# Verify dependencies
pip install -r requirements.txt

# Check port availability
netstat -an | findstr "8502"

# Try different port
streamlit run admin_app.py --server.port=8503
```

### Configuration Not Updating

- Check audit log for errors
- Verify is_active=True
- Clear config cache
- Restart Streamlit app

### Database Locked

- Close all connections
- Stop all Streamlit instances
- Check for zombie processes

## Advanced Topics

### Custom Database Location

```python
from src.database.db_manager import DatabaseManager

db = DatabaseManager(db_path="custom/path/to/db.sqlite")
```

### Programmatic Configuration

```python
from src.database.db_manager import DatabaseManager

db = DatabaseManager()

# Create complaint type
ct = db.create_complaint_type({
    'type_id': 'new_type',
    'name': 'New Type',
    'risk_level': 'medium',
    'priority': 5
})

# Create business rule
rule = db.create_business_rule({
    'rule_id': 'new_rule',
    'name': 'New Rule',
    'condition': 'amount > 1000',
    'action': 'escalate',
    'priority': 3
})
```

### Export/Backup

```python
from src.database.db_manager import DatabaseManager
import shutil
from datetime import datetime

# Backup database
backup_name = f"llm_judge_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
shutil.copy("config/llm_judge.db", f"backups/{backup_name}")
```

## Support

For issues or questions:

1. Check audit log for recent changes
2. Review database initialization logs
3. Test with YAML fallback mode
4. Check SQLite database file permissions

## Future Enhancements

- [ ] Multi-user authentication
- [ ] Role-based access control
- [ ] Configuration versioning and rollback
- [ ] Import/export YAML from UI
- [ ] Configuration comparison tool
- [ ] Bulk operations
- [ ] Search and filter improvements
- [ ] Real-time configuration reload
