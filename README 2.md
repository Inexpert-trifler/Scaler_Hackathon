# PromptGym 🎯

**An OpenEnv-compatible backend system for evaluating prompt engineering quality**

PromptGym is a meta-AI evaluation environment where an AI agent generates prompts to solve tasks, and the system evaluates how effective those prompts are. Instead of solving tasks directly, the agent must generate prompts that are executed on a simulated LLM, with outputs graded on quality.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key (optional, defaults to mock LLM)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/promptgym
cd promptgym

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment (optional)
cp .env.example .env
# Edit .env and add your OpenAI API key if using real LLM
```

### Running the API

```bash
# Start development server
python -m uvicorn app.main:app --reload --port 8000

# The API will be available at http://localhost:8000
# Documentation: http://localhost:8000/docs
```

---

## 📚 API Documentation

### Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "PromptGym"
}
```

#### `POST /reset`
Reset environment and load a new task.

**Request (optional):**
```json
{
  "seed": 42
}
```

**Response:**
```json
{
  "observation": {
    "task_description": "Summarize the given text in one sentence",
    "input_data": "...",
    "step": [0],
    "previous_scores": [0.0, 0.0, ...]
  },
  "info": {
    "task_difficulty": "EASY",
    "task_description": "..."
  }
}
```

#### `POST /step`
Execute a prompt action in the environment.

**Request:**
```json
{
  "prompt": "Summarize this text: ..."
}
```

**Response:**
```json
{
  "observation": {...},
  "reward": 0.85,
  "terminated": true,
  "truncated": false,
  "info": {
    "score": 0.85,
    "output": "The text discusses...",
    "step": 1,
    "episode_reward": 0.85,
    "task_difficulty": "EASY"
  }
}
```

#### `GET /state`
Get current environment state.

**Response:**
```json
{
  "state": {
    "task_description": "...",
    "input_data": "...",
    "expected_output": "...",
    "previous_prompts": ["..."],
    "previous_scores": [0.85],
    "step_count": 1,
    "episode_reward": 0.85,
    "task_difficulty": "EASY"
  }
}
```

#### `GET /metrics`
Get environment metrics for monitoring.

**Response:**
```json
{
  "step_count": 1,
  "max_steps": 5,
  "episode_reward": 0.85,
  "previous_scores": [0.85],
  "average_score": 0.85
}
```

#### `GET /tasks`
List all available tasks.

**Response:**
```json
{
  "total_tasks": 9,
  "tasks": [
    {
      "difficulty": "EASY",
      "description": "Summarize the given text in one sentence"
    },
    ...
  ]
}
```

---

## 🧪 Example Usage

### Using cURL

```bash
# 1. Reset environment
curl -X POST http://localhost:8000/reset

# 2. Get initial state
curl http://localhost:8000/state

# 3. Execute a prompt
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Summarize this text in one sentence: ..."}'

# 4. Check metrics
curl http://localhost:8000/metrics
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Reset
reset_response = requests.post(f"{BASE_URL}/reset")
print(reset_response.json())

# Step
step_response = requests.post(
    f"{BASE_URL}/step",
    json={"prompt": "Summarize this in one sentence: ..."}
)
print(step_response.json())
```

---

## 🤖 Baseline Agent Evaluation

Run the baseline agent to evaluate its performance:

```bash
# With mock LLM (default, no API calls)
python scripts/run_baseline_evaluation.py --episodes 50 --provider mock

# With OpenAI API (requires OPENAI_API_KEY)
python scripts/run_baseline_evaluation.py --episodes 50 --provider openai
```

**Output Example:**
```
======================================================================
PromptGym BASELINE EVALUATION RESULTS
======================================================================

Configuration:
  Total Episodes: 50
  LLM Provider: mock

Overall Performance:
  Average Reward: 0.6850 ± 0.2341
  Max Reward: 1.0000
  Min Reward: 0.0000

Performance by Difficulty:
  EASY   (n=17): Avg=0.8235, Max=1.0000, Min=0.3000
  MEDIUM (n=17): Avg=0.7000, Max=1.0000, Min=0.0000
  HARD   (n=16): Avg=0.5000, Max=1.0000, Min=0.0000

Agent Statistics:
  Total Prompts Generated: 250
  Average Prompt Effectiveness: 0.6850
  Best Achieved Score: 1.0000
```

---

## 🏗️ Architecture

### Task System (3 Levels)

| Level | Task Type | Example | Grading |
|-------|-----------|---------|---------|
| **EASY** | Summarization | Summarize text in one sentence | Semantic similarity + key concepts + length |
| **MEDIUM** | JSON Conversion | Parse text into JSON | JSON validity + key-value accuracy + structure |
| **HARD** | Reasoning | Math problem solving | Answer correctness + reasoning quality + semantic match |

### Environment Flow

```
Task → Agent → Prompt → LLM (Real or Mock) → Grader → Score [0.0-1.0]
```

### Grading Metrics

**EASY (Summarization):**
- 50% Semantic similarity
- 30% Key concept coverage
- 20% Length appropriateness

**MEDIUM (JSON):**
- 40% JSON validity
- 40% Key-value accuracy
- 20% Structure match

**HARD (Reasoning):**
- 50% Final answer correctness
- 30% Reasoning indicators
- 20% Semantic alignment

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
environment:
  max_steps: 5                        # Max steps per episode
  difficulty_sampling: [0.33, 0.33, 0.34]  # Probability distribution

llm:
  provider: "openai"                 # "openai" or "mock"
  model: "gpt-4-turbo"
  temperature: 0.7
  max_tokens: 500

grading:
  semantic_weight: 0.4
  format_weight: 0.35
  efficiency_weight: 0.25
```

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t promptgym .
```

### Run Container (Mock LLM)

```bash
docker run -p 8000:8000 promptgym
```

### Run with OpenAI API

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="sk-your-key-here" \
  -e LLM_PROVIDER="openai" \
  promptgym
```

### Test Health

```bash
curl http://localhost:8000/health
```

---

## ☁️ Hugging Face Spaces Deployment

### Setup

1. Create a new Space on Hugging Face Hub
2. Choose "Docker" as the runtime
3. Copy `Dockerfile`, `requirements.txt`, `config.yaml` to your Space repo
4. Spaces will auto-detect and deploy

**Minimum required files:**
```
Dockerfile
requirements.txt
config.yaml
app/
  __init__.py
  main.py
  env/
  agent/
  utils/
```

---

## 📊 Project Structure

```
promptgym/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── agent/
│   │   ├── __init__.py
│   │   └── baseline_agent.py    # Baseline implementations
│   ├── env/
│   │   ├── __init__.py
│   │   ├── environment.py       # OpenEnv-compatible environment
│   │   ├── tasks.py            # Task definitions
│   │   └── grader.py           # Grading logic
│   └── utils/
│       ├── __init__.py
│       └── llm_executor.py     # LLM integration
├── scripts/
│   └── run_baseline_evaluation.py   # Evaluation script
├── config.yaml             # Configuration file
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker image definition
├── .env.example           # Environment variables template
└── README.md              # This file
```

---

## 🔑 Environment Variables

```bash
# Required for OpenAI integration
OPENAI_API_KEY=sk-...

# Optional configuration
OPENAI_MODEL=gpt-4-turbo
LLM_PROVIDER=mock          # "mock" or "openai"
LOG_LEVEL=INFO
```

---

## 🚀 Production Checklist

- [ ] All 3 difficulty tasks implemented ✅
- [ ] Real LLM integration (OpenAI) ✅
- [ ] Multi-metric grading system ✅
- [ ] Adaptive baseline agent ✅
- [ ] Full OpenEnv compatibility (gym.Env) ✅
- [ ] Error handling and validation ✅
- [ ] API documentation (/docs) ✅
- [ ] Health check endpoint ✅
- [ ] Evaluation script ✅
- [ ] Docker deployment ✅
- [ ] Environment configuration ✅
- [ ] Logging system ✅
- [ ] Thread safety (async support) ✅

---

## 🧪 Testing

### Manual API Testing

```bash
# Start server
python -m uvicorn app.main:app --reload

# In another terminal, run tests
python -c "
import requests
import json

BASE = 'http://localhost:8000'

# Test health
print('Health:', requests.get(f'{BASE}/health').json())

# Test reset
reset = requests.post(f'{BASE}/reset').json()
print('Reset OK')

# Test step
step = requests.post(f'{BASE}/step', json={'prompt': 'Summarize: hello world'}).json()
print(f'Step reward: {step[\"reward\"]}')
"
```

### Evaluation Script

```bash
# Quick test with 10 episodes
python scripts/run_baseline_evaluation.py --episodes 10

# Full evaluation
python scripts/run_baseline_evaluation.py --episodes 100 --provider mock
```

---

## 🛠️ Troubleshooting

### API Connection Error

```
Error: Cannot connect to server
Solution: Make sure uvicorn is running on port 8000
```

### OpenAI API Key Error

```
Error: OPENAI_API_KEY not set
Solution: 
  1. Set environment variable: export OPENAI_API_KEY="sk-..."
  2. Or edit .env file
```

### Docker Build Fails

```
Error: ImportError: No module named 'app'
Solution: Ensure you're in the project root directory
```

---

## 📝 License

MIT (or your preferred license)

---

## 👥 Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open Pull Request

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- See HACKATHON_WORKFLOW.md for implementation guide

---

**PromptGym** - Evaluate Prompt Engineering Quality  
Built for the Hackathon 🎯
