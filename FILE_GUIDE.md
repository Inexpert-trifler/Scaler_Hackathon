# 📁 PromptGym File Guide

**Quick reference for all project files and their purposes**

---

## 📖 Documentation Files (Read These First!)

| File | Purpose | Read When |
|------|---------|-----------|
| [SUMMARY.md](SUMMARY.md) | **START HERE** - Overview of all improvements | First thing |
| [QUICK_START.md](QUICK_START.md) | 5-minute setup and first run | Want to run locally |
| [README.md](README.md) | Complete project documentation + API reference | Need full details |
| [HACKATHON_WORKFLOW.md](HACKATHON_WORKFLOW.md) | 10-phase implementation guide + architecture | Want to understand design |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Pre-submission validation checklist | Before submitting |

---

## 🐍 Application Code (`app/`)

### Core FastAPI Application
- **`app/main.py`** - FastAPI server with 6 endpoints
  - `/health` - Server status
  - `/reset` - Start new episode
  - `/step` - Execute prompt
  - `/state` - Current state
  - `/metrics` - Performance metrics
  - `/tasks` - List all tasks

### Environment (`app/env/`)
- **`app/env/environment.py`** - OpenEnv (gymnasium.Env) compatible environment
  - Task loading and sampling
  - Episode management
  - State/observation handling
  - Step execution

- **`app/env/tasks.py`** - Task definitions
  - 9 total tasks (3 EASY, 3 MEDIUM, 3 HARD)
  - Realistic scenarios
  - Helper functions for difficulty filtering

- **`app/env/grader.py`** - Multi-metric grading system
  - Summarization grading (semantic + concepts + length)
  - JSON conversion grading (validity + accuracy + structure)
  - Reasoning grading (answer + reasoning quality + semantic)
  - Unified scoring 0.0-1.0

### Agent (`app/agent/`)
- **`app/agent/baseline_agent.py`** - Agent implementations
  - `BaselineAgent` - Simple template-based
  - `AdaptiveBaselineAgent` - Learning adaptive agent
  - History tracking and mutation

### Utilities (`app/utils/`)
- **`app/utils/llm_executor.py`** - LLM execution layer
  - `LLMProvider` abstract base class
  - `OpenAIExecutor` - Real OpenAI integration
  - `MockExecutor` - Testing without API
  - Factory pattern for provider selection

---

## 🧪 Scripts & Tools (`scripts/`)

- **`scripts/run_baseline_evaluation.py`** - Comprehensive evaluation framework
  - Run multiple episodes
  - Track metrics per difficulty
  - Generate performance reports
  - Supports mock and OpenAI providers

- **`scripts/validate_setup.py`** - Setup validation utility
  - Check imports
  - Verify files
  - Test environment initialization
  - Validate API endpoints

---

## ⚙️ Configuration Files

- **`config.yaml`** - Centralized configuration
  - Environment settings (max_steps, difficulty weights)
  - LLM settings (provider, model, temperature)
  - Grading weights
  - Logging configuration

- **`.env.example`** - Environment variables template
  - OpenAI API key
  - Environment settings
  - Logging level

---

## 🐳 Deployment Files

- **`Dockerfile`** - Production-grade container definition
  - Python 3.11-slim base
  - All dependencies installed
  - Health check configured
  - Proper port exposure

- **`requirements.txt`** - Python dependencies
  - FastAPI, Uvicorn
  - Gymnasium (OpenEnv)
  - OpenAI, Pydantic
  - PyYAML for configuration

---

## 🔧 Git Configuration

- **`.gitignore`** - Files to ignore in version control
  - Environment files (.env)
  - Python artifacts (__pycache__, *.pyc)
  - IDE files (.vscode, .idea)
  - Logs and temporary files

---

## 📂 Project Structure

```
scaler-hackathon/
│
├── 📖 DOCUMENTATION
│   ├── SUMMARY.md                    # ⭐ START HERE - Overview
│   ├── QUICK_START.md               # 5-minute setup
│   ├── README.md                    # Complete guide
│   ├── HACKATHON_WORKFLOW.md        # 10-phase guide
│   ├── DEPLOYMENT_CHECKLIST.md      # Pre-submission
│   └── FILE_GUIDE.md                # This file
│
├── 🐍 APPLICATION
│   └── app/
│       ├── __init__.py
│       ├── main.py                  # FastAPI server (6 endpoints)
│       │
│       ├── env/                     # Environment system
│       │   ├── __init__.py
│       │   ├── environment.py       # Gymnasium.Env (core logic)
│       │   ├── tasks.py            # 9 tasks + helpers
│       │   └── grader.py           # Multi-metric grading
│       │
│       ├── agent/                   # Agent system
│       │   ├── __init__.py
│       │   └── baseline_agent.py    # Baseline + Adaptive
│       │
│       └── utils/                   # Utilities
│           ├── __init__.py
│           └── llm_executor.py     # LLM integration
│
├── 🧪 SCRIPTS
│   └── scripts/
│       ├── run_baseline_evaluation.py  # Evaluation framework
│       └── validate_setup.py           # Setup validator
│
├── ⚙️ CONFIGURATION
│   ├── config.yaml                  # Settings
│   ├── .env.example                 # Env template
│   └── .gitignore                   # Git config
│
├── 🐳 DEPLOYMENT
│   ├── Dockerfile                   # Container image
│   └── requirements.txt             # Dependencies
```

---

## 🚀 How to Use Each File

### For Development

1. **Start with** → `SUMMARY.md` (understand what was built)
2. **Then read** → `QUICK_START.md` (get it running)
3. **Check** → `README.md` (API reference)
4. **Study** → `app/main.py` (FastAPI structure)
5. **Understand** → `app/env/environment.py` (core logic)

### For Customization

1. **Modify tasks** → Edit `app/env/tasks.py`
2. **Adjust grading** → Edit `app/env/grader.py`
3. **Change config** → Edit `config.yaml`
4. **Improve agent** → Edit `app/agent/baseline_agent.py`
5. **Modify LLM** → Edit `app/utils/llm_executor.py`

### For Deployment

1. **Local testing** → Follow `QUICK_START.md`
2. **Validation** → Run `scripts/validate_setup.py`
3. **Docker** → Use `Dockerfile` + `docker build`
4. **Hugging Face** → Push to Spaces with Docker runtime
5. **Final checks** → Use `DEPLOYMENT_CHECKLIST.md`

### For Evaluation

1. **Run baseline** → `python scripts/run_baseline_evaluation.py`
2. **Get metrics** → Check API `/metrics` endpoint
3. **Analyze** → Review evaluation reports
4. **Improve** → Modify `app/agent/baseline_agent.py`

---

## 📊 File Purposes at a Glance

### Core Files (Must Have)
- `app/main.py` - Server (can't work without)
- `app/env/environment.py` - Environment (can't work without)
- `app/env/tasks.py` - Tasks (can't work without)
- `app/env/grader.py` - Grading (can't work without)
- `requirements.txt` - Dependencies (can't work without)
- `Dockerfile` - Deployment (needed for hackathon)

### Enhancement Files
- `app/agent/baseline_agent.py` - Better baseline agent
- `app/utils/llm_executor.py` - Real LLM support
- `config.yaml` - Configuration management
- `scripts/run_baseline_evaluation.py` - Evaluation framework
- `scripts/validate_setup.py` - Setup validation

### Documentation Files
- `README.md` - User documentation
- `QUICK_START.md` - Quick setup
- `HACKATHON_WORKFLOW.md` - Implementation guide
- `DEPLOYMENT_CHECKLIST.md` - Pre-submission
- `SUMMARY.md` - Overview

---

## 🎯 Reading Order by Goal

### Goal: Understand the Project
1. SUMMARY.md (10 min)
2. HACKATHON_WORKFLOW.md (20 min)
3. README.md (15 min)

### Goal: Run it Locally
1. QUICK_START.md (5 min)
2. Follow the steps
3. Check `scripts/validate_setup.py` for validation

### Goal: Deploy to Production
1. QUICK_START.md (setup)
2. DEPLOYMENT_CHECKLIST.md (validation)
3. Dockerfile (Docker deployment)
4. HF Spaces docs (for HF deployment)

### Goal: Modify/Extend
1. HACKATHON_WORKFLOW.md (understand design)
2. README.md (API reference)
3. Relevant file (e.g., `app/env/grader.py`)
4. `scripts/validate_setup.py` (verify)

### Goal: Evaluate Performance
1. README.md (understand metrics)
2. `scripts/run_baseline_evaluation.py` (run evaluation)
3. `app/agent/baseline_agent.py` (improve agent)
4. Repeat evaluation

---

## 💡 Tips & Tricks

### Fastest First Run
```bash
cd scaler-hackathon
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python scripts/validate_setup.py  # Should pass
python -m uvicorn app.main:app --reload
# Visit http://localhost:8000/docs
```

### Quick Test
```bash
# Terminal 1
python -m uvicorn app.main:app

# Terminal 2
curl http://localhost:8000/health
curl -X POST http://localhost:8000/reset
```

### Run Evaluation
```bash
python scripts/run_baseline_evaluation.py --episodes 50
```

### Docker Test
```bash
docker build -t promptgym .
docker run -p 8000:8000 promptgym
curl http://localhost:8000/health
```

---

## 🔗 File Dependencies

```
app/main.py
  ├── app/env/environment.py
  │   ├── app/env/tasks.py
  │   ├── app/env/grader.py
  │   └── app/utils/llm_executor.py
  │       └── (openai library)
  └── pydantic, fastapi

scripts/run_baseline_evaluation.py
  ├── app/env/environment.py
  ├── app/agent/baseline_agent.py
  └── (numpy)

scripts/validate_setup.py
  ├── config.yaml
  ├── app/env/tasks.py
  ├── app/env/grader.py
  ├── app/env/environment.py
  └── app/main.py
```

---

## ✅ Verification Checklist

Make sure you have:

- [ ] All `.py` files in `app/` directory
- [ ] `scripts/` directory with 2 files
- [ ] `config.yaml` in root
- [ ] `requirements.txt` in root
- [ ] `Dockerfile` in root
- [ ] `.env.example` in root
- [ ] `README.md` in root
- [ ] All 5 documentation files in root

Run: `python scripts/validate_setup.py`

Expected: ✓ All validation checks passed!

---

## 📞 Not Finding What You Need?

| Question | Answer |
|----------|--------|
| How do I run it? | Read QUICK_START.md |
| How do I use the API? | Read README.md |
| What was improved? | Read SUMMARY.md |
| How is it designed? | Read HACKATHON_WORKFLOW.md |
| What do I need to check before submitting? | Read DEPLOYMENT_CHECKLIST.md |
| How do I modify tasks? | Edit app/env/tasks.py |
| How do I improve the grader? | Edit app/env/grader.py |
| How do I make the agent better? | Edit app/agent/baseline_agent.py |
| How do I use real LLM? | Set LLM_PROVIDER=openai and OPENAI_API_KEY |
| How do I deploy? | Follow QUICK_START.md or DEPLOYMENT_CHECKLIST.md |

---

**Next Step: Read [SUMMARY.md](SUMMARY.md) for overview of all improvements!**
