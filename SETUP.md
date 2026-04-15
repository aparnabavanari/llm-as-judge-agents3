# Quick Setup Guide - LLM Judge Agent System

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (get from https://platform.openai.com/api-keys)
- Active billing on OpenAI account

## Setup Steps

### 1. Activate Virtual Environment

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure API Key

```powershell
# Copy the example file
Copy-Item .env.example .env

# Edit .env and add your API key
# Open .env in notepad and replace 'sk-your-api-key-here' with your actual key
notepad .env
```

Your `.env` file should look like:

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. Verify Configuration

```powershell
python -c "from src.main import LLMJudgeOrchestrator; print('Config valid!' if LLMJudgeOrchestrator().validate_configuration() else 'Config invalid')"
```

### 5. Run Example

```powershell
python run.py
```

## Expected Costs

Based on GPT-4 Turbo pricing (as of April 2026):

- Input: ~$10 per 1M tokens
- Output: ~$30 per 1M tokens

**Estimated cost per complaint evaluation**: $0.10 - $0.50

- Depends on complaint length and number of metrics
- First run may be more expensive as models "warm up"

## Troubleshooting

### "OpenAI API key not found"

- Check that `.env` file exists in project root
- Verify `OPENAI_API_KEY=` line has your actual key (no quotes needed)
- Make sure there are no spaces around the `=` sign

### "You exceeded your current quota"

- Add billing information to your OpenAI account
- Check your usage limits at https://platform.openai.com/usage

### "The model `gpt-4-turbo` does not exist"

- Verify you have access to GPT-4 in your OpenAI account
- Try using `gpt-4o` instead by changing model_name parameter
- Some accounts need to reach a spending threshold before GPT-4 access

### Import Errors

```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Model Options

You can change the model when initializing:

```python
# GPT-4 Turbo (best quality, moderate speed)
orchestrator = LLMJudgeOrchestrator(model_name="gpt-4-turbo")

# GPT-4o (balanced quality and speed)
orchestrator = LLMJudgeOrchestrator(model_name="gpt-4o")

# GPT-4o Mini (fast, economical)
orchestrator = LLMJudgeOrchestrator(model_name="gpt-4o-mini")

# GPT-3.5 Turbo (cheapest, lower quality)
orchestrator = LLMJudgeOrchestrator(model_name="gpt-3.5-turbo")
```

## Next Steps

1. ✅ Run `run.py` to see the system in action
2. ✅ Check `./output/` directory for generated evaluation results
3. ✅ Review human review requests in `./output/human_reviews/`
4. ✅ Customize `config/*.yaml` files for your specific needs
5. ✅ Monitor API usage in OpenAI dashboard

## Getting Help

- Review README.md for detailed documentation
- Check config files in `config/` directory
- Examine example complaints in `run.py`
- Review inline code documentation
