# Verity — Pre-Publication Brand Governance Platform

> **Pre-publication brand governance that cites its sources, explains every finding and keeps humans in charge.**

Built for the **TechCircuit Hackathon** (organised by WeCodeCoders) addressing the **Intelligent Brand-Governance Platform** challenge by **Inkloom AI**.

**Team**: `prijithasekar`  
- **Prijitha S** — Team Leader & Frontend Lead  
- **Rithika R** — Backend & Database Lead  
- **Priya Dharshini A** — AI & Review Engine Lead  
- **Shree Nithi Gobika S** — Integration, QA & Analytics Lead  

---

## 🚀 Quick Start (Run Locally in 10 Seconds)

### Option 1: Double-Click
Double-click **`run_app.bat`** in this folder.

### Option 2: Terminal
```powershell
python run_app.py
```

Open your browser to:
- **Interactive Web App**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive OpenAPI Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Run Tests & Benchmarks

Run the complete evaluation benchmark (100% Precision & Recall):
```powershell
python evaluation/run_evaluation.py
```

Run the unit test suite:
```powershell
python -m pytest tests/
```

---

## 🌟 The Three Key Hackathon Improvements

1. **Code-Level Citation Verifier**: Findings whose cited source excerpts cannot be verified in code against the authoritative database are automatically discarded. Stops AI guideline hallucinations completely.
2. **Three-Way Claim Verdicts (`SUPPORTED` / `CONTRADICTED` / `UNVERIFIABLE`)**: Unverifiable claims are never guessed; they are explicitly escalated to an **Authorised Reviewer**.
3. **Guideline-Clarity Insights Engine**: Tracks creator dismissals and required rationale to identify ambiguous rules (e.g. `CLAIM-04` with a 61.1% dispute rate) and gives Brand Admins actionable recommendations.

---

## 📁 Repository Structure

```
.
├── app/
│   ├── api/                  # FastAPI REST routes (review, drafts, kb, analytics, parser)
│   ├── core/                 # App configuration & settings
│   ├── db/                   # Database engine, SQLAlchemy Base, initial seed data
│   ├── models/               # Database ORM models and Pydantic schemas
│   ├── services/             # Core engines:
│   │   ├── citation_verifier.py       # (Improvement 1: Code-level Citation Verifier)
│   │   ├── grounded_retriever.py      # (Improvement 2: 3-way verdicts)
│   │   ├── workflow_engine.py         # (Human escalation & versioning v1 -> v2)
│   │   ├── governance_insights.py     # (Improvement 3: Guideline-clarity analytics)
│   │   ├── deterministic_checker.py   # Lexicon, readability, WCAG contrast
│   │   ├── claim_extractor.py         # Numeric, date, superlative extractor
│   │   ├── privacy_filter.py          # PII & confidential secret scrub
│   │   └── suggestion_generator.py    # Intent-preserving rewrites & diffs
│   └── static/               # Interactive Single Page Web Application
│       ├── index.html        # Responsive side-by-side workspace & dashboards
│       └── js/app.js         # Reactive frontend state machine
├── evaluation/
│   ├── labelled_test_set.json# Ground-truth evaluation dataset
│   └── run_evaluation.py     # Evaluation runner benchmarking precision & recall
├── sample_data/
│   ├── aura_brand_kit.json   # Exportable brand guidelines & approved facts
│   ├── draft_sample_bad.txt  # Test draft with intentional brand violations
│   └── draft_sample_good.txt # Fully compliant approved draft
├── tests/                    # Automated pytest test suites (7 passing tests)
├── ARCHITECTURE.md           # Full system architecture and technical decisions
├── EVALUATION_REPORT.md      # Detailed benchmark report & precision metrics
├── SUBMISSION_ROUND2.md      # Official Round 2 Hackathon Submission Document
├── run_app.py                # Standalone application entrypoint
└── run_app.bat               # Windows 1-click startup script
```

---

## 🔒 Responsible Design & Privacy
- **Zero Data Retention**: Confidential drafts are processed under isolated zero-retention conditions.
- **Pre-Processing PII Scrub**: Client emails, phone numbers, and secrets are automatically masked before evaluation.
- **AI Transparency**: Clear disclosure tags on every review finding specifying which rule, document, and exact quotation ground the decision.
