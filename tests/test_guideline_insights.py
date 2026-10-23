import pytest
from app.db.database import SessionLocal, Base, engine
from app.db.seed_data import seed_database
from app.services.governance_insights import GovernanceInsightsService

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    seed_database(session)
    yield session
    session.close()

def test_guideline_clarity_identifies_ambiguous_rule(db):
    """Improvement 3: Rules with high dispute rates are flagged as HIGH_AMBIGUITY."""
    report = GovernanceInsightsService.generate_clarity_report(db)

    assert "summary" in report
    assert report["summary"]["high_ambiguity_rules_count"] >= 1
    assert report["summary"]["top_disputed_rule"] == "CLAIM-04"

    # Verify CLAIM-04 is categorized as ambiguous
    claim_rule = next((r for r in report["all_rules_clarity"] if r["id"] == "CLAIM-04"), None)
    assert claim_rule is not None
    assert claim_rule["status"] == "HIGH_AMBIGUITY"
    assert claim_rule["dismissal_rate"] > 40.0
    assert len(claim_rule["dispute_feedback"]) > 0
    assert "Admin action required" in claim_rule["recommendation"]
