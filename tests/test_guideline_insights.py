import pytest
from fastapi import HTTPException
from app.db.database import SessionLocal, Base, engine
from app.db.seed_data import seed_database
from app.services.governance_insights import GovernanceInsightsService
from app.api.routes_kb import refine_brand_rule
from app.models.schemas import RuleRefineRequest
from app.models.db_models import BrandRule, AuditLog, Finding
from app.services.deterministic_checker import DeterministicChecker
from app.services.citation_verifier import CitationVerifier

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
    assert "exact_source_text" in claim_rule
    assert "description" in claim_rule

def test_guideline_refinement_updates_rule_and_logs_audit(db):
    """Guideline Improvement Workflow: Admin refines rule with mandatory rationale, updates DB and audit log."""
    original_rule = db.query(BrandRule).filter(BrandRule.id == "CLAIM-04").first()
    original_text = original_rule.exact_source_text
    original_desc = original_rule.description
    original_banned = original_rule.banned_pattern
    original_pref = original_rule.preferred_pattern
    original_dismissed = original_rule.times_dismissed

    try:
        req = RuleRefineRequest(
            new_description="Market leadership claims permitted only with verified third-party audit.",
            new_exact_source_text="No content may claim '#1 in India' or 'guaranteed' returns without certified audited proof attached.",
            new_banned_pattern=r"\b#1 in India\b|\b#1 app\b|\bguaranteed!\b|\b100% foolproof\b",
            new_preferred_pattern="Leading certified platform in India",
            actor_name="Lead Brand Admin",
            rationale="Creator disputes showed ambiguity around user review awards vs legal certs."
        )

        resp = refine_brand_rule("CLAIM-04", req, db)

        assert resp.description == req.new_description
        assert resp.exact_source_text == req.new_exact_source_text
        assert resp.times_dismissed == 0

        # Verify immutable audit log was created
        audit = db.query(AuditLog).filter(
            AuditLog.action == "GUIDELINE_REFINED",
            AuditLog.actor == "Lead Brand Admin"
        ).first()
        assert audit is not None
        assert "Creator disputes showed ambiguity" in audit.details
        assert original_text in audit.details
        assert req.new_exact_source_text in audit.details
    finally:
        # Restore original state so subsequent benchmark evaluations run against pristine seed
        r = db.query(BrandRule).filter(BrandRule.id == "CLAIM-04").first()
        r.description = original_desc
        r.exact_source_text = original_text
        r.banned_pattern = original_banned
        r.preferred_pattern = original_pref
        r.times_dismissed = original_dismissed
        db.commit()

def test_guideline_refinement_requires_rationale(db):
    """Admin rationale and new exact source text are mandatory."""
    req_missing_rationale = RuleRefineRequest(
        new_description="Test update",
        new_exact_source_text="Test source text",
        actor_name="Brand Admin",
        rationale="   "  # Empty whitespace
    )
    with pytest.raises(HTTPException) as exc_info:
        refine_brand_rule("CLAIM-04", req_missing_rationale, db)
    assert exc_info.value.status_code == 400
    assert "rationale is required" in exc_info.value.detail.lower()

    req_missing_source = RuleRefineRequest(
        new_description="Test update",
        new_exact_source_text="",
        actor_name="Brand Admin",
        rationale="Legitimate rationale"
    )
    with pytest.raises(HTTPException) as exc_info2:
        refine_brand_rule("CLAIM-04", req_missing_source, db)
    assert exc_info2.value.status_code == 400
    assert "exact source text is required" in exc_info2.value.detail.lower()

def test_guideline_refinement_missing_rule_returns_404(db):
    """Attempting to refine a non-existent rule returns 404."""
    req = RuleRefineRequest(
        new_description="Any description",
        new_exact_source_text="Any source text",
        actor_name="Brand Admin",
        rationale="Admin rationale"
    )
    with pytest.raises(HTTPException) as exc_info:
        refine_brand_rule("NONEXISTENT-999", req, db)
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()

def test_guideline_refinement_preserves_historical_findings_and_updates_subsequent_scans(db):
    """Historical findings remain untouched and subsequent reviews use the updated rule."""
    r_orig = db.query(BrandRule).filter(BrandRule.id == "TERM-12").first()
    orig_desc = r_orig.description
    orig_text = r_orig.exact_source_text
    orig_banned = r_orig.banned_pattern
    orig_pref = r_orig.preferred_pattern
    orig_dismissed = r_orig.times_dismissed

    pre_count = db.query(Finding).count()

    try:
        req = RuleRefineRequest(
            new_description="Use member instead of client.",
            new_exact_source_text="We serve members, not clients. Always address users as members.",
            new_banned_pattern=r"\bclient\b|\bclients\b",
            new_preferred_pattern="member",
            actor_name="Brand Lead",
            rationale="Updated customer terminology policy to member community."
        )
        refine_brand_rule("TERM-12", req, db)

        # 1. Historical findings remain intact
        post_count = db.query(Finding).count()
        assert pre_count == post_count

        # 2. Subsequent scan uses the updated rule wording and suggestion
        scanned_findings = DeterministicChecker.scan_deterministic_rules("Every client receives direct support.", db)
        term_finding = next((f for f in scanned_findings if f["rule_or_fact_id"] == "TERM-12"), None)
        assert term_finding is not None
        assert term_finding["cited_excerpt"] == req.new_exact_source_text
        assert term_finding["suggested_fix"] == "member"

        # 3. Citation verification validates against updated rule
        verified, _ = CitationVerifier.filter_and_verify_findings(scanned_findings, db)
        assert any(f["rule_or_fact_id"] == "TERM-12" and f.get("citation_verified") for f in verified)
    finally:
        r = db.query(BrandRule).filter(BrandRule.id == "TERM-12").first()
        r.description = orig_desc
        r.exact_source_text = orig_text
        r.banned_pattern = orig_banned
        r.preferred_pattern = orig_pref
        r.times_dismissed = orig_dismissed
        db.commit()

def test_evaluation_benchmark_executes_authentically(db):
    """Evaluation benchmark executes against curated 8-case suite and returns authentic metrics with disclaimer."""
    benchmark = GovernanceInsightsService.run_evaluation_benchmark(db)

    assert "summary" in benchmark
    assert benchmark["summary"]["total_cases"] == 8
    assert benchmark["summary"]["passed_cases"] == 8
    assert benchmark["summary"]["failed_cases"] == 0
    assert benchmark["summary"]["accuracy"] == 100.0
    assert benchmark["summary"]["precision"] == 100.0
    assert benchmark["summary"]["recall"] == 100.0
    assert len(benchmark["test_cases"]) == 8
    assert "Curated regression test set" in benchmark["scope_disclaimer"]
