<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Syne&weight=800&size=42&pause=1000&color=7C3AED&center=true&vCenter=true&width=600&height=80&lines=PromptGym+%F0%9F%8E%AF;Train+Your+Prompts." alt="PromptGym" />

<p align="center">
  <img src="https://img.shields.io/badge/OpenEnv-6%2F6%20Passing-10b981?style=for-the-badge&logo=checkmarx&logoColor=white" />
  <img src="https://img.shields.io/badge/HuggingFace-Live-FF9D00?style=for-the-badge&logo=huggingface&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-Server-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Deployed-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</p>

<p align="center">
  <a href="https://saranshhyadov-promptgym.hf.space"><strong>🚀 Live Demo</strong></a> ·
  <a href="https://huggingface.co/spaces/saranshhyadav/promptgym"><strong>🤗 HF Space</strong></a> ·
  <a href="https://saranshhyadov-promptgym.hf.space/health"><strong>💚 Health Check</strong></a>
</p>

<br/>

> **A fully OpenEnv-compliant prompt engineering evaluation environment.**
> Built for the Scaler × Meta × HuggingFace OpenEnv Hackathon 2026.

</div>

---

## 🏆 Submission Status

<div align="center">

| Check | Status |
|---|---|
| OpenEnv Reset (POST OK) | ✅ Passing |
| Dockerfile at repo root | ✅ Passing |
| inference.py at repo root | ✅ Passing |
| openenv validate | ✅ 6/6 Passing |

</div>

---

## 📊 Reward Scores

<div align="center">

| Difficulty | Score | Target |
|---|---|---|
| 🟢 Easy | **0.930** | ≥ 0.9500 |
| 🟡 Medium | **0.990** | ≥ 0.9429 |
| 🔴 Hard | **0.930** | ≥ 0.6923 |
| ⭐ Overall | **0.923** | ≥ 0.8617 |

</div>

---

## 🧠 What is PromptGym?

PromptGym is a **prompt engineering evaluation environment** that follows the [OpenEnv](https://openenv.dev) standard — a universal protocol for AI training environments.

It works like a gym for AI agents:

- 🤖 The **agent** is the student
- 📝 The **task** is a prompt engineering challenge
- 🎯 The **reward model** is the trainer that scores submissions
- 🔁 The agent **iterates and improves** its prompts over time

Any AI agent or tool can connect, receive tasks, submit prompts, and get scored — all via a clean REST API.

---

## ⚙️ How It Works
```
Agent                          PromptGym Server
  │                                   │
  │──── POST /reset ─────────────────▶│  Start new episode
  │◀─── {session_id, observation} ────│  Get task + session
  │                                   │
  │──── POST /step {prompt} ─────────▶│  Submit your prompt
  │◀─── {reward: 0.94, done, state} ──│  Get scored instantly
  │                                   │
  │──── POST /step {better prompt} ──▶│  Try again, improve
  │◀─── {reward: 0.98, done, state} ──│  Higher score!
  │                                   │
  │──── GET /state/{session_id} ─────▶│  Check full history
  │◀─── {attempts, best_score, ...} ──│
```

### Step by Step

**1️⃣ Reset — Start a session**
```bash
POST /reset
→ { "session_id": "abc-123", "observation": { "task": "Summarize a news article", "difficulty": "MEDIUM" } }
```

**2️⃣ Step — Submit a prompt**
```bash
POST /step
{ "session_id": "abc-123", "action": { "prompt": "Summarize in 3 bullet points focusing on key facts..." } }
→ { "reward": 0.94, "done": false, "observation": {...}, "state": { "attempts": 1, "best_score": 0.94 } }
```

**3️⃣ Score — Reward model evaluates**

The scorer rates your prompt on:
- ✅ Clarity of instruction
- ✅ Specificity and detail
- ✅ Structural quality
- ✅ Task alignment
- ✅ Conciseness

**4️⃣ Iterate — Get better**

Agent sees score → refines prompt → submits again → score improves 📈

---

## 🔌 API Reference

| Method | Endpoint | Description | Response |
|---|---|---|---|
| `GET` | `/health` | Health check | `{"status":"healthy","version":"1.0.0"}` |
| `GET` | `/` | Root | `{"name":"PromptGym","status":"running"}` |
| `GET` | `/metadata` | OpenEnv metadata | Full metadata JSON |
| `GET` | `/schema` | JSON schema | Request/response schemas |
| `POST` | `/reset` | Start new episode | `{session_id, observation}` |
| `POST` | `/step` | Submit prompt action | `{reward, done, observation, state}` |
| `POST` | `/mcp` | JSON-RPC MCP stub | `{"jsonrpc":"2.0","result":{"status":"ok"}}` |
| `GET` | `/state` | Global state | `{}` |
| `GET` | `/state/{id}` | Session state | Full session object |

---

## 🗂️ Project Structure
```
scaler-hackathon/
├── server/
│   ├── app.py              ← All 9 API endpoints (FastAPI)
│   └── __init__.py
├── app/                    ← Task definitions per difficulty
├── scorer/
│   └── reward_model.py     ← Scores prompts 0.0 → 1.0
├── agent/                  ← Agent helpers
├── models.py               ← Pydantic data models
├── inference.py            ← Evaluation loop runner
├── client.py               ← HTTP client helper
├── start.py                ← Entry point → 0.0.0.0:7860
├── openenv.yaml            ← OpenEnv compliance declaration
├── requirements.txt        ← Python dependencies
└── Dockerfile              ← python:3.11-slim, port 7860
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| 🐍 Python 3.11 | Core language |
| ⚡ FastAPI | REST API framework |
| 🦄 Uvicorn | ASGI server |
| 🐳 Docker | Containerized deployment |
| 🤗 HuggingFace Spaces | Public hosting |
| 🏋️ OpenEnv | Environment standard |
| 🔗 MCP Protocol | JSON-RPC AI tool integration |
| 📊 Custom Reward Model | Prompt quality scoring |

---

## 🚀 Quick Start
```bash
# Clone the repo
git clone https://github.com/Inexpert-trifler/Scaler_Hackathon
cd Scaler_Hackathon

# Install dependencies
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run locally
python start.py

# Validate OpenEnv compliance
openenv validate http://localhost:7860
# Expected: 6/6 PASSING ✅
```

**Or run with Docker:**
```bash
docker build -t promptgym .
docker run -p 7860:7860 promptgym
```

---

## 🌐 Deployment

PromptGym runs on HuggingFace Spaces via Docker:
```
Local Code → git push → HuggingFace Space → Docker Build → Live at 0.0.0.0:7860
```

The `Dockerfile` uses `python:3.11-slim`, installs all dependencies, and starts the server via `python start.py` bound to port 7860.

---

## 📁 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | Server bind host |
| `PORT` | `7860` | Server port |
| `LLM_MODE` | `mock` | LLM backend mode |
| `USE_TORCH_SCORER` | `false` | Enable torch-based scoring |
| `PYTHONUNBUFFERED` | `1` | Unbuffered Python output |

---

## 🏅 Hackathon

| Field | Value |
|---|---|
| Competition | Scaler × Meta × HuggingFace OpenEnv Hackathon |
| Deadline | April 8, 2026, 11:59 PM IST |
| Results | April 10, 2026 |
| HF Space | [saranshhyadav/promptgym](https://huggingface.co/spaces/saranshhyadav/promptgym) |
| GitHub | [Inexpert-trifler/Scaler_Hackathon](https://github.com/Inexpert-trifler/Scaler_Hackathon) |

---

<div align="center">

Made with 🎯 by **saranshhyadav**

⭐ Star this repo if you found it useful!

</div>
