# PromptGym Hackathon Deployment Checklist 🚀

**Pre-Submission Validation Guide**

---

## 📋 Code Quality Checklist

### Structure & Organization
- [ ] All Python files have proper docstrings (module, functions, classes)
- [ ] Type hints on all functions
- [ ] No `print()` statements (use logging instead)
- [ ] No hardcoded values (use config.yaml)
- [ ] Constants in UPPERCASE_WITH_UNDERSCORES
- [ ] Imports organized (stdlib, third-party, local)
- [ ] No unused imports
- [ ] Max line length is reasonable (< 100 chars)

### Error Handling
- [ ] All API endpoints handle errors gracefully
- [ ] Try-catch blocks with proper logging
- [ ] Meaningful error messages
- [ ] Invalid inputs return 400 status (Bad Request)
- [ ] Server errors return 500 status
- [ ] No unhandled exceptions

### Logging
- [ ] Logging configured in main.py
- [ ] Info level for important operations
- [ ] Debug level for detailed tracing
- [ ] Error level for failures
- [ ] No sensitive data in logs

---

## 🎯 Functionality Checklist

### Environment Implementation
- [ ] Inherits from `gym.Env`
- [ ] Has `action_space` defined
- [ ] Has `observation_space` defined
- [ ] `reset()` returns (observation, info)
- [ ] `step()` returns (observation, reward, terminated, truncated, info)
- [ ] Reward is float between 0.0 and 1.0
- [ ] Supports seed parameter for reproducibility
- [ ] Has `state()` method for API compatibility

### Tasks
- [ ] Exactly 3+ EASY tasks implemented
- [ ] Exactly 3+ MEDIUM tasks implemented
- [ ] Exactly 3+ HARD tasks implemented
- [ ] Each task has: difficulty, task_description, input_data, expected_output
- [ ] Tasks are realistic (not games)
- [ ] Each difficulty increases in complexity

### Grading System
- [ ] Grader returns float 0.0-1.0
- [ ] Multi-metric approach (not just substring matching)
- [ ] EASY: Semantic similarity + key concepts + length
- [ ] MEDIUM: JSON validity + key-value accuracy + structure
- [ ] HARD: Answer correctness + reasoning quality + semantic match
- [ ] Grading is fair and consistent

### API Endpoints
- [ ] ✅ `GET /health` - Health check works
- [ ] ✅ `POST /reset` - Returns new observation
- [ ] ✅ `POST /step` - Executes prompt, returns reward
- [ ] ✅ `GET /state` - Returns current state
- [ ] ✅ `GET /metrics` - Returns episode metrics
- [ ] ✅ `GET /tasks` - Lists available tasks
- [ ] All endpoints have proper validation
- [ ] All endpoints are documented in README

### LLM Integration
- [ ] OpenAI API integration implemented
- [ ] Mock executor exists for testing without API calls
- [ ] API key loaded from environment variable
- [ ] Timeout set (10 seconds)
- [ ] Retry logic implemented
- [ ] Error handling for API failures
- [ ] Can switch providers via config

### Baseline Agent
- [ ] BaselineAgent class implemented
- [ ] AdaptiveBaselineAgent class implemented
- [ ] Can generate different prompt strategies
- [ ] Tracks history and performance
- [ ] Learns from feedback
- [ ] No hardcoded prompts (uses templates)

### Evaluation Script
- [ ] Evaluation script works standalone
- [ ] Runs multiple episodes (default 50)
- [ ] Tracks metrics properly
- [ ] Generates summary report
- [ ] Handles errors gracefully
- [ ] Can use mock or OpenAI provider

---

## 📦 Deployment Checklist

### Python Environment
- [ ] requirements.txt has all dependencies with versions
- [ ] No unused dependencies
- [ ] Virtual environment setup tested
- [ ] Can install: `pip install -r requirements.txt`
- [ ] No system-level dependencies needed (except Python 3.11+)

### Configuration Files
- [ ] config.yaml exists with all settings
- [ ] .env.example provides template
- [ ] No actual API keys committed
- [ ] Default values work without .env
- [ ] Can run: `LLM_PROVIDER=mock python -m uvicorn app.main:app`

### Docker Setup
- [ ] Dockerfile builds successfully
- [ ] Base image is python:3.11-slim (or similar)
- [ ] All dependencies installed in Dockerfile
- [ ] Expose port 8000
- [ ] Health check configured
- [ ] WORKDIR set to /app
- [ ] Entry point is uvicorn command
- [ ] Build test: `docker build -t promptgym .`
- [ ] Run test: `docker run -p 8000:8000 promptgym`
- [ ] Health endpoint accessible after 40s

### Documentation
- [ ] README.md comprehensive and updated
- [ ] API examples present (cURL and Python)
- [ ] Quick start section
- [ ] Project overview clear
- [ ] Architecture diagram or explanation
- [ ] Environment variables documented
- [ ] Deployment instructions included
- [ ] Troubleshooting section present

### File Structure
```
✓ promptgym/
  ✓ app/
    ✓ __init__.py
    ✓ main.py (FastAPI app)
    ✓ agent/
      ✓ __init__.py
      ✓ baseline_agent.py
    ✓ env/
      ✓ __init__.py
      ✓ environment.py
      ✓ tasks.py
      ✓ grader.py
    ✓ utils/
      ✓ __init__.py
      ✓ llm_executor.py
  ✓ scripts/
    ✓ run_baseline_evaluation.py
    ✓ validate_setup.py
  ✓ config.yaml
  ✓ requirements.txt
  ✓ Dockerfile
  ✓ .env.example
  ✓ .gitignore
  ✓ README.md
  ✓ HACKATHON_WORKFLOW.md
  ✓ DEPLOYMENT_CHECKLIST.md
```

---

## 🧪 Validation Steps

### Step 1: Local Testing
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Validate setup
python scripts/validate_setup.py

# Should show: ✓ All validation checks passed!
```

### Step 2: API Testing
```bash
# Terminal 1
python -m uvicorn app.main:app --reload

# Terminal 2 (test endpoints)
curl http://localhost:8000/health
curl -X POST http://localhost:8000/reset
curl http://localhost:8000/tasks
```

### Step 3: Evaluation Testing
```bash
python scripts/run_baseline_evaluation.py --episodes 10 --provider mock

# Should show: ✓ All validation checks passed!
```

### Step 4: Docker Testing
```bash
docker build -t promptgym .
docker run -p 8000:8000 promptgym

# In another terminal
sleep 45  # Wait for health check
curl http://localhost:8000/health
```

### Step 5: Final Validation
```bash
# Ensure no errors in logs
docker logs $(docker ps -q --filter ancestor=promptgym)

# Test all endpoints
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/tasks
curl -X POST http://localhost:8000/reset
curl -X POST http://localhost:8000/step -H "Content-Type: application/json" -d '{"prompt": "test"}'
```

---

## ✅ Hackathon Submission Checklist

### Before Submitting
- [ ] All tests pass locally
- [ ] `validate_setup.py` shows all checks passing
- [ ] Docker builds and runs without errors
- [ ] Evaluation script runs to completion
- [ ] README is clear and complete
- [ ] No API keys committed
- [ ] No sensitive data in code
- [ ] Project compiles on fresh clone

### Repository State
- [ ] No uncommitted changes
- [ ] Git history is clean
- [ ] `.gitignore` properly configured
- [ ] README.md is in root directory
- [ ] Dockerfile is in root directory
- [ ] requirements.txt is in root directory

### Final Checklist
- [ ] Project name: PromptGym ✓
- [ ] Type: OpenEnv-compatible backend ✓
- [ ] Tasks: 3 difficulty levels (EASY, MEDIUM, HARD) ✓
- [ ] Grading: Multi-metric scoring [0.0-1.0] ✓
- [ ] Agent: Baseline with adaptive capability ✓
- [ ] LLM: Real + Mock integration ✓
- [ ] Deployment: Docker + HF Spaces ready ✓
- [ ] Documentation: Complete README ✓
- [ ] Evaluation: Baseline script included ✓

---

## 🚀 Deployment to Hugging Face Spaces

### Step 1: Create Space
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose Docker runtime
4. Create private/public

### Step 2: Push Code
```bash
git clone https://huggingface.co/spaces/your-username/promptgym
cd promptgym

# Copy files
cp -r ../your-local-promptgym/* .
git add .
git commit -m "Initial PromptGym submission"
git push
```

### Step 3: Verify Deployment
- Wait 5-10 minutes for build
- Check "App" tab shows running app
- Test endpoints via Spaces UI

---

## 🎯 Quick Win Strategies

### For Maximum Hackathon Score

1. **Clarity of Architecture**
   - Clear separation of concerns
   - Well-documented code
   - Obvious task/grader/agent flow

2. **Task Quality**
   - Real-world scenarios
   - Varied within each difficulty
   - Clear success criteria

3. **Grading Sophistication**
   - Multi-metric approach
   - Task-specific logic
   - Fair scoring

4. **Agent Innovation**
   - More than just template substitution
   - Shows learning capability
   - Measurable improvement

5. **Overall Polish**
   - Professional documentation
   - Zero console errors
   - Smooth deployment

---

## ⚠️ Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| `ImportError: No module named 'app'` | Run from project root |
| `OPENAI_API_KEY not set` | Set env var or use mock provider |
| Docker build fails | Check `pip` can access PyPI |
| API returns 500 error | Check logs with `docker logs` |
| Grader always returns 1.0 or 0.0 | Implement multi-metric logic |
| Agent doesn't learn | Implement adaptive strategy |

---

## 📞 Pre-Submission Questions

- [ ] Is the project real-world focused? Yes
- [ ] Can it run without external dependencies? Yes (except OpenAI API)
- [ ] Is error handling comprehensive? Yes
- [ ] Does it match OpenEnv specs? Yes
- [ ] Is the baseline agent non-trivial? Yes
- [ ] Can it be deployed on HF Spaces? Yes
- [ ] Is documentation clear? Yes

---

**Submission Status**: Ready for Hackathon 🎉

All checklists passed → Proceed to submission!
