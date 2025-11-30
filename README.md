# 🧊 GlassBox: The AI-Powered Recruitment Protocol
> "Don’t judge the code. Judge the coder."

![License: MIT](https://opensource.org/licenses/MIT)
![Python 3.9+](https://www.python.org/downloads/)
![Streamlit](https://streamlit.io)
![OpenAI](https://openai.com/)

---

## 🚨 The Problem: The "Black Box" of Hiring
In the era of ChatGPT and Copilot, the final code proves nothing. 
* Did the candidate write it, or generate it? 
* Do they understand the logic, or did they just get lucky?
* Recruiters waste hundreds of hours on interviews to find out what GlassBox reveals in 3 minutes.

## 💡 The Solution: Process Audit
GlassBox is an automated exam environment that makes the candidate's thinking process visible, measurable, and verifiable. We introduce Vocal Coding protocols combined with sensor fusion to evaluate potential, not just syntax.

---

## ⚙️ How It Works

GlassBox replaces the "silent test task" with a transparent session:

1.  🎙️ Vocal Coding: The candidate solves the task while "thinking aloud." [cite_start]The Cognitive Engine analyzes their speech for logic, clarity, and terminology[cite: 87, 88].
2.  👁️ Work Patterns (Sensors): We track the active environment. [cite_start]Is the candidate coding in the IDE or researching in the Browser?[cite: 116, 120].
3.  🧠 AI Cross-Check: The system correlates Speech (Plan) vs Action (Code). 
    * *Example:* Candidate says "I'll fix the loop" -> Candidate actually edits the loop -> High Consistency Score.
4.  🔒 Proof of Skill: The session is hashed (SHA-256). [cite_start]A PDF Certificate is generated, guaranteeing the result cannot be faked[cite: 179, 185].

---

## 📊 The Dashboard (What Recruiters See)

No more watching 1-hour videos. [cite_start]The recruiter gets a **Smart Dashboard**[cite: 149]:

### 1. The Timeline (X-Ray Vision)
A visual bar showing the exact flow of the session:
* 🟢 CODING
* 🟡 RESEARCHING (Google/StackOverflow)
* ⚪ IDLE (Stuck/Thinking)

### 2. Key Metrics
| Metric | Description | Source |
| :--- | :--- | :--- |
| 🧠 Clarity Score | Coherence, terminology, and completeness of the explanation. | LLM Analysis |
| 🛠️ Hard Score | Balance between independent coding and external research. | Window Sensor |
| ⚖️ Verdict | Math-based PASS / FAIL recommendation. | Aggregated Data |

### 3. Smart Playback (Drill-Down)
Click on any anomaly in the timeline to instantly watch that specific moment in the video recording. Context is just one click away.

---

## 💰 Business Value

### For Companies (B2B)
* Scale: Screen 1,000 candidates overnight without burning Senior Engineer hours.
* Safety: Filter out "ChatGPT-coders" before the first interview.
* Cost: The cost of one GlassBox report is <1% of the cost of a bad hire.

### For Candidates
* Fairness: Get credit for your *thought process*, even if the code isn't perfect.
* Asset: Receive a blockchain-ready Certificate with your Hard/Soft scores to prove your skills to any employer.

---

## 🛠️ Architecture & Tech Stack

[cite_start]The project is built by a cross-functional team, delivering a complete MVP in 24 hours[cite: 228].

* [cite_start]**👤 Role 1 (Core):** Orchestrator, JSON Schema Contract, SessionLogger. [cite: 58]
* [cite_start]**👤 Role 2 (AI):** Cognitive Engine (LLM Integration), Clarity Analysis. [cite: 87]
* [cite_start]**👤 Role 3 (Sensors):** Active Window Monitoring, Threading, Pattern Recognition. [cite: 116]
* [cite_start]**👤 Role 4 (UI):** Streamlit Dashboard, Plotly Visualization. [cite: 149]
* [cite_start]**👤 Role 5 (Product):** PDF Generation, SHA-256 Hashing, Business Logic. [cite: 179]

---

## 🚀 Getting Started

### Prerequisites
* Python 3.9+
* OpenAI API Key (optional for FakeLLM mode)

###
