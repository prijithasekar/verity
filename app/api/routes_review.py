import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel

from app.db.database import get_db
from app.models.db_models import DraftDocument, DraftVersion, Finding
from app.services.privacy_filter import PrivacyFilter
from app.services.deterministic_checker import DeterministicChecker
from app.services.claim_extractor import ClaimExtractor
from app.services.grounded_retriever import GroundedRetriever
from app.services.citation_verifier import CitationVerifier
from app.services.workflow_engine import WorkflowEngine
from app.models.schemas import ContrastCheckRequest, ContrastCheckResponse

router = APIRouter(prefix="/review", tags=["Content Review Engine"])

class QuickReviewRequest(BaseModel):
    content: str
    content_type: str = "social_post"

class QuickReviewResponse(BaseModel):
    sanitized_content: str
    redacted_items: List[Dict[str, str]]
    readability: Dict[str, Any]
    verified_findings: List[Dict[str, Any]]
    discarded_hallucinations: List[Dict[str, Any]]
    assigned_role: str
    ai_disclosure: str

@router.post("/analyze", response_model=QuickReviewResponse)
def analyze_content(req: QuickReviewRequest, db: Session = Depends(get_db)):
    # 1. Privacy & Confidentiality Filter (PII & Secret Masking)
    sanitized_text, redacted_items = PrivacyFilter.sanitize(req.content)

    # 2. Readability Metrics
    readability = DeterministicChecker.calculate_readability(sanitized_text)

    # 3. Deterministic Rule Scans (Lexicon, Banned Patterns, Alt-text)
    det_findings = DeterministicChecker.scan_deterministic_rules(sanitized_text, db)

    # 4. Claim Extraction (Factual, Superlatives, Promotions, Dates)
    claims = ClaimExtractor.extract_claims(sanitized_text)

    # 5. Grounded Knowledge Base Retrieval & Three-Way Verdict (Improvement 2)
    claim_findings = GroundedRetriever.evaluate_claims(claims, db)

    # Combine all raw candidate findings
    raw_findings = det_findings + claim_findings

    # 6. CODE-LEVEL CITATION VERIFIER (Improvement 1)
    # Strictly validates that cited source excerpts exist in ground-truth DB in code.
    # Discards fabricated or hallucinated citations.
    verified_findings, discarded_findings = CitationVerifier.filter_and_verify_findings(raw_findings, db)

    # 7. Workflow Human Routing (Improvement 2)
    assigned_role = WorkflowEngine.determine_assigned_role(verified_findings)

    return QuickReviewResponse(
        sanitized_content=sanitized_text,
        redacted_items=redacted_items,
        readability=readability,
        verified_findings=verified_findings,
        discarded_hallucinations=discarded_findings,
        assigned_role=assigned_role,
        ai_disclosure="Verity Grounded Engine v1.2 — All findings code-verified against verified Brand Knowledge Base."
    )

@router.post("/contrast-check", response_model=ContrastCheckResponse)
def check_contrast(req: ContrastCheckRequest):
    result = DeterministicChecker.check_wcag_compliance(
        req.fg_hex, req.bg_hex, req.font_size, req.is_bold
    )
    return ContrastCheckResponse(**result)
