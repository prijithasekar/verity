from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.db_models import BrandRule, ApprovedFact, BrandAsset, AuditLog
from app.models.schemas import (
    BrandRuleCreate, BrandRuleResponse, ApprovedFactCreate, ApprovedFactResponse,
    RuleRefineRequest
)

router = APIRouter(prefix="/knowledge-base", tags=["Brand Knowledge Base"])

@router.get("/rules", response_model=List[BrandRuleResponse])
def get_brand_rules(db: Session = Depends(get_db)):
    rules = db.query(BrandRule).all()
    # Calculate clarity score
    results = []
    for r in rules:
        total = (r.times_accepted or 0) + (r.times_dismissed or 0)
        clarity = round((r.times_accepted / total * 100), 1) if total > 0 else 100.0
        data = BrandRuleResponse.from_orm(r)
        data.clarity_score = clarity
        results.append(data)
    return results

@router.post("/rules", response_model=BrandRuleResponse)
def create_brand_rule(rule_in: BrandRuleCreate, db: Session = Depends(get_db)):
    existing = db.query(BrandRule).filter(BrandRule.id == rule_in.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Rule ID {rule_in.id} already exists.")
    
    rule = BrandRule(**rule_in.dict())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.patch("/rules/{rule_id}/refine", response_model=BrandRuleResponse)
def refine_brand_rule(rule_id: str, req: RuleRefineRequest, db: Session = Depends(get_db)):
    """
    Guideline Improvement Workflow:
    Allows a Brand Administrator to refine an ambiguous guideline based on creator dispute feedback.
    Requires explicit human administrator identity and mandatory rationale.
    Records the change in the AuditLog and preserves review history.
    """
    if not req.rationale or not req.rationale.strip():
        raise HTTPException(status_code=400, detail="Administrator rationale is required to refine a guideline.")
    if not req.new_exact_source_text or not req.new_exact_source_text.strip():
        raise HTTPException(status_code=400, detail="New exact source text is required.")

    rule = db.query(BrandRule).filter(BrandRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule ID '{rule_id}' not found.")

    old_text = rule.exact_source_text

    # Update rule attributes safely
    rule.description = req.new_description.strip()
    rule.exact_source_text = req.new_exact_source_text.strip()
    if req.new_banned_pattern is not None:
        rule.banned_pattern = req.new_banned_pattern.strip()
    if req.new_preferred_pattern is not None:
        rule.preferred_pattern = req.new_preferred_pattern.strip()

    # Reset active dispute count to reflect clarified rule
    rule.times_dismissed = 0

    # Log immutable audit event
    audit_entry = AuditLog(
        draft_id=req.draft_id or "ORG-POLICY",
        action="GUIDELINE_REFINED",
        actor=req.actor_name,
        actor_role="admin",
        details=(
            f"Rule {rule.id} ({rule.rule_name}) refined by {req.actor_name}. "
            f"Rationale: '{req.rationale.strip()}'. "
            f"Previous Excerpt: '{old_text}'. Updated Excerpt: '{rule.exact_source_text}'."
        )
    )
    db.add(audit_entry)

    db.commit()
    db.refresh(rule)

    total = (rule.times_accepted or 0) + (rule.times_dismissed or 0)
    clarity = round((rule.times_accepted / total * 100), 1) if total > 0 else 100.0
    resp = BrandRuleResponse.model_validate(rule)
    resp.clarity_score = clarity
    return resp

@router.get("/facts", response_model=List[ApprovedFactResponse])
def get_approved_facts(db: Session = Depends(get_db)):
    return db.query(ApprovedFact).all()

@router.post("/facts", response_model=ApprovedFactResponse)
def create_approved_fact(fact_in: ApprovedFactCreate, db: Session = Depends(get_db)):
    existing = db.query(ApprovedFact).filter(ApprovedFact.id == fact_in.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Fact ID {fact_in.id} already exists.")

    fact = ApprovedFact(**fact_in.dict())
    db.add(fact)
    db.commit()
    db.refresh(fact)
    return fact

@router.get("/assets")
def get_brand_assets(db: Session = Depends(get_db)):
    return db.query(BrandAsset).all()
