import os

class Settings:
    PROJECT_NAME: str = "Verity — Pre-Publication Brand Governance"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Storage & DB
    DATABASE_URL: str = "sqlite:///./verity.db"
    
    # Security & AI Disclosures
    AI_MODEL_DISCLOSURE: str = "Verity Hybrid Engine (Deterministic Rules + Grounded Verification Model v1.2)"
    CONFIDENTIALITY_NOTICE: str = "All customer content is sanitized and processed under zero-data-retention isolation."
    
    # Review Thresholds
    MIN_CITATION_CONFIDENCE: float = 0.70
    READABILITY_TARGET_GRADE_MAX: float = 12.0
    WCAG_MIN_CONTRAST_RATIO: float = 4.5

settings = Settings()
