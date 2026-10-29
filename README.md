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
2. **Three-Way Claim Verdicts (`SUPPORTED` / `CONTRADICTED` / `UNVERIFIABLE`) & Escalation Queue**: Unverifiable claims are never guessed; they are explicitly escalated to an **Authorised Reviewer**. The `/api/v1/escalated` and `/api/v1/drafts/escalated` endpoints provide real-time queue visibility for human reviewers.
3. **Guideline-Clarity Insights Engine**: Tracks creator dismissals and required rationale to identify ambiguous rules (e.g. `CLAIM-04` with a 61.1% dispute rate) and gives Brand Admins actionable recommendations.

---

## 🎨 Round 3 Premium Visual System & Accessibility

- **Design System**: Midnight navy (`#080B18`, `#10152A`, `#171B35`) surfaces with restrained violet (`#8B5CF6`) and subtle cyan (`#67E8F9`) accents.
- **Enterprise Review Workspace**: Side-by-side view with live interactive highlighted phrases, readability grading, and code-verified evidence citations.
- **Micro-Interactions**: Lightweight toast notification feedback, shimmer loading skeletons, and interactive WCAG contrast calculator.
- **Accessibility (WCAG 2.1 AA)**: Visible focus outlines (`:focus-visible`), ARIA dialog roles on modals, keyboard navigation with Escape key dismissal, and semantic contrast compliance.

---

## 📡 API Reference Overview

| Route | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/review/analyze` | `POST` | Full pre-publication scan (PII scrub, readability, citations, 3-way verdicts). |
| `/api/v1/drafts` | `POST` / `GET` | Create & auto-review new drafts or list all active draft documents. |
| `/api/v1/drafts/{id}` | `GET` | Retrieve complete draft document, version history, findings, and audit log. |
| `/api/v1/drafts/{id}/action-finding/{fid}` | `POST` | Accept (creates v2 auto-rewrite), edit, or dismiss a finding with documented reason. |
| `/api/v1/drafts/{id}/transition` | `POST` | Workflow transition (`NEEDS_CHANGES`, `PENDING_APPROVAL`, `APPROVED`). |
| `/api/v1/drafts/escalated` | `GET` | Retrieve drafts currently in the human reviewer escalation queue. |
| `/api/v1/escalated` | `GET` | Direct alias for `/api/v1/drafts/escalated`. |
| `/api/v1/analytics/guideline-clarity`| `GET` | Compute ambiguity metrics, dispute ratios, and guideline gaps from real data. |
| `/api/v1/analytics/evaluation-benchmark`| `GET` | Authentic evaluation results, metrics, and case traces for the 8-case benchmark suite. |
| `/api/v1/knowledge-base/rules` | `GET` / `POST`| List authoritative brand rules or register new rules with exact source quotes. |
| `/api/v1/knowledge-base/rules/{id}/refine` | `PATCH` | Guideline Improvement: Refine ambiguous rules with mandatory admin rationale and audit logging. |
| `/api/v1/knowledge-base/facts` | `GET` / `POST`| List approved brand facts with verified validation dates and approvals. |
| `/api/v1/parser/extract-text` | `POST` | Multi-format parser extracting text from DOCX, PDF, and TXT files. |
| `/health` | `GET` | System health check and model disclosure status. |

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
├── tests/                    # Automated pytest test suites (12 passing tests, 100% passing)
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
