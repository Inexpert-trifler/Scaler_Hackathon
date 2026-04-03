---
title: PromptGym
emoji: 🎯
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
tags:
  - openenv
pinned: false
---

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
  <a href="https://saranshhyadav-promptgym.hf.space"><strong>🚀 Live Demo</strong></a> ·
  <a href="https://huggingface.co/spaces/saranshhyadav/promptgym"><strong>🤗 HF Space</strong></a> ·
  <a href="https://saranshhyadav-promptgym.hf.space/health"><strong>💚 Health Check</strong></a>
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

## 🧠 What is PromptGym?

PromptGym is a **prompt engineering evaluation environment** that follows the [OpenEnv](https://openenv.dev) standard — a universal protocol for AI training environments.

It works like a gym for AI agents:

- 🤖 The **agent** is the student
- 📝 The **task** is a prompt engineering challenge
- 🎯 The **reward model** is the trainer that scores submissions
- 🔁 The agent **iterates and improves** its prompts over time

Any AI agent or tool can connect, receive tasks, submit prompts, and get scored — all via a clean REST API.

---

## 🚀 Quick Start

### Installation

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
./venv/bin/openenv validate http://localhost:7860
```

---

## 🤖 Baseline Agent Evaluation

To evaluate your baseline agent, ensure you have set your `HF_TOKEN` in your environment, then run:

```bash
python inference.py
```

It will produce logs in the mandatory format:
```
[START] task=promptgym-easy-1 env=promptgym model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action='...' reward=0.85 done=true error=null
[END] success=true steps=1 score=0.850 rewards=0.85
```

---

## 🏗️ Architecture & Scoring

### Blended Reward Model
The environment features a **blended reward system** combining:
1. **Heuristic Grader**: Keyword coverage, token F1 similarity, and length penalties.
2. **Torch Scorer**: An MLP-based reward model that predicts "naturalness" and adherence to instructions based on extracted prompt features.

### Task Difficulty
- **🟢 EASY (Summarization)**: Focuses on capturing key ideas concisely.
- **🟡 MEDIUM (JSON Conversion)**: Requires strict formatting and data integrity.
- **🔴 HARD (Reasoning)**: Demands step-by-step logic and final answer accuracy.

---

## 🔌 API Reference

| Method | Endpoint | Description | Response |
|---|---|---|---|
| `GET` | `/health` | Health check | `{"status":"healthy","version":"1.0.0"}` |
| `GET` | `/metadata` | OpenEnv metadata | Full metadata JSON |
| `POST` | `/reset` | Start new episode | `{session_id, observation}` |
| `POST` | `/step` | Submit prompt action | `{reward, done, observation, state}` |
| `GET` | `/state/{id}` | Session state | Full session object |

---

## 🗂️ Project Structure
```
scaler-hackathon/
├── server/
│   ├── app.py              ← All API endpoints (FastAPI)
│   └── environment.py      ← OpenEnv Environment class
├── app/
│   ├── tasks/              ← Task JSON definitions
│   └── grader.py           ← Multi-signal grading logic
├── scorer/
│   └── reward_model.py     ← PyTorch-based neural scorer
├── models.py               ← Pydantic data models
├── inference.py            ← Evaluation loop runner (OpenAI client)
├── start.py                ← Server entry point (Port 7860)
├── openenv.yaml            ← OpenEnv compliance manifest
├── Dockerfile              ← Containerization spec
└── README.md               ← This file
```

---

<div align="center">

Made with 🎯 by **saranshhyadav** for the **Scaler OpenEnv Hackathon**

⭐⭐⭐

</div>
