class SyntheticData:
    PATIENTS = {
        "demo-high": """
PATIENT: Margaret Chen | Age: 82 | Female
Chief Complaint: Altered mental status and hypotension — brought in by family.

Vitals (trending last 4 hours):
- HR: 88 → 96 → 104 bpm (rising)
- BP: 118/76 → 98/62 → 84/54 mmHg (dropping)
- Temp: 38.9°C
- RR: 22/min
- SpO2: 94% on 2L NC
- Lactate: 3.4 mmol/L (drawn 14:32)

Labs: WBC 18.2 (elevated), Creatinine 2.1 (baseline 0.9), Procalcitonin 4.8

Nursing note (15:10): Patient increasingly diaphoretic and confused. Not responding to orientation questions. Family reports she was fine this morning. IV access x2 established. Fluids running.

PMH: Type 2 Diabetes, Hypertension, CKD Stage 2
Medications: Metformin, Lisinopril, Aspirin
""",
        "demo-moderate": """
PATIENT: Robert Okafor | Age: 56 | Male
Chief Complaint: Fever and productive cough x3 days, now with rigors.

Vitals:
- HR: 98 bpm (stable)
- BP: 108/70 mmHg
- Temp: 39.2°C
- RR: 20/min
- SpO2: 96% on room air
- Lactate: 1.8 mmol/L

Labs: WBC 14.1, CRP elevated, Chest X-ray shows RLL consolidation

Nursing note: Alert and oriented x3. Uncomfortable but conversational. Started on empiric antibiotics 2 hours ago.

PMH: Hypertension, former smoker
Medications: Amlodipine
""",
        "demo-low": """
PATIENT: James Whitfield | Age: 19 | Male
Chief Complaint: Sore throat and low-grade fever x2 days.

Vitals:
- HR: 84 bpm
- BP: 122/78 mmHg
- Temp: 37.9°C
- RR: 16/min
- SpO2: 99% on room air
- Lactate: 0.9 mmol/L

Labs: WBC 11.2 (mildly elevated), Rapid strep negative

Nursing note: Alert, appropriate, no distress. Tolerating PO fluids. Here for evaluation before college travel.

PMH: None
Medications: None
"""
    }

    @classmethod
    def get_patient(cls, scenario: str) -> str:
        key = f"demo-{scenario.lower()}"
        return cls.PATIENTS.get(key, cls.PATIENTS["demo-high"])
