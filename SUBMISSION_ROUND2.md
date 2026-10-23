# Round 2 Submission: The Build — Verity

**Project Name**: **Verity**  
**Tagline**: *Pre-publication brand governance that cites its sources, explains every finding and keeps humans in charge*  
**Problem Statement**: Intelligent Brand-Governance Platform by Inkloom AI  
**Event**: TechCircuit Hackathon (organised by WeCodeCoders)  
**Team**: prijithasekar

---

## 1. Team Members and Individual Contributions

In accordance with Hackathon Rule 14 and Round 2 Submission Requirements, here is each team member's official contribution:

| Team Member | Official Role | Key Contributions in Round 2 Build |
|---|---|---|
| **Prijitha S** | **Team Leader & Frontend Lead** | Designed and built the side-by-side Review Workspace matching the wireframe in Slide 4; implemented real-time inline annotated highlights (red/yellow/blue/purple), visual diff views (`del`/`ins`), interactive finding cards, role switcher, and accessibility/usability testing. |
| **Rithika R** | **Backend & Database Lead** | Designed the FastAPI REST backend, SQLite/SQLAlchemy ORM database schema, draft versioning engine (`v1` $\rightarrow$ `v2`), role-based workflow routing, and immutable audit logging. |
| **Priya Dharshini A** | **AI & Review Engine Lead** | Engineered the hybrid review engine: claim extraction, grounded retrieval against authoritative facts, the **Code-Level Citation Verifier** (Improvement 1), the **Three-Way Claim Verdict** engine (Improvement 2), and intent-preserving rewrite generator. |
| **Shree Nithi Gobika S** | **Integration, QA & Analytics Lead** | Built the **Guideline-Clarity Insights Engine** (Improvement 3), WCAG 2.1 contrast calculation tool, document/PDF/image ingestion pipelines (`python-docx`, `pdfplumber`, `Pillow`), privacy PII sanitizer, and benchmark evaluation suite (`evaluation/run_evaluation.py`). |

---

## 2. Core Workflow Runs End-to-End

A judge or user can run the complete core workflow live in seconds:

1. **Brand Knowledge Base Import**: System seeds automatically with approved rules (e.g. `TERM-12`, `TONE-03`, `CLAIM-04`, `ACC-01`) and approved facts (e.g. `FACT-21`, `FACT-14`).
2. **Draft Submission & PII Sanitization**: User inputs or uploads copy. PII and confidential credentials are scrubbed before evaluation.
3. **Automated Audit with Code-Level Citation Proof**: Engine checks text, generates findings with severity tags, exact source citations, and verified badges.
4. **Intent-Preserving Correction**: Creator clicks `[Accept]` to 1-click update the draft text, which increments the version to `v2` and creates an audit log.
5. **Dismissal with Required Feedback**: If a creator dismisses a finding, they provide a reason which automatically updates the Guideline Clarity insights.
6. **Role Escalation**: High severity or unverifiable claims route automatically to the **Authorised Reviewer**; clean drafts route to the **Content Manager**.
7. **Manager Sign-Off**: The manager reviews version diffs, comments, and approves the draft for publication (`APPROVED`).

---

## 3. The Three Committed Improvements (Detailed Verification)

### Improvement 1: Code-Level Citation Verifier
- **What it does**: Confirms in deterministic Python code that any cited rule or fact excerpt genuinely exists in the authoritative source database.
- **Why it matters**: Completely stops AI hallucinations from inventing brand guidelines or penalizing creators for non-existent rules.
- **Evidence**: `tests/test_citation_verifier.py` (3 passing unit tests) and `app/services/citation_verifier.py`.

### Improvement 2: Three-Way Claim Verdicts with Human Routing
- **What it does**: Rather than giving binary accept/reject verdicts, claims are classified as:
  - `SUPPORTED`: Proven by verified fact.
  - `CONTRADICTED`: Conflicts with approved dates, pricing, or metrics $\rightarrow$ suggested fix with diff.
  - `UNVERIFIABLE`: Lacks approved source proof $\rightarrow$ escalated to **Authorised Reviewer** without guessing.
- **Why it matters**: Prevents false confidence in AI verification and keeps human experts in the loop for high-risk promotional assertions.
- **Evidence**: `tests/test_unverifiable_claims.py` and `app/services/grounded_retriever.py`.

### Improvement 3: Guideline-Clarity Insights Engine
- **What it does**: Aggregates creator disputes and dismissal reasons to calculate real-time guideline clarity scores and identify confusing standards.
- **Why it matters**: Turns routine compliance reviews into organizational learning, pinpointing rules like `CLAIM-04` (61% dismissal rate) that need clarification.
- **Evidence**: `tests/test_guideline_insights.py`, `app/services/governance_insights.py`, and the dedicated interactive dashboard tab in the UI.

---

## 4. Technical Stack, APIs, and Libraries Used

- **Language & Runtime**: Python 3.12, Modern ECMAScript
- **Backend**: FastAPI 0.161.1, Uvicorn 0.54.0, SQLAlchemy 2.1.6, Pydantic 2.14.1
- **Frontend**: Responsive Single-Page Application, Tailwind CSS, Lucide-style SVG icons
- **Document & Asset Processing**: `python-docx` 1.2.0, `pdfplumber` 0.11.10, `Pillow` 13.0.0
- **Testing & Benchmarking**: `pytest` 9.1.1, `TestClient` (Starlette/httpx)
- **AI & Security**: Zero-Retention PII Sanitization, Grounded Retrieval Engine, Deterministic Lexicon Verification

---

## 5. User Testing & Benchmark Evidence

- **Labelled Test Dataset**: 8 standardized evaluation cases covering contradictory claims, unverifiable claims, terminology violations, tone issues, accessibility problems, and true facts.
- **Benchmark Metric**: **100% Accuracy, 100% Precision, 100% Recall** (`python evaluation/run_evaluation.py`).
- **Unit Test Suite**: 7 passing tests with 0 failures (`python -m pytest tests/`).
