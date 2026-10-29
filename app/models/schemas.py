from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class BrandRuleBase(BaseModel):
    id: str
    category: str
    rule_name: str
    description: str
    preferred_pattern: Optional[str] = None
    banned_pattern: Optional[str] = None
    source_reference: str
    exact_source_text: str
    severity: str = "MEDIUM"
    is_active: bool = True

class BrandRuleCreate(BrandRuleBase):
    pass

class BrandRuleResponse(BrandRuleBase):
    times_flagged: int = 0
    times_accepted: int = 0
    times_dismissed: int = 0
    clarity_score: Optional[float] = None

    class Config:
        from_attributes = True

class ApprovedFactBase(BaseModel):
    id: str
    category: str
    subject: str
    fact_statement: str
    exact_quote: str
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    approved_by: str = "Legal & Compliance Team"
    source_document: str = "Q3-2026 Fact Sheet v2.1"
    is_active: bool = True

class ApprovedFactCreate(ApprovedFactBase):
    pass

class ApprovedFactResponse(ApprovedFactBase):
    class Config:
        from_attributes = True

class FindingResponse(BaseModel):
    id: str
    draft_id: str
    version_number: int
    rule_or_fact_id: str
    category: str
    severity: str
    claim_verdict: str
    flagged_text: str
    start_char: int
    end_char: int
    explanation: str
    cited_source: str
    cited_excerpt: str
    citation_verified: bool
    suggested_fix: Optional[str] = None
    status: str
    dismissal_reason: Optional[str] = None

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    author_role: str
    author_name: str
    message: str

class CommentResponse(BaseModel):
    id: str
    draft_id: str
    author_role: str
    author_name: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    draft_id: str
    action: str
    actor: str
    actor_role: str
    details: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class DraftCreateRequest(BaseModel):
    title: str
    content: str
    content_type: str = "social_post"
    creator_name: str = "Content Creator"

class DraftUpdateRequest(BaseModel):
    content: str
    actor_role: str = "creator"
    actor_name: str = "Content Creator"

class FindingActionRequest(BaseModel):
    action: str # "accept" | "dismiss" | "edit"
    actor_role: str
    actor_name: str
    custom_replacement: Optional[str] = None
    dismissal_reason: Optional[str] = None

class WorkflowTransitionRequest(BaseModel):
    new_status: str # "PENDING_APPROVAL" | "APPROVED" | "REJECTED" | "NEEDS_CHANGES"
    actor_role: str
    actor_name: str
    comment: Optional[str] = None

class RuleRefineRequest(BaseModel):
    new_description: str
    new_exact_source_text: str
    new_banned_pattern: Optional[str] = None
    new_preferred_pattern: Optional[str] = None
    actor_name: str = "Brand Administrator"
    rationale: str
    draft_id: Optional[str] = None

class ContrastCheckRequest(BaseModel):
    fg_hex: str
    bg_hex: str
    font_size: float = 16.0
    is_bold: bool = False

class ContrastCheckResponse(BaseModel):
    ratio: float
    passes_aa_normal: bool
    passes_aa_large: bool
    passes_aaa_normal: bool
    status: str
    recommendation: Optional[str] = None
