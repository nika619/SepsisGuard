# ◈ SEPSISGUARD AI ◈

**Detect Deterioration. Defend Every Hour. Deliver Survival.**

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Server](https://img.shields.io/badge/MCP-Server-orange.svg)](https://modelcontextprotocol.io)

Sepsis doesn't announce itself. It creeps — a heart rate rising 8 bpm per hour, a lactate drifting from 1.8 to 3.4, a nursing note that reads "patient increasingly diaphoretic and confused." By the time traditional scoring systems trigger, the window for optimal intervention has already narrowed.

Every year, **49 million people** develop sepsis worldwide and **11 million die** — that's 1 in 5 of all global deaths. Every hour of delayed detection increases mortality by approximately **7%**.

**SepsisGuard AI** was built because rules count numbers, but survival requires reasoning.

---

## ⚠️ The Problem — Rule-Based Blindness

Current clinical systems rely on static threshold scoring:

| System | Method | Limitation |
| :--- | :--- | :--- |
| **qSOFA** | RR ≥ 22, SBP ≤ 100, AMS | Misses early-stage deterioration |
| **SIRS** | HR > 90, Temp > 38°C, WBC > 12k | High false-positive rate |
| **NEWS** | Aggregate vital scoring | Cannot read clinical context |

These systems answer: *"Has the patient crossed a threshold?"*
SepsisGuard AI answers: **"Is this patient deteriorating — and what does the full clinical picture say?"**

---

## 🚀 What It Does

SepsisGuard AI is an **MCP Server** published on the Prompt Opinion Marketplace with three composable tools that any agent in the ecosystem can invoke:

### 🛠️ Tool 1 — `compute_sepsis_risk`
Analyzes patient vitals, labs, and clinical notes. Returns a risk score (0–100) with an evidence-cited reasoning chain, confidence level, and key clinical signals.

### 🛠️ Tool 2 — `generate_clinical_alert`
Formats structured bedside alerts for nursing staff — headline, immediate actions, escalation guidance, and reassessment timing.

### 🛠️ Tool 3 — `recommend_bundle_actions`
Returns time-stamped treatment recommendations aligned with **Surviving Sepsis Campaign (SSC) 2024** guidelines.

---

## 🧠 Core Intelligence

Sepsis risk is not a binary event. It is a continuous multivariate signal across physiological, biochemical, and contextual domains.

### Why Gen AI, Not Rules?
Rule-based systems operate on isolated thresholds:
```python
IF lactate >= 2.0 THEN flag
IF HR > 90 THEN add_point
```

**SepsisGuard AI operates on integrated clinical reasoning:**
- **OBSERVE**: HR trending 88 → 96 → 104 over 4 hours (rising trajectory)
- **OBSERVE**: Lactate 3.4 mmol/L (tissue hypoperfusion)
- **OBSERVE**: Nursing note — "diaphoretic, confused, not oriented"
- **OBSERVE**: PMH includes CKD Stage 2 (comorbidity amplifier)
- **REASON**: Synergistic deterioration across hemodynamic, metabolic, and neurological domains.
- **CONCLUDE**: Risk 78/100 — **HIGH** — Hour-1 Bundle recommended.

---

## 🏗️ Architecture (Enterprise Level)

Built as a native MCP Server with a clean, modular Python architecture:

| Layer | Technology |
| :--- | :--- |
| **MCP Server** | Python + MCP SDK + Starlette |
| **AI Engine** | Gemini 2.5 Flash |
| **Protocol** | SHARP Context Propagation |
| **Data Standard** | FHIR R4 |
| **Transport** | Streamable HTTP |

---

## 🛠️ Setup & Installation

### 1. Clone the repository
```bash
git clone <your-repo-link>
cd sepsisguard
```

### 2. Configure Environment
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Edit `.env` and add your `GEMINI_API_KEY`.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Server
```bash
python -m src.sepsisguard.main
```

---

## 🌍 Impact

SepsisGuard AI transforms sepsis detection from:
- ❌ **Reactive** → ✅ **Predictive**
- ❌ **Rule-based** → ✅ **Reasoning-based**
- ❌ **Threshold-dependent** → ✅ **Trajectory-aware**
- ❌ **Isolated signals** → ✅ **Integrated clinical picture**

---

## ⚠️ Disclaimer
SepsisGuard AI is a clinical decision support tool. It augments clinician judgment — it does not replace it. All patient data used in this submission is fully synthetic. No protected health information (PHI) was used at any stage.

---

*"Sepsis doesn't wait for rules to trigger. Neither should we."*
**SepsisGuard AI — because every hour matters.**
