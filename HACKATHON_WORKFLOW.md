# PromptGym: Complete Hackathon Workflow 🚀

**Status**: Production-Ready Build Guide  
**Difficulty**: Intermediate → Advanced  
**Time Estimate**: 4-6 hours with AI tools  

---

## 📊 Executive Summary

Your PromptGym project is a **meta-evaluation environment** where an AI agent generates prompts to solve tasks. This guide transforms it from prototype to production-ready submission by:

1. ✅ Enhancing OpenEnv compatibility
2. ✅ Replacing mock LLM with real API (OpenAI/Anthropic)
3. ✅ Implementing robust grading (semantic similarity, format validation)
4. ✅ Building sophisticated baseline agent
5. ✅ Creating evaluation metrics dashboard
6. ✅ Preparing Docker deployment
7. ✅ Documenting for Hugging Face Spaces

---

## 🏗️ PHASE 1: Architecture Review & Improvements

### 1.1 Current Issues

| Issue | Impact | Fix |
|-------|--------|-----|
| Grader is substring-based | Unfairly penalizes synonyms | Use semantic similarity (difflib, embeddings) |
| Mock LLM always succeeds | Doesn't test prompt quality | Integrate real LLM API |
| No action/observation spaces | Not fully OpenEnv compatible | Add proper space definitions |
| Baseline agent is hardcoded | Cannot learn/improve | Implement adaptive prompting |
| No error handling | Crashes on invalid input | Add validation layer |
| No metrics tracking | Can't evaluate performance | Add prometheus metrics |
| Missing environment limits | Unlimited steps possible | Add max_steps configuration |

### 1.2 Required Architecture Changes

```
Current Flow:
Task → Agent → Prompt → Mock LLM → Grader → Score

New Flow:
Task → Agent → Prompt → Real LLM → Grader → Score → Metrics → Dashboard
```

### 1.3 Key Architectural Decisions

**A. Environment State Representation**
```python
# OLD: Raw dict with mixed types
state_data: dict[str, Any]

# NEW: Proper observation space
observation_space = Dict({
    'task_description': Text,
    'input_data': Text,
    'previous_prompts': List[Text],  # History
    'previous_scores': List[Float],  # Track improvement
    'step': Int,  # Current step
})

action_space = Dict({
    'prompt': Text,
})
```

**B. Grading Strategy (Multi-Metric)**
```
Final Score = 0.3 * semantic_score + 0.4 * format_score + 0.3 * efficiency_score

- semantic_score: Does output match expected meaning? (0-1)
- format_score: Is format correct? (0-1)  
- efficiency_score: How efficient is the prompt? (0-1)
```

**C. Configuration Management**
```python
# Add config.yaml (not hardcoded)
llm:
  provider: "openai"  # or "anthropic"
  model: "gpt-4-turbo"
  api_key: "${OPENAI_API_KEY}"
  
environment:
  max_steps_per_episode: 5
  task_difficulty_weights: [0.3, 0.5, 0.2]  # easy, medium, hard
  
grading:
  semantic_weight: 0.3
  format_weight: 0.4
  efficiency_weight: 0.3
```

---

## 🧠 PHASE 2: Enhanced Grading Logic

### 2.1 Multi-Level Grading Strategy

**For EASY Tasks (Summarization)**
```python
def grade_summarization(expected, output):
    # 1. Check key concepts present
    key_concepts = extract_noun_phrases(expected)
    coverage = sum(1 for c in key_concepts if c in output) / len(key_concepts)
    
    # 2. Check length is reasonable (5-15 words)
    word_count = len(output.split())
    length_score = 1.0 if 5 <= word_count <= 15 else 0.5
    
    # 3. Semantic similarity using embeddings
    semantic_sim = embedding_similarity(expected, output)
    
    return 0.2*coverage + 0.3*length_score + 0.5*semantic_sim
```

**For MEDIUM Tasks (JSON Conversion)**
```python
def grade_json(expected, output):
    try:
        parsed = json.loads(output)
        expected_parsed = json.loads(expected)
    except:
        return 0.0  # Invalid JSON
    
    # Check all required keys present
    keys_match = set(parsed.keys()) == set(expected_parsed.keys())
    if not keys_match:
        return 0.3  # Partial credit
    
    # Check value accuracy
    accuracy = sum(
        1 for k in parsed.keys() 
        if str(parsed[k]).lower() == str(expected_parsed[k]).lower()
    ) / len(parsed)
    
    return 0.7 if keys_match else 0.0 + 0.3*accuracy
```

**For HARD Tasks (Reasoning)**
```python
def grade_reasoning(expected, output):
    # 1. Check if final answer is contained
    answer_correct = expected.lower() in output.lower()
    
    # 2. Check for reasoning indicators
    reasoning_quality = 0.0
    if any(word in output.lower() for word in ['step', 'therefore', 'thus', 'because']):
        reasoning_quality = 0.5
    if any(word in output.lower() for word in ['first', 'second', 'third', 'finally']):
        reasoning_quality = 1.0
    
    # 3. Semantic match
    semantic_sim = embedding_similarity(expected, output)
    
    return 0.6*answer_correct + 0.2*reasoning_quality + 0.2*semantic_sim
```

### 2.2 Implementation: Use SequenceMatcher + Optional Embeddings

**Simple (No API calls):**
```python
from difflib import SequenceMatcher

def semantic_similarity_simple(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()
```

**Advanced (With embeddings - optional):**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight

def semantic_similarity_embeddings(a: str, b: str) -> float:
    emb_a = model.encode(a, convert_to_tensor=True)
    emb_b = model.encode(b, convert_to_tensor=True)
    return float((emb_a @ emb_b) / (norm(emb_a) * norm(emb_b)))
```

---

## 🤖 PHASE 3: Real LLM Integration

### 3.1 Recommended Setup

**Provider**: OpenAI (most reliable, best for hackathons)  
**Model**: `gpt-4-turbo` (best for prompt generation tasks)  
**Fallback**: `gpt-3.5-turbo` (faster, cheaper)

### 3.2 Implementation Structure

```python
# llm_executor.py - UPDATED VERSION

from abc import ABC, abstractmethod
import openai

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def execute(self, prompt: str, input_data: str) -> str:
        pass

class OpenAIExecutor(LLMProvider):
    """OpenAI GPT-4 executor."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def execute(self, prompt: str, input_data: str) -> str:
        """Execute prompt via OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Respond concisely."
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nData: {input_data}"
                    }
                ],
                temperature=0.7,
                max_tokens=500,
                timeout=10  # Prevent hanging
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LLM Error: {str(e)}"

class MockExecutor(LLMProvider):
    """Fallback mock executor for testing."""
    # Keep existing mock for testing without API calls
```

### 3.3 Configuration File (config.yaml)

```yaml
environment:
  max_steps: 5
  time_limit_seconds: 30
  difficulty_sampling: [0.33, 0.33, 0.34]  # Easy, Medium, Hard

llm:
  provider: "openai"
  model: "gpt-4-turbo"
  temperature: 0.7
  max_tokens: 500
  timeout: 10
  retry_attempts: 2

grading:
  semantic_weight: 0.4
  format_weight: 0.35
  efficiency_weight: 0.25
  use_embeddings: false  # Set true if using sentence-transformers

logging:
  level: "INFO"
  log_file: "logs/promptgym.log"
```

---

## ⚙️ PHASE 4: OpenEnv Compatibility

### 4.1 Required OpenEnv Compliance

```python
# environment.py - ENHANCED VERSION

from gym import Env, spaces
import numpy as np

class PromptGymEnv(Env):
    """PromptGym environment with full OpenEnv compatibility."""
    
    metadata = {'render_modes': ['human']}
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__()
        self.config = load_config(config_path)
        self.max_steps = self.config['environment']['max_steps']
        
        # Define action and observation spaces
        self.action_space = spaces.Dict({
            'prompt': spaces.Text(max_length=1000)
        })
        
        self.observation_space = spaces.Dict({
            'task_description': spaces.Text(max_length=500),
            'input_data': spaces.Text(max_length=2000),
            'step': spaces.Box(low=0, high=self.max_steps, shape=(1,)),
            'previous_scores': spaces.Box(low=0.0, high=1.0, shape=(self.max_steps,)),
        })
        
    def reset(self, seed=None, options=None):
        """Reset environment."""
        super().reset(seed=seed)
        # Load new task
        # Return observation dict matching observation_space
        return obs, info
    
    def step(self, action):
        """Execute step."""
        # Validate action matches action_space
        # Return obs, reward, terminated, truncated, info
        return obs, reward, terminated, truncated, info
    
    def render(self):
        """Optional rendering."""
        pass
    
    def close(self):
        """Cleanup."""
        pass
```

### 4.2 Full OpenEnv Checklist

- ✅ Inherits from `gym.Env`
- ✅ Defines `action_space` with proper spaces
- ✅ Defines `observation_space` with proper spaces
- ✅ `reset()` returns `(obs, info)` tuple
- ✅ `step()` returns `(obs, reward, terminated, truncated, info)` tuple
- ✅ Reward is a scalar float
- ✅ `terminated` and `truncated` are booleans
- ✅ Handles `seed` parameter for reproducibility
- ✅ Proper metadata dictionary

---

## 🧪 PHASE 5: Baseline Agent Evolution

### 5.1 Baseline Agent Strategies

**Strategy 1: Template-Based (Simple)**
```python
def baseline_agent_template(state):
    """Generate prompts using task-specific templates."""
    task = state['task_description'].lower()
    
    templates = {
        'summarize': "Summarize the following text in one sentence: {input}",
        'json': "Convert the following text to JSON format: {input}",
        'reason': "Solve this step-by-step: {input}",
    }
    
    for key, template in templates.items():
        if key in task:
            return {
                'prompt': template.format(input=state['input_data'])
            }
```

**Strategy 2: Few-Shot Examples (Better)**
```python
def baseline_agent_fewshot(state):
    """Generate prompts with few-shot examples."""
    task = state['task_description'].lower()
    examples = {
        'summarize': """
            Here are examples of good summaries:
            - Long text → One sentence capturing main idea
            - Technical text → Key concept in simple words
            
            Now summarize: {input}
        """,
        'json': """
            Convert to JSON with clear key-value pairs:
            Example: "Alice, 30, NYC" → {"name": "Alice", "age": 30, "city": "NYC"}
            
            Convert: {input}
        """
    }
```

**Strategy 3: Adaptive (Best)**
```python
class AdaptiveBaselineAgent:
    """Learns what types of prompts work best."""
    
    def __init__(self):
        self.prompt_history = []
        self.score_history = []
        self.prompt_templates = {}
    
    def get_action(self, state):
        """Adapt prompts based on previous performance."""
        if self.score_history:
            best_idx = np.argmax(self.score_history)
            best_prompt = self.prompt_history[best_idx]
            
            # Mutate best prompt slightly
            return self._mutate_prompt(best_prompt)
        else:
            # First attempt
            return self._initial_prompt(state)
    
    def update(self, prompt, score):
        """Track prompt effectiveness."""
        self.prompt_history.append(prompt)
        self.score_history.append(score)
```

### 5.2 Evaluation Script

```python
# scripts/run_baseline_evaluation.py

def evaluate_baseline(num_episodes: int = 50):
    """Run baseline agent and collect metrics."""
    env = PromptGymEnv()
    agent = AdaptiveBaselineAgent()
    
    results = {
        'episode_rewards': [],
        'difficulty_performance': {'EASY': [], 'MEDIUM': [], 'HARD': []},
        'prompt_length_stats': [],
    }
    
    for episode in range(num_episodes):
        obs, info = env.reset()
        difficulty = current_task['difficulty']
        episode_reward = 0
        
        for step in range(env.max_steps):
            action = agent.get_action(obs)
            obs, reward, terminated, truncated, info = env.step(action)
            
            results['prompt_length_stats'].append(len(action['prompt'].split()))
            results['difficulty_performance'][difficulty].append(reward)
            episode_reward += reward
            
            agent.update(action['prompt'], reward)
            
            if terminated or truncated:
                break
        
        results['episode_rewards'].append(episode_reward)
    
    # Generate report
    print(f"Average Reward: {np.mean(results['episode_rewards']):.3f}")
    for diff in ['EASY', 'MEDIUM', 'HARD']:
        avg = np.mean(results['difficulty_performance'][diff])
        print(f"{diff}: {avg:.3f}")
```

---

## 🐳 PHASE 6: Docker & Deployment Preparation

### 6.1 Enhanced Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY config.yaml .
COPY .env .env 2>/dev/null || true

# Expose API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Updated requirements.txt

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
openai==1.3.9
anthropic==0.7.0
python-dotenv==1.0.0
gym==0.26.2
numpy==1.26.2
scipy==1.11.4
sentence-transformers==2.2.2
pyyaml==6.0.1
prometheus-client==0.19.0
```

### 6.3 Hugging Face Spaces Deployment

**Step 1**: Create Hugging Face Space (Settings → Space Settings)
**Step 2**: Choose "Docker" as runtime
**Step 3**: Add `Dockerfile` to repo
**Step 4**: Spaces auto-detects and deploys

**Min. required files:**
```
Dockerfile
app/
requirements.txt
config.yaml
```

---

## 📊 PHASE 7: Metrics & Monitoring

### 7.1 Evaluation Metrics

```python
# metrics.py

class PromptGymMetrics:
    def __init__(self):
        self.metrics = {
            'episode_rewards': [],
            'prompt_tokens': [],
            'grader_scores': [],
            'task_difficulty': [],
            'api_latency': [],
        }
    
    def record_episode(self, episode_data):
        """Record metrics from an episode."""
        for key, value in episode_data.items():
            if key in self.metrics:
                self.metrics[key].append(value)
    
    def get_summary(self):
        """Generate summary report."""
        return {
            'avg_reward': np.mean(self.metrics['episode_rewards']),
            'max_reward': np.max(self.metrics['episode_rewards']),
            'improvement_rate': self._calculate_improvement(),
            'success_rate': self._calculate_success_rate(),
            'avg_api_latency': np.mean(self.metrics['api_latency']),
        }
```

### 7.2 Prometheus Metrics (Optional but Recommended)

```python
from prometheus_client import Counter, Histogram, Gauge

episodes_total = Counter('episodes_total', 'Total episodes')
reward_histogram = Histogram('episode_reward', 'Episode reward distribution')
api_latency_histogram = Histogram('api_latency_seconds', 'API latency')
```

---

## ☁️ PHASE 8: Hacking Success Strategy

### 8.1 Hackathon Evaluation Criteria (Typical)

| Criteria | Weight | How to Win |
|----------|--------|-----------|
| **Functionality** | 25% | All 3 tasks work, API responds reliably |
| **Code Quality** | 20% | Clean architecture, good documentation |
| **Innovation** | 20% | Adaptive agent, advanced grading |
| **Completeness** | 20% | README, Docker, baseline, metrics |
| **Deployment** | 15% | Works on HF Spaces, no setup needed |

### 8.2 Winning Checklist

**Before Submission:**

- [ ] All 3 difficulty tasks implemented
- [ ] Real LLM integration (not mock)
- [ ] Grading uses multiple metrics (not just substring match)
- [ ] Baseline agent can improve over time (adaptive)
- [ ] OpenEnv fully compatible (gym.Env with proper spaces)
- [ ] README explains project clearly
- [ ] Dockerfile builds and runs successfully
- [ ] API endpoints have error handling
- [ ] Config file for easy customization
- [ ] Evaluation script with metrics
- [ ] No hardcoded API keys (use env vars)
- [ ] Project description matches submission criteria
- [ ] Can run: `docker build . && docker run -p 8000:8000 promptgym`

### 8.3 Quick Wins (Do These First)

1. **Add Health Check Endpoint**
   ```python
   @app.get("/health")
   def health():
       return {"status": "ok"}
   ```

2. **Add Metrics Endpoint**
   ```python
   @app.get("/metrics")
   def get_metrics():
       return env.get_metrics()
   ```

3. **Add More Task Variants**
   - 4-5 tasks per difficulty level
   - Real-world scenarios
   - Varied input/output formats

4. **Improve Baseline Agent**
   - Few-shot examples
   - Chain-of-thought prompting
   - Adaptive based on feedback

---

## ⚠️ PHASE 9: Common Mistakes to AVOID

### 9.1 Disqualification Risks

| ❌ Mistake | 🚀 Solution |
|-----------|----------|
| **Hardcoded API keys** | Use `.env` file + `python-dotenv` |
| **No error handling** | Add try-catch, return 500 errors gracefully |
| **Mock LLM in final submit** | Replace with real API before submission |
| **Grading too simple** | Multi-metric approach (semantic + format) |
| **No documentation** | Detailed README with examples |
| **Docker doesn't work** | Test: Build, run, call API locally first |
| **Scores always 1.0 or 0.0** | Implement nuanced grading (0.0-1.0 range) |
| **Agent doesn't learn** | Implement adaptive strategy |
| **Missing OpenEnv features** | Use gym.Env, define spaces properly |
| **Broken on startup** | Test fresh clone before submitting |

### 9.2 LLM Integration Gotchas

```python
# ❌ WRONG
response = openai.ChatCompletion.create(...)  # Old API

# ✅ CORRECT
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(...)
```

```python
# ❌ WRONG: Blocking forever
response = client.chat.completions.create(..., timeout=None)

# ✅ CORRECT: Set timeout
response = client.chat.completions.create(..., timeout=10)
```

```python
# ❌ WRONG: Exposing key
print(os.environ['OPENAI_API_KEY'])

# ✅ CORRECT: Use only when configured
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set")
```

---

## 🚀 PHASE 10: Final Pre-Submission Checklist

### 10.1 Code Quality Checklist

- [ ] No `print()` statements (use logging)
- [ ] All functions have docstrings
- [ ] Type hints on all functions
- [ ] No unused imports
- [ ] Constants in UPPERCASE
- [ ] Error messages are descriptive
- [ ] No hardcoded values (use config)

### 10.2 Functionality Checklist

- [ ] `/reset` endpoint works
- [ ] `/step` endpoint works
- [ ] `/state` endpoint works
- [ ] `/health` endpoint added
- [ ] Task difficulty sampling works
- [ ] All 3 difficulties can be tested
- [ ] Reward calculation is deterministic for same input
- [ ] Agent can run through full episode

### 10.3 Documentation Checklist

- [ ] README.md with setup instructions
- [ ] API documentation (request/response examples)
- [ ] Example curl commands for each endpoint
- [ ] Instructions for running evaluation script
- [ ] Deployment instructions for HF Spaces

### 10.4 Deployment Checklist

- [ ] `requirements.txt` has all dependencies
- [ ] `Dockerfile` builds successfully
- [ ] `config.yaml` has all required settings
- [ ] `.env.example` file created
- [ ] `.gitignore` excludes `.env`
- [ ] No large files (< 500MB total)
- [ ] All imports work in Docker container

### 10.5 Performance Checklist

- [ ] `/step` responds in < 5 seconds
- [ ] No memory leaks (monitor after 100 episodes)
- [ ] API handles concurrent requests (test with 5+ simultaneous)
- [ ] Batch inference for efficiency (if applicable)

---

## 📋 Quick Implementation Order

### Day 1 (2 hours)
1. Update `requirements.txt` with real dependencies
2. Refactor `grader.py` with multi-metric scoring
3. Integrate OpenAI API into `llm_executor.py`
4. Add configuration management (`config.yaml`)

### Day 2 (3 hours)
5. Enhance `environment.py` for full OpenEnv compliance
6. Improve `baseline_agent.py` with adaptive strategy
7. Create evaluation script
8. Add error handling to `main.py`

### Day 3 (2 hours)
9. Update `Dockerfile` with health checks
10. Write comprehensive `README.md`
11. Add `/health` and `/metrics` endpoints
12. Create `.env.example` file

### Final (1 hour)
13. Test everything locally with Docker
14. Verify all hackathon requirements
15. Final code cleanup and documentation
16. Deploy to test HF Space

---

## 📚 Resources

- OpenAI API: https://platform.openai.com/docs
- OpenEnv (Gym): https://gymnasium.farama.org/
- FastAPI Best Practices: https://fastapi.tiangolo.com/deployment/docker/
- HF Spaces Docker: https://huggingface.co/docs/hub/spaces-sdks-docker

---

**Next Step**: Follow Phase 1 → Phase 10 in order. Each phase has implementation details.
