# PromptGym Quick Setup Guide 🚀

**Get running in 5 minutes**

---

## Prerequisites

- Python 3.11+ 
- pip (Python package manager)
- (Optional) OpenAI API key

---

## Setup Steps

### Step 1: Create Virtual Environment

```bash
cd /Users/saranshyadav/Documents/Web-Dev/scaler-hackathon
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi uvicorn pydantic gymnasium numpy scipy pyyaml...
```

### Step 3: Verify Setup

```bash
python scripts/validate_setup.py
```

Expected: `✓ All validation checks passed!`

---

## Running the API

### Development Mode

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Then open: http://localhost:8000/docs

### Using Mock LLM (Default)

```bash
export LLM_PROVIDER=mock
python -m uvicorn app.main:app --port 8000
```

### Using OpenAI API

```bash
export OPENAI_API_KEY="sk-your-key-here"
export LLM_PROVIDER=openai
python -m uvicorn app.main:app --port 8000
```

---

## Testing

### 1. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

### 2. Test Full Flow

```bash
# Reset environment
curl -X POST http://localhost:8000/reset | jq

# Submit a prompt
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Summarize this in one sentence: AI is great"}' | jq

# Get current state
curl http://localhost:8000/state | jq
```

### 3. Run Evaluation

```bash
# Quick test (10 episodes)
python scripts/run_baseline_evaluation.py --episodes 10

# Full evaluation (50 episodes)
python scripts/run_baseline_evaluation.py --episodes 50 --provider mock
```

---

## Docker Deployment

```bash
# Build image
docker build -t promptgym .

# Run container
docker run -p 8000:8000 promptgym

# Wait 40 seconds, then test
curl http://localhost:8000/health
```

---

## File Structure

```
scaler-hackathon/
├── app/
│   ├── main.py                    # 🔴 Fast API app
│   ├── env/
│   │   ├── environment.py         # 🎮 OpenEnv environment
│   │   ├── tasks.py              # 📋 Task definitions
│   │   └── grader.py             # ⭐ Multi-metric grader
│   ├── agent/
│   │   └── baseline_agent.py      # 🤖 Baseline + Adaptive agents
│   └── utils/
│       └── llm_executor.py        # 🧠 LLM integration (OpenAI + Mock)
├── scripts/
│   ├── run_baseline_evaluation.py # 📊 Evaluation script
│   └── validate_setup.py          # ✅ Setup validator
├── config.yaml                    # ⚙️ Configuration
├── Dockerfile                     # 🐳 Docker image
├── requirements.txt               # 📦 Dependencies
├── README.md                      # 📖 Full documentation
├── HACKATHON_WORKFLOW.md         # 🚀 Implementation guide
└── DEPLOYMENT_CHECKLIST.md       # ✅ Pre-submission checklist
```

---

## Key Features

✅ **OpenEnv Compatible** - Full gymnasium.Env implementation  
✅ **Real LLM Integration** - OpenAI + Mock executor  
✅ **Multi-Metric Grading** - Semantic + format + efficiency scores  
✅ **Adaptive Agent** - Baseline agent that learns over time  
✅ **3 Difficulty Levels** - EASY, MEDIUM, HARD tasks  
✅ **Production Ready** - Error handling, logging, Docker support  
✅ **Fully Documented** - API docs, README, deployment guide  

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'gymnasium'`
```bash
pip install -r requirements.txt
```

### `OPENAI_API_KEY not set`
```bash
# Use mock LLM instead
export LLM_PROVIDER=mock

# Or set your API key
export OPENAI_API_KEY="sk-..."
```

### Port 8000 already in use
```bash
# Use different port
python -m uvicorn app.main:app --port 8001
```

### Docker build fails
```bash
# Rebuild without cache
docker build --no-cache -t promptgym .
```

---

## Next Steps

1. ✅ Run validation: `python scripts/validate_setup.py`
2. ✅ Start API: `python -m uvicorn app.main:app --reload`
3. ✅ Test endpoints: `curl http://localhost:8000/docs`
4. ✅ Run evaluation: `python scripts/run_baseline_evaluation.py`
5. ✅ Follow [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) before submission

---

## API Documentation

See http://localhost:8000/docs (automatic Swagger UI)

Or read [README.md](README.md) for full API reference

---

**Ready to compete!** 🎯
