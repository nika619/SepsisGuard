# SepsisGuard AI — Complete Setup Guide
# Follow every step in order. Do not skip anything.

=======================================================================
WHAT YOU ARE BUILDING
=======================================================================
An MCP Server called SepsisGuard AI that:
1. Receives a patient context from Prompt Opinion (SHARP context)
2. Fetches the patient's clinical documents
3. Uses Claude AI to detect early sepsis signals in the text
4. Returns a risk score, clinical alert, and bundle recommendations
5. Lives at your ngrok URL and is published to the Prompt Opinion Marketplace

=======================================================================
BEFORE YOU START — THINGS YOU NEED
=======================================================================
□ Python 3.11 or higher installed (check: python --version)
□ An Anthropic API key (get free at https://console.anthropic.com)
□ ngrok installed (get free at https://ngrok.com/download)
□ A Prompt Opinion account (app.promptopinion.ai)
□ Your SepsisGuard project files (server.py, requirements.txt, .env)

=======================================================================
STEP 1 — SET UP YOUR PROJECT FOLDER
=======================================================================

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux).

Run these commands one at a time:

  cd Desktop
  mkdir sepsisguard
  cd sepsisguard

Now copy these files into the sepsisguard folder:
  - server.py
  - requirements.txt
  - .env.example

=======================================================================
STEP 2 — CREATE YOUR ENVIRONMENT FILE
=======================================================================

In the sepsisguard folder, copy .env.example to .env:

  Mac/Linux:  cp .env.example .env
  Windows:    copy .env.example .env

Now open .env in any text editor and fill in:

  ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
  SEPSISGUARD_API_KEY=sepsisguard-secret-2026
  PORT=8000

Save the file. Do not share this file with anyone.

=======================================================================
STEP 3 — INSTALL PYTHON DEPENDENCIES
=======================================================================

Run this in your terminal (inside the sepsisguard folder):

  pip install -r requirements.txt

Wait for it to finish. You should see "Successfully installed" messages.

If you get permission errors on Mac/Linux, try:
  pip3 install -r requirements.txt

=======================================================================
STEP 4 — TEST THE SERVER LOCALLY
=======================================================================

Run the server:

  python server.py

You should see:
  SepsisGuard AI MCP Server starting on port 8000
  MCP endpoint: http://localhost:8000/mcp
  Health check: http://localhost:8000/health

Open a NEW terminal tab and test the health check:

  curl http://localhost:8000/health

You should see: {"status": "ok", "service": "SepsisGuard AI MCP Server"}

If you see this — your server works. Keep it running.

=======================================================================
STEP 5 — EXPOSE YOUR SERVER WITH NGROK
=======================================================================

Open a THIRD terminal tab. Run:

  ngrok http 8000

You will see output like:
  Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000

COPY the https://abc123.ngrok-free.app URL. This is your public URL.
Every time you restart ngrok, this URL changes. Keep ngrok running.

Your MCP endpoint is: https://abc123.ngrok-free.app/mcp

=======================================================================
STEP 6 — ADD PATIENTS TO PROMPT OPINION
=======================================================================

Go to app.promptopinion.ai → Patient Data → Import

Section "Upload a FHIR Bundle":
  Click the file picker → select patient_A_high_risk.txt → click Import

Wait for success message. Repeat for:
  patient_B_moderate_risk.txt
  patient_C_low_risk.txt

Then go to Patient Data → List to confirm 3 patients appear.

NOTE: If the platform requires JSON format, rename your .txt files to
.json and wrap the content like this:
{
  "resourceType": "Bundle",
  "type": "document",
  "entry": [{
    "resource": {
      "resourceType": "DocumentReference",
      "content": [{"attachment": {"contentType": "text/plain",
      "data": "BASE64_ENCODED_NOTE_TEXT"}}]
    }
  }]
}

=======================================================================
STEP 7 — CONFIGURE MCP SERVER IN PROMPT OPINION
=======================================================================

Go to app.promptopinion.ai → Configuration → MCP Servers
Click "+ Add MCP Server"

Fill in:
  Friendly Name:        SepsisGuard AI
  Endpoint:             https://YOUR-NGROK-URL.ngrok-free.app/mcp
  Transport Type:       Streamable HTTP
  Authentication Type:  API Key
  API Key Header Name:  x-sepsisguard-key
  API Key Header Value: sepsisguard-secret-2026

Click "Continue" (it's a 2-step flow — screenshot the next screen)

On Step 2:
  Toggle ON: Requires Patient Data Access
  Accept the yellow security warning
  Click "Test"

EXPECTED RESULT: You should see "MCP Server Tools — Success" with:
  ✓ ComputeSepsisRisk
  ✓ GenerateClinicalAlert
  ✓ RecommendBundleActions

If the tools appear — SCREENSHOT THIS. It is your Stage One proof.
Click Save.

=======================================================================
STEP 8 — CREATE YOUR DUMMY TEST AGENT (BYO Agent)
=======================================================================

Go to Agents → BYO Agents → Add Agent

BASIC TAB:
  Allowed Contexts: ✓ Patient (CHECK THIS — critical)
  Agent Name: SepsisGuard Test Agent
  Description: Internal test agent for SepsisGuard MCP server validation
  Model Configuration: gemini-3-flash-preview (leave default)
  Timeout Seconds: 120

SYSTEM PROMPT TAB — paste this exactly:
---
You are the SepsisGuard AI clinical assistant. When a user asks you to
assess a patient for sepsis, you must:

1. Call ComputeSepsisRisk with the current patient's fhirUrl, patientId,
   and fhirToken from the SHARP context.
2. Take the result and call GenerateClinicalAlert with the risk_score,
   confidence, signals_found, reasoning, and time_sensitivity values.
3. Take the risk_score and call RecommendBundleActions with the patient_id,
   risk_score, and time_sensitivity.
4. Present all three results clearly to the user.

Always use the SHARP context patient data. Never make up patient information.
This system uses synthetic data only and is for demonstration purposes.
---

TOOLS TAB:
  Add your SepsisGuard AI MCP server here (select it from the list)

A2A & SKILLS TAB:
  Toggle ON: Send FHIR Context
  *** A second toggle appears: Toggle ON: Acknowledge Sending FHIR Context ***
  (Missing this second toggle = FHIR context never arrives at your server)

Click Save.

=======================================================================
STEP 9 — ADD GUARDRAIL (30 minutes — huge credibility boost)
=======================================================================

Go to Configuration → Guardrails → Add Guardrail

  Type: Agent
  Name: SepsisGuard PHI Blocker
  Description (Optional): Blocks real PHI from entering SepsisGuard
  Model Configuration: gemini-3-flash-preview
  Validation Instruction:
    This MCP server processes only synthetic FHIR data for demonstration
    purposes. Reject any input that appears to contain real patient
    information including real full names combined with real dates of
    birth, real SSNs, real insurance IDs, or real medical record numbers
    from actual healthcare institutions. Only synthetic test data with
    fictional patient names is permitted.

Click Save.

=======================================================================
STEP 10 — TEST THE FULL FLOW
=======================================================================

Go to Launchpad (top right of the platform)

Select context: Patient → choose Margaret Chen (Patient A, high risk)
Select agent: SepsisGuard Test Agent

Type in the chat:
  "Assess this patient for sepsis risk"

EXPECTED: The agent calls all 3 tools in sequence and returns:
  1. Risk score ~80+ with specific clinical signals quoted
  2. CRITICAL alert formatted with warning indicators
  3. Hour-1 Bundle actions with priorities

SCREENSHOT EVERYTHING. This is your demo video content.

Repeat for Robert Okafor (moderate) and James Whitfield (low risk).
You now have 3 different risk stratification results to show judges.

=======================================================================
STEP 11 — PUBLISH TO MARKETPLACE (DO THIS ON DAY 7)
=======================================================================

Go to Marketplace Studio → MCP Servers
Click "+ Add MCP Server"
Find "SepsisGuard AI" in the list
Toggle ON: Publish to Marketplace
Click Save

Verify: Go to External Agents → Search Marketplace
Search for "SepsisGuard"
Confirm your server appears in results

SCREENSHOT THE MARKETPLACE LISTING. This is your Stage One verification proof.

=======================================================================
STEP 12 — RECORD YOUR DEMO VIDEO (Day 8-9)
=======================================================================

Your video script (exactly 3 minutes):

0:00–0:30 THE PROBLEM
  "Sepsis kills 270,000 Americans per year. Every hour of delayed
  detection increases mortality by 7%. Current rule-based scoring
  like qSOFA misses 30% of sepsis cases — it cannot read a nurse's
  note that says a patient felt 'not right' at 3am. That is the gap
  SepsisGuard fills."

0:30–1:30 THE DEMO
  Show Prompt Opinion platform.
  Select Margaret Chen (high risk patient).
  Trigger SepsisGuard.
  Show the risk score 80+ appearing.
  Show the signals — "diaphoretic at 0300", "confused about current date"
  Show the Hour-1 Bundle recommendations.
  Say: "These signals — a nursing observation at 3am, a trending heart
  rate — are invisible to qSOFA. Only LLM reasoning over unstructured
  text can find them."

1:30–2:15 RISK STRATIFICATION
  Switch to Robert Okafor (moderate) — show score ~55, Watch protocol.
  Switch to James Whitfield (low) — show score ~20, Routine monitoring.
  Say: "SepsisGuard correctly stratifies risk across patients. The same
  tool works across your entire patient population."

2:15–2:45 PLATFORM INTEGRATION
  Show the Marketplace listing.
  Say: "SepsisGuard is published to the Prompt Opinion Marketplace.
  Any A2A agent on the platform can call ComputeSepsisRisk as a
  superpower. We are not just a demo — we are infrastructure."

2:45–3:00 CLOSE
  "270,000 lives. 7% per hour. SepsisGuard AI."

=======================================================================
TROUBLESHOOTING
=======================================================================

PROBLEM: Tools don't appear after clicking Test
FIX: Your server is not running or ngrok URL is wrong.
     Check: is python server.py still running? Is ngrok still running?
     Copy the ngrok URL fresh — do not type it manually.

PROBLEM: 401 Unauthorized when platform calls your server
FIX: API Key mismatch. Check that .env SEPSISGUARD_API_KEY exactly
     matches what you entered in "API Key Header Value" in the platform.

PROBLEM: ComputeSepsisRisk returns "Missing required SHARP context"
FIX: Both FHIR toggles are not ON in the A2A & Skills tab of your
     BYO agent. Go back and enable both: Send FHIR Context AND
     Acknowledge Sending FHIR Context.

PROBLEM: Patient clinical text is not found, demo mode activates
FIX: Check that patients were imported correctly. The demo fallback
     will still work for the judges — it shows the tool functioning
     even if FHIR fetch fails.

PROBLEM: ngrok URL changes every time
FIX: Free ngrok gives random URLs on restart. Either keep it running
     continuously OR upgrade to ngrok free static domain (1 free static
     domain available at dashboard.ngrok.com). Use the static domain
     in your platform config so you never have to update it.

=======================================================================
DAILY CHECKLIST
=======================================================================

Every day before working:
  □ Start python server.py in terminal 1
  □ Start ngrok http 8000 in terminal 2
  □ Confirm ngrok URL matches what is in Prompt Opinion MCP config
  □ Run health check: curl https://YOUR-NGROK-URL.ngrok-free.app/health

Day 7 must-do:
  □ Publish to Marketplace
  □ Verify discoverable in Search Marketplace
  □ Screenshot the listing

Day 10 must-do:
  □ Submit on Devpost by 11pm May 10 (not May 11 — buffer day)
  □ Include Marketplace URL in submission
  □ Video uploaded to YouTube (unlisted is fine)

=======================================================================
SUBMISSION CHECKLIST — STAGE ONE PASS/FAIL
=======================================================================

□ MCP Server published and discoverable in Marketplace
□ All 3 tools appear when Test button clicked
□ Both FHIR toggles ON in BYO agent A2A settings
□ Requires Patient Data Access toggle ON in MCP config
□ Only synthetic patient data used (Margaret Chen, Robert Okafor, James Whitfield)
□ Demo video under 3 minutes showing tools working in Prompt Opinion
□ Devpost submission includes Marketplace URL
□ Guardrail configured (PHI Blocker)
