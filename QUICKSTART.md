# 🚀 Quick Start Guide - Streamlit UI

Get started with the LLM Judge Agent System UI in 5 minutes!

## Prerequisites

- Python 3.8+
- OpenAI API Key
- Internet connection

## Step 1: Install Dependencies

Open PowerShell in the project directory and run:

```powershell
# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Set Up API Key

**Option A: Environment Variable (Recommended for testing)**

```powershell
$env:OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

**Option B: .env File (Recommended for permanent setup)**

Create a file named `.env` in the project root:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Step 3: Launch the UI

**Option A: Use the launcher script**

```powershell
# Double-click launch_ui.bat in File Explorer
# OR run from PowerShell:
.\launch_ui.ps1
```

**Option B: Run directly**

```powershell
streamlit run streamlit_app.py
```

Your browser will automatically open to `http://localhost:8501`

## Step 4: Initialize the System

1. You'll see the **Home** page
2. Scroll to "Quick Start" section
3. Select your preferred model (GPT-4 Turbo recommended)
4. Click **"Initialize Orchestrator"**
5. Wait for the success message ✅

## Step 5: Evaluate Your First Complaint

### Option 1: Use a Sample (Easiest)

1. Navigate to **"📝 Evaluate Complaint"** in the sidebar
2. Select **"Sample Complaints"** radio button
3. Choose a sample type (e.g., "🚨 Fraud - High Risk")
4. Click **"Load Sample"**
5. Click **"🔍 Evaluate Complaint"**
6. Watch the evaluation progress!

### Option 2: Manual Entry

1. Navigate to **"📝 Evaluate Complaint"**
2. Select **"Manual Entry"**
3. Fill in the form:
   - **Complaint ID**: Auto-generated or enter custom
   - **Customer ID**: Enter customer identifier
   - **Complaint Type**: Select from dropdown (or leave blank for auto-classification)
   - **Original Complaint**: Paste the customer's original text
   - **Complaint Summary**: Enter the summarized version
4. Click **"🔍 Evaluate Complaint"**

## Step 6: View Results

After evaluation, you'll see:

- **Overview Metrics**: ID, type, risk level, score
- **Recommendation**: Approve, Revise, Escalate, or Reject
- **Metric Scores**: Detailed breakdown with reasoning
- **Strengths & Improvements**: Quality analysis
- **Human Review**: If required, shows priority and deadline

## Step 7: Explore More

- **📊 View Results**: Browse evaluation history
- **📈 Statistics**: Track performance metrics
- **⚙️ Settings**: Change models, view configs

## Troubleshooting

### "Orchestrator not initialized"

→ Go to Home page and click "Initialize Orchestrator"

### "API Key Error"

→ Verify your OPENAI_API_KEY is set correctly
→ Check your OpenAI account has billing enabled

### "Module not found"

→ Ensure you're in the virtual environment
→ Run: `pip install -r requirements.txt`

### Page won't load

→ Check terminal for error messages
→ Ensure port 8501 is not in use
→ Try: `streamlit run streamlit_app.py --server.port 8502`

### Evaluation takes too long

→ Switch to faster model (GPT-3.5 Turbo) in Settings
→ Check your internet connection
→ Verify OpenAI API status

## Tips for Best Experience

1. **Start with samples** to understand the system
2. **Use GPT-4 Turbo** for highest quality results
3. **Check statistics** regularly to monitor patterns
4. **Review metric scores** to understand evaluation logic
5. **Save important evaluations** for reference

## What's Next?

- Customize evaluation metrics in `config/evaluation_profiles.yaml`
- Adjust business rules in `config/business_rules.yaml`
- Modify prompts in `config/prompts.yaml`
- Process multiple complaints in batch (coming soon)
- Export results to PDF (coming soon)

## Need Help?

- Check [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) for detailed documentation
- Review [README.md](README.md) for system architecture
- Check configuration files in `config/` directory
- Review sample outputs in `output/` directory

---

**Ready to Start?** Run `streamlit run streamlit_app.py` and enjoy! 🎉
