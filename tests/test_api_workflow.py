import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_draft_workflow_lifecycle():
    """Tests end-to-end draft creation, review findings, accept action, version increment, and approval."""
    # 1. Create draft
    payload = {
        "title": "Launch Campaign Post",
        "content": "Our client-friendly app is the #1 app in India, guaranteed! Get 50% off until 31 August.",
        "content_type": "social_post",
        "creator_name": "Test Creator"
    }
    res = client.post("/api/v1/drafts", json=payload)
    assert res.status_code == 200
    data = res.json()
    draft_id = data["id"]
    assert data["status"] == "NEEDS_CHANGES"
    assert data["assigned_role"] == "reviewer" # Due to #1 app in India (UNVERIFIABLE)

    # 2. Get draft details
    res_details = client.get(f"/api/v1/drafts/{draft_id}")
    assert res_details.status_code == 200
    details = res_details.json()
    findings = details["findings"]
    assert len(findings) >= 3

    # 3. Accept terminology finding (client -> customer)
    term_finding = next((f for f in findings if f["rule_or_fact_id"] == "TERM-12"), None)
    assert term_finding is not None

    action_res = client.post(
        f"/api/v1/drafts/{draft_id}/action-finding/{term_finding['id']}",
        json={
            "action": "accept",
            "actor_role": "creator",
            "actor_name": "Test Creator"
        }
    )
    assert action_res.status_code == 200
    assert action_res.json()["draft_current_version"] == 2 # Incremented to v2!

    # 4. Add comment
    cmt_res = client.post(
        f"/api/v1/drafts/{draft_id}/comments",
        json={
            "author_role": "reviewer",
            "author_name": "Legal Reviewer",
            "message": "Please revise the unverified claim before launch."
        }
    )
    assert cmt_res.status_code == 200

    # 5. Transition to Approved
    trans_res = client.post(
        f"/api/v1/drafts/{draft_id}/transition",
        json={
            "new_status": "APPROVED",
            "actor_role": "manager",
            "actor_name": "Brand Director",
            "comment": "Final sign-off granted."
        }
    )
    assert trans_res.status_code == 200
    assert trans_res.json()["status"] == "APPROVED"
