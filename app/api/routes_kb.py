from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.db_models import BrandRule, ApprovedFact, BrandAsset
from app.models.schemas import BrandRuleCreate, BrandRuleResponse, ApprovedFactCreate, ApprovedFactResponse

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
