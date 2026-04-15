# 🎨 Streamlit UI - Visual Workflow Guide

## Application Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT WEB UI                             │
│                    http://localhost:8501                             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
        ┌─────────────────────────────────────────────────┐
        │            SIDEBAR NAVIGATION                    │
        ├─────────────────────────────────────────────────┤
        │  🏠 Home                                         │
        │  📝 Evaluate Complaint                          │
        │  📊 View Results                                │
        │  ⚙️  Settings                                    │
        │  📈 Statistics                                   │
        │                                                  │
        │  [System Status]                                │
        │  • Orchestrator: 🟢 Active                      │
        │  • Total Processed: 15                          │
        │  • Human Reviews: 3                             │
        └─────────────────────────────────────────────────┘

```

## Page-by-Page Workflow

### 🏠 HOME PAGE

```
┌───────────────────────────────────────────────────────────┐
│  ⚖️ LLM Judge Agent System                                │
│  Banking Complaint Summary Evaluation Platform            │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  [🤖 AI-Powered] [📊 Multi-Agent] [⚡ Fast & Accurate]   │
│                                                            │
│  🚀 Quick Start                                           │
│  ┌──────────────────────────────────────────────┐        │
│  │ 1️⃣ Initialize the System                      │        │
│  │   Select Model: [gpt-4-turbo ▼]              │        │
│  │   [Initialize Orchestrator]                   │        │
│  └──────────────────────────────────────────────┘        │
│                                                            │
│  🔄 Evaluation Pipeline                                   │
│  📥 → 🏷️ → 📐 → ⚖️ → 👤 → ✅                              │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

### 📝 EVALUATE COMPLAINT PAGE

```
┌────────────────────────────────────────────────────────────┐
│  📝 Evaluate Banking Complaint                             │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Input Method: ◉ Manual Entry  ○ Sample  ○ JSON Upload    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Complaint ID: [COMP_20260415_103000         ]     │   │
│  │ Customer ID:  [CUST_987654                  ]     │   │
│  │ Complaint Type: [fraud                      ▼]    │   │
│  │                                                    │   │
│  │ Original Complaint:                                │   │
│  │ ┌────────────────────────────────────────────┐    │   │
│  │ │ I found three wire transfers...            │    │   │
│  │ │                                            │    │   │
│  │ └────────────────────────────────────────────┘    │   │
│  │                                                    │   │
│  │ Complaint Summary:                                 │   │
│  │ ┌────────────────────────────────────────────┐    │   │
│  │ │ Customer reports unauthorized...           │    │   │
│  │ │                                            │    │   │
│  │ └────────────────────────────────────────────┘    │   │
│  │                                                    │   │
│  │          [🔍 Evaluate Complaint]                   │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 🔄 Evaluating...                                   │   │
│  │ ████████████████░░░░ 80%                           │   │
│  │ Step 4/5: Generating final judgment...             │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 📊 RESULTS DISPLAY

```
┌────────────────────────────────────────────────────────────┐
│  📊 Evaluation Results                                     │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │Complaint │ │  Type:   │ │  Risk:   │ │ Score:   │     │
│  │  ID:     │ │  FRAUD   │ │  🔴HIGH  │ │ 4.26/5.00│     │
│  │COMP_001  │ │          │ │          │ │          │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│                                                             │
│  📋 Recommendation                                         │
│  ┌────────────────────────────────────────────────────┐   │
│  │  ⬆️ ESCALATE                                        │   │
│  │  This complaint requires immediate attention due    │   │
│  │  to high fraud risk and significant financial       │   │
│  │  impact. Escalate to fraud investigation team.      │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  📏 Metric Scores                                          │
│  ▼ Factual Accuracy - Score: 4.5/5                        │
│  ▼ Information Completeness - Score: 4.2/5                │
│  ▼ Clarity & Readability - Score: 3.8/5                   │
│  ▼ Urgency Detection - Score: 4.5/5                       │
│  ▶ Risk Level Accuracy - Score: 3.9/5                     │
│                                                             │
│  ✅ Strengths              🔍 Areas for Improvement        │
│  • Clear description       • Add specific timestamps       │
│  • Urgent tone captured    • Include transaction details   │
│  • Risk identified         • Mention security measures     │
│                                                             │
│  👤 Human Review Required                                  │
│  Request ID: 7f116404-6908-4196-a111-283c0537fabd         │
│  Priority: HIGH | Deadline: 2026-04-16 10:30:00           │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### ⚙️ SETTINGS PAGE

```
┌────────────────────────────────────────────────────────────┐
│  ⚙️ System Settings                                        │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  [🤖 Model Settings] [📋 Configuration] [📂 Output]        │
│                                                             │
│  🤖 LLM Model Configuration                                │
│  Current Model: gpt-4-turbo                                │
│                                                             │
│  Reinitialize with Different Model                         │
│  Select Model: [gpt-4-turbo          ▼]                   │
│                [Reinitialize Orchestrator]                 │
│                                                             │
│  ────────────────────────────────────────────────────      │
│                                                             │
│  📋 Configuration Files                                    │
│  ▼ Business Rules (config/business_rules.yaml)            │
│  ▶ Evaluation Profiles (config/evaluation_profiles.yaml)  │
│  ▶ Prompts (config/prompts.yaml)                          │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 📈 STATISTICS PAGE

```
┌────────────────────────────────────────────────────────────┐
│  📈 System Statistics                                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │  Total   │ │ Approved │ │  Needs   │ │  Human   │     │
│  │Processed │ │          │ │ Revision │ │ Reviews  │     │
│  │    15    │ │    8     │ │    4     │ │    3     │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│                                                             │
│  Detailed Breakdown                                        │
│  ┌──────────┐ ┌──────────┐                                │
│  │Escalated │ │ Rejected │                                │
│  │    2     │ │    1     │                                │
│  └──────────┘ └──────────┘                                │
│                                                             │
│  Session Statistics                                        │
│  Evaluations in current session: 5                         │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

## Interaction Patterns

### Pattern 1: Quick Sample Evaluation

```
1. Home Page → Initialize → Success ✅
2. Navigate → 📝 Evaluate Complaint
3. Select "Sample Complaints"
4. Choose "🚨 Fraud - High Risk"
5. Click "Load Sample"
6. Click "🔍 Evaluate Complaint"
7. View Results → Done! ⏱️ ~30 seconds
```

### Pattern 2: Manual Complaint Entry

```
1. Home Page → Initialize → Success ✅
2. Navigate → 📝 Evaluate Complaint
3. Select "Manual Entry"
4. Fill Form:
   - Complaint ID
   - Customer ID
   - Original text
   - Summary text
   - Optional: Type, customer info
5. Click "🔍 Evaluate Complaint"
6. Wait for Progress Bar
7. Review Detailed Results
8. Navigate → 📊 View Results (to see history)
```


## Color Coding System

### Risk Levels

```
🔴 CRITICAL  - Red background    (#dc3545)
🟠 HIGH      - Orange background (#fd7e14)
🟡 MEDIUM    - Yellow background (#ffc107)
🟢 LOW       - Green background  (#28a745)
```

### Recommendations

```
✅ APPROVE   - Green success box
📝 REVISE    - Yellow warning box
⬆️ ESCALATE  - Red danger box
❌ REJECT    - Red danger box
```

### Status Indicators

```
🟢 Active    - System operational
🔴 Inactive  - System not initialized
🟡 Warning   - Configuration issues
```

## Keyboard Shortcuts

```
R     - Rerun the application
C     - Clear cache and refresh
Esc   - Close sidebar (mobile)
H     - Show help (coming soon)
```

## Mobile Responsive Layout

```
Desktop (>1024px):        Tablet (768-1024px):     Mobile (<768px):
┌─────────┬──────────┐   ┌─────────┬─────────┐    ┌──────────────┐
│Sidebar  │  Main    │   │Sidebar  │  Main   │    │   Hamburger  │
│         │          │   │(collaps)│         │    │     Menu     │
│Navigation Content  │   │         │         │    ├──────────────┤
│         │          │   │         │         │    │              │
│         │          │   │         │         │    │   Content    │
│         │          │   │         │         │    │   (Full)     │
└─────────┴──────────┘   └─────────┴─────────┘    └──────────────┘
```

## Data Flow

```
User Input
    │
    ▼
Streamlit UI (streamlit_app.py)
    │
    ▼
Session State Management
    │
    ▼
LLMJudgeOrchestrator (src/main.py)
    │
    ├──► Classifier Agent
    ├──► Metric Evaluator Agent
    ├──► Judge Agent
    └──► Human Review Agent
    │
    ▼
Results Processing
    │
    ├──► Save to output/evaluations/
    ├──► Save to output/human_reviews/
    └──► Update session state
    │
    ▼
Display Results in UI
    │
    ├──► Overview Metrics
    ├──► Recommendation Box
    ├──► Metric Scores (expandable)
    ├──► Strengths & Improvements
    └──► Human Review Request
```

## Session State Management

```
st.session_state = {
    'orchestrator': LLMJudgeOrchestrator instance,
    'evaluation_history': [
        {
            'complaint': Complaint,
            'evaluation_result': EvaluationResult,
            'human_review_request': HumanReviewRequest
        },
        ...
    ],
    'current_evaluation': {...}
}
```

## Error Handling Flow

```
Try:
    User Action
    │
    ▼
    Validation
    │
    ▼
    Processing
    │
    ▼
    Success ✅

Catch:
    Error Detected
    │
    ▼
    Error Message
    │
    ├──► st.error() - Critical
    ├──► st.warning() - Non-critical
    └──► st.info() - Information
    │
    ▼
    Recovery Options
    │
    └──► Suggested Actions
```

---

## 🎯 Quick Reference Card

| Task               | Location      | Action                          |
| ------------------ | ------------- | ------------------------------- |
| Initialize System  | 🏠 Home       | Click "Initialize Orchestrator" |
| Evaluate Complaint | 📝 Evaluate   | Choose input method → Evaluate  |
| View History       | 📊 Results    | Browse Recent/Saved tabs        |
| Change Model       | ⚙️ Settings   | Select model → Reinitialize     |
| Check Stats        | 📈 Statistics | View metrics                    |
| Sample Test        | 📝 Evaluate   | Sample Complaints → Fraud       |
| JSON Import        | 📝 Evaluate   | JSON Upload → Choose file       |
| View Config        | ⚙️ Settings   | Configuration tab               |

---

**💡 Pro Tip**: Bookmark this guide for quick workflow reference!
