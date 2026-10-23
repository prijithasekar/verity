import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.db_models import DraftDocument, DraftVersion, Finding, WorkflowComment, AuditLog, BrandRule
from app.services.suggestion_generator import SuggestionGenerator

class WorkflowEngine:
    """
    Manages review workflow, human oversight, and role transitions:
    - Creator, Reviewer, Manager, Admin
    - Version history tracking (v1 -> v2)
    - Improvement 2: Automatic escalation of Unverifiable / High-severity claims to Reviewer
    - Dismissal tracking with required rationale to feed Guideline Clarity insights
    """

    @classmethod
    def determine_assigned_role(cls, findings: list) -> str:
        """
        Improvement 2:
        High-severity claims and UNVERIFIABLE verdicts are routed to authorized reviewer;
        standard reviews route to manager.
        """
        for f in findings:
            verdict = f.get("claim_verdict", "")
            severity = f.get("severity", "")
            status = f.get("status", "OPEN")
            if status == "OPEN":
                if verdict == "UNVERIFIABLE" or severity == "HIGH":
                    return "reviewer"
        return "manager"

    @classmethod
    def log_audit_event(cls, db: Session, draft_id: str, action: str, actor: str, actor_role: str, details: str = None):
        log = AuditLog(
            draft_id=draft_id,
            action=action,
            actor=actor,
            actor_role=actor_role,
            details=details,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(log)
        db.commit()

    @classmethod
    def apply_finding_action(
        cls, 
        db: Session, 
        finding_id: str, 
        action: str, 
        actor_role: str, 
        actor_name: str,
        custom_replacement: Optional[str] = None,
        dismissal_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        if not finding:
            raise ValueError(f"Finding {finding_id} not found.")

        draft = db.query(DraftDocument).filter(DraftDocument.id == finding.draft_id).first()
        rule = db.query(BrandRule).filter(BrandRule.id == finding.rule_or_fact_id).first()

        latest_version = db.query(DraftVersion).filter(
            DraftVersion.draft_id == draft.id,
            DraftVersion.version_number == draft.current_version
        ).first()

        current_content = latest_version.content if latest_version else ""

        if action == "accept":
            replacement = custom_replacement or finding.suggested_fix or ""
            new_content = SuggestionGenerator.apply_suggestion_to_text(
                current_content, 
                finding.flagged_text, 
                replacement
            )

            # Update finding status
            finding.status = "ACCEPTED"
            
            # Increment rule acceptance count
            if rule:
                rule.times_accepted = (rule.times_accepted or 0) + 1

            # Bump version
            draft.current_version += 1
            new_version = DraftVersion(
                draft_id=draft.id,
                version_number=draft.current_version,
                content=new_content,
                sanitized_content=new_content,
                findings_count=max(0, latest_version.findings_count - 1 if latest_version else 0)
            )
            db.add(new_version)
            
            cls.log_audit_event(
                db, draft.id, "SUGGESTION_ACCEPTED", actor_name, actor_role,
                f"Accepted suggestion for {finding.rule_or_fact_id}: '{finding.flagged_text}' -> '{replacement}' (version incremented to v{draft.current_version})"
            )

        elif action == "dismiss":
            if not dismissal_reason or not dismissal_reason.strip():
                raise ValueError("Dismissal requires a documented reason to feed guideline clarity insights.")

            finding.status = "DISMISSED"
            finding.dismissal_reason = dismissal_reason.strip()

            # Increment rule dismissal count and add feedback (Improvement 3)
            if rule:
                rule.times_dismissed = (rule.times_dismissed or 0) + 1
                feedback_list = list(rule.dispute_feedback or [])
                feedback_list.append(f"[{actor_role.upper()}: {actor_name}] {dismissal_reason.strip()}")
                rule.dispute_feedback = feedback_list

            cls.log_audit_event(
                db, draft.id, "FINDING_DISMISSED", actor_name, actor_role,
                f"Dismissed finding {finding.rule_or_fact_id}. Reason: {dismissal_reason.strip()}"
            )

        elif action == "edit":
            replacement = custom_replacement or ""
            new_content = SuggestionGenerator.apply_suggestion_to_text(
                current_content, 
                finding.flagged_text, 
                replacement
            )
            finding.status = "EDITED"

            # Bump version
            draft.current_version += 1
            new_version = DraftVersion(
                draft_id=draft.id,
                version_number=draft.current_version,
                content=new_content,
                sanitized_content=new_content,
                findings_count=latest_version.findings_count if latest_version else 0
            )
            db.add(new_version)

            cls.log_audit_event(
                db, draft.id, "MANUAL_EDIT", actor_name, actor_role,
                f"Custom edit applied for {finding.rule_or_fact_id}: '{replacement}' (v{draft.current_version})"
            )

        # Check remaining open findings to re-evaluate assigned role
        open_findings = db.query(Finding).filter(
            Finding.draft_id == draft.id,
            Finding.status == "OPEN"
        ).all()
        
        draft.assigned_role = cls.determine_assigned_role([
            {"claim_verdict": f.claim_verdict, "severity": f.severity, "status": f.status}
            for f in open_findings
        ])

        db.commit()
        return {
            "finding_id": finding.id,
            "status": finding.status,
            "draft_current_version": draft.current_version,
            "assigned_role": draft.assigned_role
        }
