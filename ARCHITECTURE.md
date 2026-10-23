# Verity — Technical Architecture & Design Document

**System**: Verity (Pre-Publication Brand Governance Platform)  
**Hackathon**: TechCircuit Hackathon (organised by WeCodeCoders)  
**Problem Statement**: Intelligent Brand-Governance Platform by Inkloom AI  

---

## 1. Architectural Overview

Verity is engineered as a pre-publication brand governance gateway that combines **deterministic lexical/accessibility rules** with **grounded knowledge retrieval** and **human oversight**. It operates between "draft" and "published" status.

```
+-------------------------------------------------------------------------+
|                        Verity Ingestion Gateway                         |
|  - Raw Text & Markdown                                                  |
|  - Multi-Format Documents (python-docx, pdfplumber)                     |
|  - Asset Color & Ratio Analysis (Pillow)                                |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                    Layer 1: Privacy & Sanitization                      |
|  - Zero-Data-Retention Filter                                           |
|  - PII Masking: Emails, phone numbers, secret tokens, API keys          |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|              Layer 2: Deterministic Fast-Path Evaluation                |
|  - Regex Terminology Lexicon (banned vs preferred patterns)             |
|  - Tone & Urgent Metaphor Scanners                                      |
|  - Flesch-Kincaid Grade Level & Readability Scorer                      |
|  - WCAG 2.1 Contrast Ratio Calculator (L1+0.05)/(L2+0.05)               |
|  - Image Alt-Text Presence Detector                                     |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|             Layer 3: Claim Extraction & Grounded Retrieval              |
|  - Numeric, percentage, date, and superlative statement extraction      |
|  - Three-Way Grounding: SUPPORTED | CONTRADICTED | UNVERIFIABLE         |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|            Layer 4: Code-Level Citation Verifier (Improvement 1)        |
|  - Python code confirms cited excerpt exists in Brand Knowledge Base    |
|  - Hallucinated or invented citations are pruned and discarded          |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|             Layer 5: Intent-Preserving Suggestion Generator             |
|  - Preserves creator's original purpose and grammatical structure       |
|  - Generates visual HTML diff (del / ins)                               |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|           Layer 6: Role-Based Workflow & Human Escalation               |
|  - High Severity / Unverifiable Claims  --> Authorised Reviewer         |
|  - Standard Violations & Clean Content --> Content Manager              |
|  - Actions: [Accept] -> v2, [Edit], [Dismiss] -> Feeds Insights         |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|       Layer 7: Guideline-Clarity Insights Engine (Improvement 3)        |
|  - Per-rule dismissal rate analysis                                     |
|  - Identifies ambiguous / contested brand guidelines for Brand Admins   |
+-------------------------------------------------------------------------+
```

---

## 2. Technical Decisions & Justifications

| Layer | Selection | Justification |
|---|---|---|
| **Frontend** | Responsive SPA with Tailwind CSS & JavaScript State Engine | Matches Slide 4 wireframe exactly. Zero fragile client build tool issues for hackathon judges; instantly runs on any modern browser. |
| **Backend** | FastAPI (Python 3.12) | Asynchronous, typed, high throughput, automatic OpenAPI documentation, clean integration with Python NLP and document processing libraries. |
| **Database** | SQLite + SQLAlchemy ORM | Zero-configuration local database that works out of the box with zero external database service dependencies; can easily target PostgreSQL + pgvector. |
| **Parsing & OCR** | `python-docx`, `pdfplumber`, `Pillow` | Robust extraction of paragraphs, tables, text layout, and image palette luminance. |
| **Verification Engine** | Hybrid: Deterministic Lexicon + Grounded Retriever + Code Citation Verifier | Avoids hallucination risks inherent in raw LLM prompting. Every single finding links back to an exact source document excerpt. |

---

## 3. Database Schema

1. `brand_rules`: Stores atomic rules (ID, category, rule name, banned/preferred regex, exact source text, severity, times flagged, times accepted, times dismissed, dispute feedback).
2. `approved_facts`: Stores authoritative company truths (ID, category, subject, fact statement, exact quote, validity range, approved by).
3. `brand_assets`: Vector logos, color palettes, and typography specifications.
4. `draft_documents`: Main draft record (ID, title, status, assigned role, version count, creator).
5. `draft_versions`: Version history snapshots (`v1`, `v2`, etc.) with sanitized content.
6. `findings`: Detailed findings with exact character offsets, explanation, cited source, verified badge, and suggested fix.
7. `workflow_comments`: Collaboration discussion trail between creators, reviewers, and managers.
8. `audit_logs`: Immutable chronological log of all actions.
