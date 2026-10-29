from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

class BrandRule(Base):
    __tablename__ = "brand_rules"

    id = Column(String, primary_key=True, index=True) # e.g. TONE-01, TERM-12
    category = Column(String, index=True) # tone, terminology, claim, accessibility, asset
    rule_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    preferred_pattern = Column(String, nullable=True) # e.g. "customer"
    banned_pattern = Column(String, nullable=True)    # e.g. "client", regex or comma-separated
    source_reference = Column(String, nullable=False) # e.g. Brand Guidelines 2026, Section 3.2
    exact_source_text = Column(Text, nullable=False) # For citation verification
    severity = Column(String, default="MEDIUM")       # HIGH, MEDIUM, LOW
    is_active = Column(Boolean, default=True)
    
    # Guideline Clarity Analytics (Improvement 3)
    times_flagged = Column(Integer, default=0)
    times_accepted = Column(Integer, default=0)
    times_dismissed = Column(Integer, default=0)
    dispute_feedback = Column(JSON, default=list)

class ApprovedFact(Base):
    __tablename__ = "approved_facts"

    id = Column(String, primary_key=True, index=True) # e.g. FACT-01, FACT-21
    category = Column(String, index=True) # pricing, product, metrics, legal, dates
    subject = Column(String, nullable=False)
    fact_statement = Column(Text, nullable=False)
    exact_quote = Column(Text, nullable=False) # The ground-truth string for exact citation verification
    valid_from = Column(String, nullable=True)
    valid_until = Column(String, nullable=True)
    approved_by = Column(String, default="Legal & Compliance Team")
    source_document = Column(String, default="Q3-2026 Fact Sheet v2.1")
    is_active = Column(Boolean, default=True)

class BrandAsset(Base):
    __tablename__ = "brand_assets"

    id = Column(String, primary_key=True, index=True) # e.g. ASSET-01
    name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False) # logo, palette, typography
    rules_json = Column(JSON, default=dict) # e.g. {"primary_hex": "#1E3A8A", "min_contrast": 4.5}

class DraftDocument(Base):
    __tablename__ = "draft_documents"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content_type = Column(String, default="social_post") # social_post, email, press_release, web_copy, docx
    current_version = Column(Integer, default=1)
    status = Column(String, default="NEEDS_CHANGES") # DRAFT, NEEDS_CHANGES, PENDING_APPROVAL, APPROVED, REJECTED
    assigned_role = Column(String, default="creator") # creator, reviewer, manager, admin
    creator_name = Column(String, default="Content Creator")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    versions = relationship("DraftVersion", back_populates="draft", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="draft", cascade="all, delete-orphan")
    comments = relationship("WorkflowComment", back_populates="draft", cascade="all, delete-orphan")
    logs = relationship("AuditLog", back_populates="draft", cascade="all, delete-orphan")

class DraftVersion(Base):
    __tablename__ = "draft_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(String, ForeignKey("draft_documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    sanitized_content = Column(Text, nullable=True)
    findings_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    draft = relationship("DraftDocument", back_populates="versions")

class Finding(Base):
    __tablename__ = "findings"

    id = Column(String, primary_key=True, index=True)
    draft_id = Column(String, ForeignKey("draft_documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    
    rule_or_fact_id = Column(String, nullable=False) # e.g. TONE-03, FACT-21, CLAIM-04
    category = Column(String, nullable=False) # tone, terminology, fact, claim, accessibility
    severity = Column(String, default="MEDIUM") # HIGH, MEDIUM, LOW
    
    # Improvement 2: Three-Way Verdict
    claim_verdict = Column(String, default="NONE") # SUPPORTED, CONTRADICTED, UNVERIFIABLE, VIOLATION, NONE
    
    flagged_text = Column(Text, nullable=False)
    start_char = Column(Integer, default=0)
    end_char = Column(Integer, default=0)
    
    explanation = Column(Text, nullable=False)
    cited_source = Column(String, nullable=False)
    cited_excerpt = Column(Text, nullable=False)
    
    # Improvement 1: Code-level Citation Verification
    citation_verified = Column(Boolean, default=False)
    
    suggested_fix = Column(Text, nullable=True)
    status = Column(String, default="OPEN") # OPEN, ACCEPTED, DISMISSED, EDITED
    dismissal_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    draft = relationship("DraftDocument", back_populates="findings")

class WorkflowComment(Base):
    __tablename__ = "workflow_comments"

    id = Column(String, primary_key=True, index=True)
    draft_id = Column(String, ForeignKey("draft_documents.id"), nullable=False)
    author_role = Column(String, nullable=False) # creator, reviewer, manager, admin
    author_name = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    draft = relationship("DraftDocument", back_populates="comments")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(String, ForeignKey("draft_documents.id"), nullable=True)
    action = Column(String, nullable=False) # e.g. DRAFT_SUBMITTED, FINDING_ACCEPTED, ESCALATED_TO_REVIEWER, APPROVED
    actor = Column(String, nullable=False)
    actor_role = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    draft = relationship("DraftDocument", back_populates="logs")
