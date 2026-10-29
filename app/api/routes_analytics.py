from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.governance_insights import GovernanceInsightsService

router = APIRouter(prefix="/analytics", tags=["Governance & Clarity Insights"])

@router.get("/guideline-clarity")
def get_guideline_clarity_insights(db: Session = Depends(get_db)):
    """
    IMPROVEMENT 3: Guideline-Clarity Insights.
    Returns calculated dispute rates, flagged ambiguity rules, recurring issue categories,
    and recommendations for brand admins.
    """
    return GovernanceInsightsService.generate_clarity_report(db)

@router.get("/evaluation-benchmark")
def get_evaluation_benchmark(db: Session = Depends(get_db)):
    """
    Returns authentic evaluation results and metrics for the curated 8-case benchmark,
    complete with scope disclaimers and per-case verification traces.
    """
    return GovernanceInsightsService.run_evaluation_benchmark(db)
