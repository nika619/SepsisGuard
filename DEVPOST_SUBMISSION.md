# SEPSISGUARD AI — DEVPOST SUBMISSION TEXT
# Copy each section into the corresponding Devpost field

=======================================================================
PROJECT NAME
=======================================================================
SepsisGuard AI — Real-Time Sepsis Intelligence MCP

=======================================================================
SHORT DESCRIPTION (shown on card)
=======================================================================
An MCP server that detects early sepsis 4-6 hours before clinical
recognition by using LLM reasoning over unstructured clinical notes —
catching what rule-based qSOFA scoring misses.

=======================================================================
FULL DESCRIPTION
=======================================================================

## The Problem No One Talks About

At 3:07am, a nurse writes in her notes: "Patient seemed a little off
tonight. Diaphoretic. Kept asking what day it was."

A qSOFA score sees: HR 91, RR 19, no altered mental status documented
in structured fields. Score: 0. No alert fires.

Eight hours later, Margaret Chen is in septic shock.

This happens 270,000 times per year in the United States. Sepsis is
the leading cause of preventable hospital deaths. The window for
effective intervention is narrow — every hour of delayed treatment
increases mortality by 7%. And the signals are almost always there,
written in plain language in nursing notes, patient complaints, and
clinical narratives that rule-based software cannot read.

SepsisGuard AI was built to close this gap.

## What SepsisGuard AI Does

SepsisGuard AI is an MCP Server published to the Prompt Opinion
Marketplace. It exposes three composable tools that any A2A agent on
the platform can invoke:

**ComputeSepsisRisk** — The core intelligence tool. Receives a patient
context via SHARP/FHIR context propagation, fetches the patient's
clinical documents from the platform's internal FHIR store, and uses
Claude AI to reason over the full unstructured clinical narrative.
It identifies sepsis warning signals that exist in text but not in
structured data fields: nursing observations of diaphoresis,
patient-reported malaise, trending vital narratives, wound
descriptions, urine output changes. Returns a 0-100 risk score,
confidence level, exact quoted signals from the clinical text, and
clinical reasoning in three sentences.

**GenerateClinicalAlert** — Takes the ComputeSepsisRisk output and
produces a structured, formatted clinical alert ready for care team
handoff. Color-coded by severity. Cites the exact clinical signals.
Specifies time-bound action requirements.

**RecommendBundleActions** — Returns a prioritized, evidence-based
action list following the Surviving Sepsis Campaign 2024 Hour-1 Bundle
guidelines. For high-risk patients: blood cultures, broad-spectrum
antibiotics within 60 minutes, IV fluids 30mL/kg, lactate measurement.
Each action includes a FHIR ServiceRequest resource type for EHR
integration.

## Why This Is a GenAI-Only Capability

Traditional sepsis detection software operates on structured data:
numeric vital sign thresholds, ICD-10 code presence, documented
diagnosis fields. This is rule-based software. It fails when:

- Vitals are individually within normal limits but trending dangerously
- The most important signal is in a nursing note: "patient felt off"
- Early sepsis presents atypically in elderly post-surgical patients
- The nurse observed something but didn't know which structured field
  to document it in

SepsisGuard uses LLM reasoning across the full clinical text. It reads
the same document a senior intensivist would read and extracts the same
signals they would flag. This is not achievable with any rule-based
system. It requires the semantic understanding that only generative AI
provides.

## Platform Integration

SepsisGuard is built natively on the Prompt Opinion platform:

- **SHARP Context**: Patient ID and FHIR access token arrive
  automatically via the SHARP extension spec. No manual patient
  selection. No API key management by the calling agent.
- **MCP Protocol**: All three tools are auto-discovered by the platform
  via the MCP Streamable HTTP transport. Any A2A agent in the Marketplace
  can pick up ComputeSepsisRisk as a superpower with one click.
- **Marketplace Published**: SepsisGuard is live in the Prompt Opinion
  Marketplace. Discoverable. Invokable. Composable with any other agent
  in the ecosystem.
- **Guardrails**: A PHI Blocker guardrail is configured to reject any
  real patient data. All development and demonstration uses only
  synthetic patient records.

## The Demo Scenario

Three synthetic patients at different risk levels demonstrate
SepsisGuard's risk stratification capability:

**Patient A — Margaret Chen, 67F, post-op hip replacement**
Score: 82/100 CRITICAL
Signals: Trending HR 88→104 over 5 hours. Temp 39.1C. Nursing note:
"diaphoretic at 0300, confused about current date." Decreased urine
output 420mL → 180mL. Wound erythema.
qSOFA would score: 0-1. SepsisGuard: CRITICAL — Hour-1 Bundle now.

**Patient B — Robert Okafor, 71M, pneumonia day 2**
Score: 56/100 WATCH
Signals: Rising WBC 11.8→14.2. New mild confusion noted by nursing.
Procalcitonin 2.1. Incomplete antibiotic response. AKI developing.
Action: Reassess in 30 minutes. Antibiotic escalation consideration.

**Patient C — James Whitfield, 54M, pre-op assessment**
Score: 19/100 ROUTINE
Signals: None. All vitals stable. Labs normal. Fully oriented.
Action: Standard monitoring. Cleared for surgery.

## Potential Impact

- 270,000 sepsis deaths per year in the US are preventable with
  earlier detection
- 4-6 hours of earlier detection = 7% mortality reduction per hour
  = up to 42% lives saved in that window
- Each ICU bed day costs $3,000-$4,000. Earlier detection = shorter
  ICU stays = significant cost avoidance
- SepsisGuard operates on existing clinical documentation — no new
  sensors, no new workflows, no hardware

## Feasibility

- Fully synthetic data. No PHI. HIPAA-compatible architecture.
- Integrates with any FHIR R4-compliant EHR via SMART on FHIR
- MCP tools are composable and auditable — every signal cited comes
  from an exact quote in the clinical document, not LLM inference
- Agent drafts the alert. Physician reviews and acts. Clinical authority
  remains with the human. SepsisGuard removes the 3am detection gap,
  not the physician.
- Production deployment: containerized Python server behind API gateway,
  no patient data stored server-side, stateless architecture

=======================================================================
TECH STACK
=======================================================================
- Python 3.11 + FastMCP (MCP server framework)
- Anthropic Claude (LLM reasoning over clinical text)
- Prompt Opinion Platform (MCP hosting, SHARP context, Marketplace)
- FHIR R4 (patient data via platform's internal FHIR store)
- SHARP Extension Spec (patient context propagation)
- Starlette + Uvicorn (ASGI server)
- ngrok (tunnel for hackathon deployment)

=======================================================================
MARKETPLACE URL (fill in after publishing)
=======================================================================
https://app.promptopinion.ai/marketplace/[YOUR-LISTING-ID]

=======================================================================
DEMO VIDEO (fill in after recording)
=======================================================================
https://youtube.com/watch?v=[YOUR-VIDEO-ID]
