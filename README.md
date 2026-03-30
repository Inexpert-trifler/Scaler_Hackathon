---
title: PromptGym
emoji: 🏋️
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 8000
tags:
  - openenv
pinned: false
---

# PromptGym Backend 🎯

**A complete backend system for training and evaluating LLM prompt engineering**

PromptGym is an RL-friendly environment where agents submit prompts to solve tasks, and the system provides multi-signal rewards. No API keys required - mock LLM mode built-in.

## 📋 Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Client (Agent/Browser)                                     │
│  • Calls /reset to start episode                            │
│  • Calls /step to submit prompt                             │
│  • Receives (observation, reward, done, info)               │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ↓
        ┌─────────────────────┐
        │  FastAPI Server     │
        │  (app/main.py)      │
        └─────────┬───────────┘
                  │
                  ↓
         ┌────────────────────┐
         │ PromptGymEnv       │──────→  TaskLoader
         │ (app/env.py)       │──────→  LLMExecutor (mock)
         │                    │──────→  Grader
         │                    │──────→  SessionManager
         │                    │──────→  PyTorch RewardScorer (optional)
         └────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ↓             ↓             ↓
  Tasks       Grading         Session
  (JSON)      Signals         State
```

## 🏗️ System Architecture

### Component Overview

| Component | Purpose | File |
|-----------|---------|------|
| **Config** | Environment settings (mode, port, thresholds) | `app/config.py` |
| **Schemas** | Pydantic request/response models | `app/schemas.py` |
| **Tasks** | 15 tasks (5 per difficulty) with ground truth | `app/tasks/` |
| **Executor** | Mock LLM that simulates output quality | `app/executor.py` |
| **Grader** | Multi-signal grading (5 metrics, task-weighted) | `app/grader.py` |
| **Scorer** | Optional PyTorch reward model (guarded import) | `scorer/reward_model.py` |
| **Session** | In-memory episode state tracking | `app/session.py` |
| **Environment** | Orchestrator combining all components | `app/env.py` |
| **API** | FastAPI server with 6 endpoints | `app/main.py` |

## 🎮 Quick Start

### Installation

```bash
# Clone repo
git clone <your-repo>
cd scaler-hackathon

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running Locally

```bash
# Copy environment template
cp .env.example .env

# Start API server
python -m uvicorn app.main:app --host 0.0.0.0 --port 7860

# In another terminal, run baseline agent
python agent/baseline_agent.py
```

**API**: http://localhost:7860
**Docs**: http://localhost:7860/docs

### Running Tests

```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_grader.py::test_perfect_score_summarization -v

# With coverage
pytest tests/ --cov=app
```

### Docker Deployment

```bash
# Build image
docker build -t promptgym:latest .

# Run container
docker run -p 7860:7860 \
  -e LLM_MODE=mock \
  -e USE_TORCH_SCORER=True \
  promptgym:latest
```

## 📡 API Endpoints

### 1. Health Check
```bash
GET /health

# Response
{
  "status": "ok",
  "sessions_active": 2
}
```

### 2. Reset Environment
```bash
POST /reset
{
  "difficulty": "easy",
  "session_id": "optional-id"  # optional, auto-generated if not provided
}

# Response
{
  "session_id": "uuid-...",
  "observation": {
    "task_description": "Summarize the given text",
    "input_data": "...",
    "task_type": "summarization",
    "step": 0,
    "max_steps": 5,
    "difficulty": "easy"
  },
  "info": {
    "task_id": "easy_01",
    "task_type": "summarization"
  }
}
```

### 3. Step (Execute Prompt)
```bash
POST /step
{
  "session_id": "uuid-...",
  "action": "Your prompt here"
}

# Response
{
  "observation": {...},
  "reward": 0.85,  # [0.0, 1.0]
  "done": false,
  "info": {
    "llm_output": "Model's response",
    "score": 0.85,
    "signals": {
      "token_f1": 0.8,
      "keyword_coverage": 0.9,
      "length_penalty": 0.85,
      "json_structure": 1.0,
      "answer_match": 0.75
    },
    "step": 1,
    "task_id": "easy_01"
  }
}
```

### 4. Get State
```bash
GET /state/{session_id}

# Response
{
  "session_id": "uuid-...",
  "observation": {...},
  "last_reward": 0.85,
  "total_reward": 0.85,
  "step": 1,
  "done": false
}
```

### 5. List Tasks
```bash
GET /tasks/{difficulty}

# Response
{
  "difficulty": "easy",
  "count": 5,
  "tasks": [
    {"id": "easy_01", "type": "summarization"},
    {"id": "easy_02", "type": "summarization"},
    ...
  ]
}
```

### 6. Leaderboard
```bash
GET /leaderboard

# Response
{
  "leaderboard": [
    {
      "session_id": "uuid-...",
      "total_reward": 4.25,
      "steps": 5,
      "difficulty": "easy",
      "done": true
    },
    ...
  ],
  "total_sessions": 42
}
```

## 📊 Grading System

The grader computes **5 signals** with **task-specific weighting**:

### Signals Computed

| Signal | Range | Description |
|--------|-------|-------------|
| `token_f1` | [0.0, 1.0] | F1 score on word tokens vs expected output |
| `keyword_coverage` | [0.0, 1.0] | Fraction of task keywords present in output |
| `length_penalty` | [0.0, 1.0] | Penalty for unusual output length (0.5-2.0x is optimal) |
| `json_structure` | [0.0, 1.0] | JSON validity + required keys present (JSON tasks only) |
| `answer_match` | [0.0, 1.0] | Match against answer variants (reasoning tasks only) |

### Task-Specific Weighting

**Summarization:**
```
score = 0.35×token_f1 + 0.35×keyword_coverage + 0.30×length_penalty
```

**JSON Extraction:**
```
score = 0.50×json_structure + 0.30×token_f1 + 0.20×keyword_coverage
```

**Reasoning:**
```
score = 0.60×answer_match + 0.25×keyword_coverage + 0.15×token_f1
```

All scores are clipped to [0.0, 1.0] and rounded to 4 decimals.

## 🧠 Mock LLM Quality

The mock executor simulates LLM quality based on **keyword ratio** in the prompt:

| Keyword Ratio | Quality Tier | Output Type |
|---|---|---|
| ≥ 0.70 | HIGH | Paraphrased summary / Valid JSON / Detailed reasoning |
| 0.40-0.70 | MEDIUM | Partial summary / Missing JSON keys / Vague reasoning |
| < 0.40 | LOW | Generic text / Invalid JSON / Wrong answer |

**Example:**
```
Task keywords: ["AI", "neural networks", "training"]
Prompt: "Explain AI and neural networks"
Keyword ratio: 2/3 ≈ 0.67 → MEDIUM quality
```

## 🔥 PyTorch Reward Model

Optional deep reward model for blending with grader scores:

**Architecture:**
```
Input Features (dim=6)
  ↓
Linear(6 → 32) + ReLU + Dropout(0.2)
  ↓
Linear(32 → 16) + ReLU
  ↓
Linear(16 → 1) + Sigmoid
  ↓
Output: score ∈ [0.0, 1.0]
```

**Feature Extraction:**
- `prompt_length`: Normalized prompt word count
- `output_length`: Normalized output word count
- `keyword_ratio`: Task keywords in output
- `has_instructions`: Explicit instructions present
- `output_non_empty`: Non-empty output
- `prompt_output_overlap`: Overlap ratio

**Pretraining:** Synthetic data (200 examples) for 50 epochs

**Blending:** Final score = 0.7 × grader_score + 0.3 × torch_score

Set `USE_TORCH_SCORER=False` to disable (still works if torch unavailable).

## 📦 File Structure

```
scaler-hackathon/
├── app/
│   ├── __init__.py
│   ├── config.py              # Settings + pydantic-settings
│   ├── schemas.py             # 7 Pydantic models
│   ├── main.py                # FastAPI server
│   ├── env.py                 # PromptGymEnv orchestrator
│   ├── executor.py            # Mock LLM executor
│   ├── grader.py              # Multi-signal grader
│   ├── session.py             # Session manager
│   └── tasks/
│       ├── __init__.py
│       ├── loader.py          # TaskLoader class
│       ├── easy.json          # 5 summarization tasks
│       ├── medium.json        # 5 JSON extraction tasks
│       └── hard.json          # 5 reasoning tasks
├── agent/
│   ├── __init__.py
│   └── baseline_agent.py      # 4 prompt strategies
├── scorer/
│   ├── __init__.py
│   └── reward_model.py        # PyTorch MLP + pretraining
├── tests/
│   ├── __init__.py
│   ├── test_grader.py         # 7 grader tests
│   └── test_api.py            # 8 API tests
├── requirements.txt           # 9 dependencies
├── Dockerfile                 # Python 3.11-slim
├── .env.example              # Config template
└── README.md                  # This file
```

## 🧪 Testing

### Test Coverage

**test_grader.py** (7 tests):
- Perfect score on expected output
- Empty output handling
- JSON structure validation
- Reasoning with answer variants
- Score bounds [0.0, 1.0]
- Keyword coverage scoring
- Length penalty scoring

**test_api.py** (8 tests):
- Health check
- Reset with/without session ID
- Invalid difficulty error
- Valid step execution
- Invalid session error
- Full episode (5 steps)
- State endpoint
- Reward bounds check

### Running Tests

```bash
# Run all
pytest tests/ -v

# Specific module
pytest tests/test_grader.py -v

# Specific test
pytest tests/test_api.py::test_full_episode -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## 🚀 Deployment

### HuggingFace Spaces

```bash
# Push to HF Spaces
git push huggingface main

# Container runs on port 7860 automatically
# API accessible at: https://your-username-space.hf.space
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|---|
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 7860 | Server port |
| `LLM_MODE` | mock | LLM mode (only "mock" supported) |
| `MAX_STEPS` | 5 | Max steps per episode |
| `REWARD_THRESHOLD` | 0.95 | Score threshold to terminate episode |
| `USE_TORCH_SCORER` | True | Enable PyTorch reward model |
| `LOG_FILE` | logs/episodes.jsonl | JSONL episode logs path |

## 📝 Example Workflows

### Using curl

```bash
# 1. Reset
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}'

# 2. Step
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "...",
    "action": "Summarize this text in one sentence: ..."
  }'

# 3. Leaderboard
curl http://localhost:7860/leaderboard
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:7860"

# Reset
resp = requests.post(f"{BASE_URL}/reset", json={"difficulty": "easy"})
session_id = resp.json()["session_id"]

# Step
resp = requests.post(f"{BASE_URL}/step", json={
    "session_id": session_id,
    "action": "Your prompt here"
})

print(f"Reward: {resp.json()['reward']}")
print(f"Done: {resp.json()['done']}")
```

### Using Baseline Agent

```bash
python agent/baseline_agent.py

# Output:
# Benchmark Results:
# ────────────────────────────────────────────
# Difficulty    Strategy              Reward    Steps
# ────────────────────────────────────────────
# easy          NAIVE                 0.7234    3
# easy          STRUCTURED            0.8123    2
# ...
```

## 🔧 Configuration

### Mock LLM Settings

Edit behavior in `app/executor.py`:

```python
# Adjust quality tier thresholds
if keyword_ratio >= 0.70:       # HIGH quality threshold
elif keyword_ratio >= 0.40:     # MEDIUM quality threshold
else:                           # LOW quality
```

### Grader Weights

Edit in `app/grader.py`:

```python
# Adjust task-specific weights
if task["type"] == "summarization":
    return 0.35 * token_f1 + 0.35 * keyword_coverage + 0.30 * length_penalty
```

### Torch Model

Edit in `scorer/reward_model.py`:

```python
# Adjust network architecture
class RewardMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(6, 64)  # Increase hidden units
        # ... rest of network
```

## 📊 Performance Tips

1. **Cache Tasks**: TaskLoader caches all tasks in memory on init
2. **In-Memory Sessions**: No database overhead
3. **Mock LLM**: ~1ms per execution (deterministic)
4. **Batch Grading**: Process multiple outputs in parallel
5. **Torch Optional**: System works without PyTorch (graceful fallback)

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 7860 in use | Set `PORT=8000` in .env |
| Torch import error | Set `USE_TORCH_SCORER=False` in .env |
| Tasks not loading | Check JSON syntax in `app/tasks/*.json` |
| Session not found | Verify session_id is current |
| Reward out of bounds | File issue (should not happen) |

## 📄 License

MIT

## 👤 Author

Built for Scaler Hackathon

---

**Made with ❤️ for prompt engineering research**
