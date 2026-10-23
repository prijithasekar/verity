import pytest
from app.db.database import SessionLocal, Base, engine
from app.db.seed_data import seed_database
from app.services.claim_extractor import ClaimExtractor
from app.services.grounded_retriever import GroundedRetriever
from app.services.workflow_engine import WorkflowEngine

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    seed_database(session)
    yield session
    session.close()

def test_unverifiable_claim_routes_to_reviewer(db):
    """Improvement 2: Unsupported claims are tagged UNVERIFIABLE and route to reviewer."""
    text = "We are the #1 app in India, guaranteed!"
    claims = ClaimExtractor.extract_claims(text)
    findings = GroundedRetriever.evaluate_claims(claims, db)

    assert len(findings) > 0
    assert findings[0]["claim_verdict"] == "UNVERIFIABLE"
    assert findings[0]["severity"] == "HIGH"

    # Test workflow routing
    assigned_role = WorkflowEngine.determine_assigned_role(findings)
    assert assigned_role == "reviewer"

def test_contradicted_claim_detected(db):
    """Contradicted promotional claims are accurately flagged with approved fact citation."""
    text = "Get 50% off until 31 August on our annual plans."
    claims = ClaimExtractor.extract_claims(text)
    findings = GroundedRetriever.evaluate_claims(claims, db)

    assert len(findings) > 0
    assert findings[0]["claim_verdict"] == "CONTRADICTED"
    assert findings[0]["rule_or_fact_id"] == "FACT-21"
    assert "30%" in findings[0]["suggested_fix"]
    assert "15 August" in findings[0]["suggested_fix"]
