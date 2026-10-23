import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timezone

from app.db.database import get_db
from app.models.db_models import DraftDocument, DraftVersion, Finding, WorkflowComment, AuditLog
from app.models.schemas import (
    DraftCreateRequest, DraftUpdateRequest, FindingActionRequest, 
    WorkflowTransitionRequest, CommentCreate, CommentResponse, AuditLogResponse
)
from app.services.privacy_filter import PrivacyFilter
from app.services.deterministic_checker import DeterministicChecker
from app.services.claim_extractor import ClaimExtractor
from app.services.grounded_retriever import GroundedRetriever
from app.services.citation_verifier import CitationVerifier
from app.services.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/drafts", tags=["Review & Approval Workflow"])

@router.post("")
def create_and_review_draft(req: DraftCreateRequest, db: Session = Depends(get_db)):
    draft_id = str(uuid.uuid4())[:8]

    # Run review pipeline
    sanitized_text, _ = PrivacyFilter.sanitize(req.content)
    det_findings = DeterministicChecker.scan_deterministic_rules(sanitized_text, db)
    claims = ClaimExtractor.extract_claims(sanitized_text)
    claim_findings = GroundedRetriever.evaluate_claims(claims, db)
    
    # Improvement 1: Citation Verification Pass
    verified_findings, _ = CitationVerifier.filter_and_verify_findings(det_findings + claim_findings, db)

    # Determine assigned role (Improvement 2)
    assigned_role = WorkflowEngine.determine_assigned_role(verified_findings)
    status = "NEEDS_CHANGES" if verified_findings else "PENDING_APPROVAL"

    draft = DraftDocument(
        id=draft_id,
        title=req.title,
        content_type=req.content_type,
        current_version=1,
        status=status,
        assigned_role=assigned_role,
        creator_name=req.creator_name
    )
    db.add(draft)

    version_1 = DraftVersion(
        draft_id=draft_id,
        version_number=1,
        content=req.content,
        sanitized_content=sanitized_text,
        findings_count=len(verified_findings)
    )
    db.add(version_1)

    # Persist findings
    for idx, f in enumerate(verified_findings):
        finding_db = Finding(
            id=f"{draft_id}-f{idx+1}",
            draft_id=draft_id,
            version_number=1,
            rule_or_fact_id=f["rule_or_fact_id"],
            category=f["category"],
            severity=f["severity"],
            claim_verdict=f.get("claim_verdict", "NONE"),
            flagged_text=f["flagged_text"],
            start_char=f["start_char"],
            end_char=f["end_char"],
            explanation=f["explanation"],
            cited_source=f["cited_source"],
            cited_excerpt=f["cited_excerpt"],
            citation_verified=True,
            suggested_fix=f.get("suggested_fix"),
            status="OPEN"
        )
        db.add(finding_db)

    # Initial Audit Log
    WorkflowEngine.log_audit_event(
        db, draft_id, "DRAFT_CREATED", req.creator_name, "creator",
        f"Draft '{req.title}' submitted for automated brand review. {len(verified_findings)} verified findings detected. Routed to: {assigned_role}."
    )

    db.commit()

    return {
        "id": draft_id,
        "title": draft.title,
        "current_version": 1,
        "status": draft.status,
        "assigned_role": draft.assigned_role,
        "findings_count": len(verified_findings)
    }

@router.get("")
def list_drafts(db: Session = Depends(get_db)):
    drafts = db.query(DraftDocument).order_by(DraftDocument.updated_at.desc()).all()
    results = []
    for d in drafts:
        results.append({
            "id": d.id,
            "title": d.title,
            "content_type": d.content_type,
            "current_version": d.current_version,
            "status": d.status,
            "assigned_role": d.assigned_role,
            "creator_name": d.creator_name,
            "created_at": d.created_at,
            "updated_at": d.updated_at
        })
    return results

@router.get("/{draft_id}")
def get_draft_details(draft_id: str, db: Session = Depends(get_db)):
    draft = db.query(DraftDocument).filter(DraftDocument.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    latest_version = db.query(DraftVersion).filter(
        DraftVersion.draft_id == draft_id,
        DraftVersion.version_number == draft.current_version
    ).first()

    versions = db.query(DraftVersion).filter(DraftVersion.draft_id == draft_id).order_by(DraftVersion.version_number.asc()).all()
    findings = db.query(Finding).filter(Finding.draft_id == draft_id).all()
    comments = db.query(WorkflowComment).filter(WorkflowComment.draft_id == draft_id).order_by(WorkflowComment.created_at.asc()).all()
    logs = db.query(AuditLog).filter(AuditLog.draft_id == draft_id).order_by(AuditLog.timestamp.desc()).all()

    return {
        "id": draft.id,
        "title": draft.title,
        "content_type": draft.content_type,
        "current_version": draft.current_version,
        "status": draft.status,
        "assigned_role": draft.assigned_role,
        "creator_name": draft.creator_name,
        "content": latest_version.content if latest_version else "",
        "versions": [{"version_number": v.version_number, "created_at": v.created_at, "content": v.content} for v in versions],
        "findings": [
            {
                "id": f.id,
                "rule_or_fact_id": f.rule_or_fact_id,
                "category": f.category,
                "severity": f.severity,
                "claim_verdict": f.claim_verdict,
                "flagged_text": f.flagged_text,
                "start_char": f.start_char,
                "end_char": f.end_char,
                "explanation": f.explanation,
                "cited_source": f.cited_source,
                "cited_excerpt": f.cited_excerpt,
                "citation_verified": f.citation_verified,
                "suggested_fix": f.suggested_fix,
                "status": f.status,
                "dismissal_reason": f.dismissal_reason
            } for f in findings
        ],
        "comments": [
            {
                "id": c.id,
                "author_role": c.author_role,
                "author_name": c.author_name,
                "message": c.message,
                "created_at": c.created_at
            } for c in comments
        ],
        "audit_logs": [
            {
                "id": l.id,
                "action": l.action,
                "actor": l.actor,
                "actor_role": l.actor_role,
                "details": l.details,
                "timestamp": l.timestamp
            } for l in logs
        ]
    }

@router.post("/{draft_id}/action-finding/{finding_id}")
def action_finding(
    draft_id: str, 
    finding_id: str, 
    req: FindingActionRequest, 
    db: Session = Depends(get_db)
):
    try:
        result = WorkflowEngine.apply_finding_action(
            db, 
            finding_id=finding_id,
            action=req.action,
            actor_role=req.actor_role,
            actor_name=req.actor_name,
            custom_replacement=req.custom_replacement,
            dismissal_reason=req.dismissal_reason
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{draft_id}/transition")
def transition_status(
    draft_id: str, 
    req: WorkflowTransitionRequest, 
    db: Session = Depends(get_db)
):
    draft = db.query(DraftDocument).filter(DraftDocument.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    old_status = draft.status
    draft.status = req.new_status
    
    # If approved
    if req.new_status == "APPROVED":
        draft.assigned_role = "completed"
    elif req.new_status == "NEEDS_CHANGES":
        draft.assigned_role = "creator"

    # Add optional comment
    if req.comment and req.comment.strip():
        comment = WorkflowComment(
            id=str(uuid.uuid4())[:8],
            draft_id=draft_id,
            author_role=req.actor_role,
            author_name=req.actor_name,
            message=req.comment.strip()
        )
        db.add(comment)

    WorkflowEngine.log_audit_event(
        db, draft_id, f"STATUS_CHANGED_{req.new_status}", req.actor_name, req.actor_role,
        f"Status transitioned from {old_status} to {req.new_status} by {req.actor_role} ({req.actor_name}). Note: {req.comment or 'None'}"
    )

    db.commit()
    return {"id": draft.id, "status": draft.status, "assigned_role": draft.assigned_role}

@router.post("/{draft_id}/comments")
def add_comment(draft_id: str, req: CommentCreate, db: Session = Depends(get_db)):
    draft = db.query(DraftDocument).filter(DraftDocument.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    comment = WorkflowComment(
        id=str(uuid.uuid4())[:8],
        draft_id=draft_id,
        author_role=req.author_role,
        author_name=req.author_name,
        message=req.message
    )
    db.add(comment)

    WorkflowEngine.log_audit_event(
        db, draft_id, "COMMENT_POSTED", req.author_name, req.author_role,
        f"Comment: '{req.message}'"
    )

    db.commit()
    db.refresh(comment)
    return comment
