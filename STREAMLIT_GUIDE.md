# Streamlit UI Guide - LLM Judge Agent System

## 🚀 Quick Start

### Installation

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your OpenAI API key:**

   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY = "your-api-key-here"

   # Or create a .env file
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

3. **Run the Streamlit application:**

   ```bash
   streamlit run streamlit_app.py
   ```

4. **Access the application:**
   - Opens automatically in your browser at `http://localhost:8501`
   - Or navigate manually to the URL shown in the terminal

## 📖 Features Overview

### 🏠 Home Page

- **System overview** and quick start guide
- **Initialize orchestrator** with your preferred LLM model
- View the **evaluation pipeline** visualization
- System status indicators

### 📝 Evaluate Complaint

Three input methods:

1. **Manual Entry**: Enter complaint details directly
   - Complaint ID, Customer ID
   - Original complaint text
   - Summary text
   - Customer metadata (high-value, previous complaints)
   - Optional complaint type

2. **Sample Complaints**: Load pre-configured examples
   - Fraud scenarios
   - Billing disputes
   - Account access issues
   - Service quality complaints

3. **JSON Upload**: Import complaint data from file
   ```json
   {
     "complaint_id": "COMP_001",
     "customer_id": "CUST_12345",
     "original_complaint": "...",
     "summary": "...",
     "submission_date": "2026-04-15T10:30:00",
     "complaint_type": "fraud",
     "has_previous_complaints": false,
     "previous_complaint_count": 0,
     "is_high_value_customer": true
   }
   ```

### 📊 View Results

- **Recent Evaluations**: Review current session evaluations
- **Saved Results**: Browse historical evaluation files
- **Search**: Find specific evaluations (coming soon)

### ⚙️ Settings

- **Model Configuration**: Change LLM model
- **Configuration Files**: View YAML configs
- **Output Management**: Check output directories

### 📈 Statistics

- Total complaints processed
- Approval/rejection rates
- Human review requirements
- Session metrics

## 🎨 UI Components

### Evaluation Results Display

Each evaluation shows:

- **Overview Metrics**: Complaint ID, type, risk level, score
- **Recommendation**: Color-coded final decision
  - ✅ Green: APPROVE
  - ⚠️ Yellow: REVISE
  - 🚨 Red: ESCALATE/REJECT
- **Metric Scores**: Detailed scoring with reasoning
- **Strengths & Improvements**: Quality analysis
- **Human Review**: Priority and focus areas (if required)

### Risk Level Indicators

- 🔴 **CRITICAL**: Immediate attention required
- 🟠 **HIGH**: Significant concerns
- 🟡 **MEDIUM**: Moderate issues
- 🟢 **LOW**: Minor or no concerns

## 💡 Usage Tips

### Best Practices

1. **Initialize first**: Always initialize the orchestrator from Home page
2. **Start with samples**: Test with sample complaints to understand the system
3. **Check history**: Review past evaluations before processing new ones
4. **Monitor statistics**: Track system performance and patterns

### Troubleshooting

**Problem**: "Orchestrator not initialized"

- **Solution**: Go to Home page and click "Initialize Orchestrator"

**Problem**: Evaluation takes too long

- **Solution**: Check your API key and network connection
- Consider using a faster model (gpt-3.5-turbo)

**Problem**: Results not showing

- **Solution**: Check the `output/` directory permissions
- Verify YAML configuration files are present

**Problem**: API errors

- **Solution**: Verify OPENAI_API_KEY is set correctly
- Check API quota and rate limits

## 🔧 Configuration

### Model Selection

Available models:

- `gpt-4-turbo`: Best quality, slower, more expensive
- `gpt-4`: High quality, balanced speed
- `gpt-3.5-turbo`: Fast, economical, good quality
- `gpt-4o`: Latest optimized model

### Custom Themes

Edit `.streamlit/config.toml` to customize colors and appearance.

## 📁 Output Files

### Evaluations

- Location: `output/evaluations/`
- Format: `{complaint_id}_evaluation.json` and `{complaint_id}_report.txt`

### Human Reviews

- Location: `output/human_reviews/`
- Format: `{request_id}_review.json` and `{request_id}_review.txt`

## 🔒 Security Notes

- Never commit `.env` files with API keys
- API keys are loaded from environment variables
- Output files may contain sensitive information
- Configure appropriate file permissions for production

## 📞 Support

For issues or questions:

1. Check configuration files in `config/`
2. Review logs in the terminal
3. Examine output files for error details
4. Verify API key and permissions

## 🎯 Next Steps

1. **Explore**: Try different complaint types and scenarios
2. **Customize**: Modify evaluation metrics in config files
3. **Integrate**: Connect with your existing systems
4. **Monitor**: Track patterns in statistics page
5. **Scale**: Process batch evaluations programmatically

---

**Version**: 1.0  
**Last Updated**: April 2026
