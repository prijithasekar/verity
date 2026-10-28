import pytest
from app.db.database import SessionLocal, Base, engine
from app.db.seed_data import seed_database
from app.models.schemas import (
    DraftCreateRequest, FindingActionRequest, WorkflowTransitionRequest, CommentCreate
)
from app.api.routes_workflow import (
    create_and_review_draft, get_draft_details, get_escalated_drafts,
    action_finding, add_comment, transition_status
)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    seed_database(session)
    yield session
    session.close()

def test_full_draft_workflow_lifecycle(db):
    """Tests end-to-end draft creation, review findings, accept action, version increment, escalation queue, and approval."""
    # 1. Create draft
    payload = DraftCreateRequest(
        title="Launch Campaign Post",
        content="Our client-friendly app is the #1 app in India, guaranteed! Get 50% off until 31 August.",
        content_type="social_post",
        creator_name="Test Creator"
    )
    data = create_and_review_draft(payload, db)
    draft_id = data["id"]
    assert data["status"] == "NEEDS_CHANGES"
    assert data["assigned_role"] == "reviewer" # Due to #1 app in India (UNVERIFIABLE)

    # 2. Get draft details
    details = get_draft_details(draft_id, db)
    findings = details["findings"]
    assert len(findings) >= 3

    # 2b. Check escalated queue (Improvement 2: /escalated)
    escalated = get_escalated_drafts(db)
    assert any(d["id"] == draft_id for d in escalated)

    # 3. Accept terminology finding (client -> customer)
    term_finding = next((f for f in findings if f["rule_or_fact_id"] == "TERM-12"), None)
    assert term_finding is not None

    action_res = action_finding(
        draft_id,
        term_finding["id"],
        FindingActionRequest(action="accept", actor_role="creator", actor_name="Test Creator"),
        db
    )
    assert action_res["draft_current_version"] == 2 # Incremented to v2!

    # 4. Add comment
    cmt_res = add_comment(
        draft_id,
        CommentCreate(
            author_role="reviewer",
            author_name="Legal Reviewer",
            message="Please revise the unverified claim before launch."
        ),
        db
    )
    assert cmt_res.message == "Please revise the unverified claim before launch."

    # 5. Transition to Approved
    trans_res = transition_status(
        draft_id,
        WorkflowTransitionRequest(
            new_status="APPROVED",
            actor_role="manager",
            actor_name="Brand Director",
            comment="Final sign-off granted."
        ),
        db
    )
    assert trans_res["status"] == "APPROVED"
