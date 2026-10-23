import pytest
from app.db.database import SessionLocal, Base, engine
from app.db.seed_data import seed_database
from app.services.citation_verifier import CitationVerifier

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    seed_database(session)
    yield session
    session.close()

def test_genuine_citation_verified(db):
    """Improvement 1: Real excerpt from KB is verified."""
    genuine_finding = {
        "rule_or_fact_id": "TERM-12",
        "cited_excerpt": "We serve customers, not clients. Always address our platform users as customers or community members."
    }
    is_valid, reason = CitationVerifier.verify_finding_citation(genuine_finding, db)
    assert is_valid is True
    assert "Verified" in reason

def test_hallucinated_citation_discarded(db):
    """Improvement 1: Hallucinated / invented guideline is discarded."""
    fabricated_finding = {
        "rule_or_fact_id": "TERM-12",
        "cited_excerpt": "You must never use the word client because our CEO dislikes it intensely."
    }
    is_valid, reason = CitationVerifier.verify_finding_citation(fabricated_finding, db)
    assert is_valid is False
    assert "HALLUCINATION REJECTED" in reason

def test_nonexistent_rule_rejected(db):
    """Improvement 1: Invented rule ID is rejected."""
    fake_rule_finding = {
        "rule_or_fact_id": "MADE-UP-99",
        "cited_excerpt": "Some invented rule excerpt."
    }
    is_valid, reason = CitationVerifier.verify_finding_citation(fake_rule_finding, db)
    assert is_valid is False
    assert "REJECTED" in reason
