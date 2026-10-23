from app.models.db_models import BrandRule, ApprovedFact, BrandAsset
from sqlalchemy.orm import Session

def seed_database(db: Session):
    # Check if already seeded
    if db.query(BrandRule).first() is not None:
        return

    # 1. Brand Rules
    rules = [
        BrandRule(
            id="TERM-12",
            category="terminology",
            rule_name="Customer-Centric Terminology",
            description="Use 'customer' or 'user' instead of 'client'.",
            preferred_pattern="customer",
            banned_pattern="\\bclient\\b|\\bclients\\b",
            source_reference="Verity Brand Guidelines 2026, Section 2.1",
            exact_source_text="We serve customers, not clients. Always address our platform users as customers or community members.",
            severity="LOW",
            times_flagged=14,
            times_accepted=12,
            times_dismissed=2
        ),
        BrandRule(
            id="TERM-08",
            category="terminology",
            rule_name="Product Naming Convention",
            description="Our primary software platform is 'Verity Core' or 'Verity Platform', never 'Verity Tool' or 'Verity App'.",
            preferred_pattern="Verity Platform",
            banned_pattern="\\bVerity Tool\\b|\\bVerity App\\b",
            source_reference="Verity Brand Book 2026, Section 1.4",
            exact_source_text="Our platform is officially titled Verity Platform. Avoid using informal designations like Verity Tool or Verity App in public communications.",
            severity="MEDIUM",
            times_flagged=6,
            times_accepted=6,
            times_dismissed=0
        ),
        BrandRule(
            id="TONE-03",
            category="tone",
            rule_name="Empathetic Urgency vs FOMO",
            description="Avoid aggressive urgency, clickbait and artificial pressure such as 'hurry up' or 'or regret it'.",
            preferred_pattern="available for a limited period",
            banned_pattern="\\bhurry up\\b|\\bdon't miss out\\b|\\bor regret it\\b|\\bact fast or lose\\b",
            source_reference="Editorial Voice & Tone Guide 2026, Section 3.2",
            exact_source_text="Urgency should be respectful and informative. Never pressure users through manufactured panic, aggressive FOMO, or sensationalist threats.",
            severity="MEDIUM",
            times_flagged=9,
            times_accepted=8,
            times_dismissed=1
        ),
        BrandRule(
            id="TONE-05",
            category="tone",
            rule_name="Inclusive & Accessible Language",
            description="Avoid ableist metaphors like 'blind to changes', 'crazy discounts', or 'insane speed'.",
            preferred_pattern="unprecedented speed",
            banned_pattern="\\binsane\\b|\\bcrazy discounts\\b|\\bblind to\\b",
            source_reference="Inclusive Communication Manual 2026, Section 4",
            exact_source_text="Use inclusive descriptions. Replace ableist slang such as crazy discounts or insane speed with precise, objective descriptions.",
            severity="MEDIUM",
            times_flagged=5,
            times_accepted=4,
            times_dismissed=1
        ),
        BrandRule(
            id="CLAIM-04",
            category="claim",
            rule_name="Unsubstantiated Market Leadership Claims",
            description="Claims of being '#1', 'the best in the world', or 'guaranteed returns' require official certified legal approval.",
            preferred_pattern="Leading brand governance solution",
            banned_pattern="\\b#1 in India\\b|\\b#1 app\\b|\\bguaranteed!\\b|\\b100% foolproof\\b",
            source_reference="Legal & Advertising Standards 2026, Clause 4.8",
            exact_source_text="No content may claim '#1 in India' or 'guaranteed' returns without certified audited proof attached.",
            severity="HIGH",
            times_flagged=18,
            times_accepted=7,
            times_dismissed=11, # High dismissal rate -> surfaces in Guideline Clarity Insights!
            dispute_feedback=[
                "Marketing team feels '#1 ranked by user reviews' is acceptable",
                "Product launch campaign needed superlative phrasing",
                "Creator noted ambiguity between industry awards vs legal claim"
            ]
        ),
        BrandRule(
            id="ACC-01",
            category="accessibility",
            rule_name="Alternative Text Requirement",
            description="All embedded visual banners and figures must provide descriptive alt-text.",
            preferred_pattern="Descriptive alt-text summarizing visual content",
            banned_pattern="no alt text",
            source_reference="Web Accessibility Policy (WCAG 2.1 AA), Section 1.1",
            exact_source_text="All non-text visual content published across web and email channels must include concise, accurate text alternatives.",
            severity="HIGH",
            times_flagged=8,
            times_accepted=7,
            times_dismissed=1
        ),
        BrandRule(
            id="ACC-02",
            category="accessibility",
            rule_name="Color Contrast Compliance",
            description="Body text must maintain at least 4.5:1 contrast against its background according to WCAG AA.",
            preferred_pattern="Compliant color pairing (minimum 4.5:1)",
            banned_pattern="low contrast",
            source_reference="Brand Visual Identity Guide 2026, Section 5",
            exact_source_text="Text visual presentation must satisfy WCAG AA contrast ratio of at least 4.5 to 1 for standard text.",
            severity="MEDIUM",
            times_flagged=4,
            times_accepted=4,
            times_dismissed=0
        )
    ]
    for r in rules:
        db.add(r)

    # 2. Approved Facts
    facts = [
        ApprovedFact(
            id="FACT-21",
            category="pricing",
            subject="Summer Promotion 2026",
            fact_statement="Summer 2026 promotional campaign offers 30% off annual licenses until 15 August 2026.",
            exact_quote="Get 30% off on all annual plans until 15 August 2026.",
            valid_from="2026-06-01",
            valid_until="2026-08-15",
            approved_by="VP of Marketing & CFO",
            source_document="Pricing Matrix Q2-Q3 2026"
        ),
        ApprovedFact(
            id="FACT-14",
            category="metrics",
            subject="Customer Base & Scale",
            fact_statement="Verity is deployed across 1,200+ marketing teams globally with 99.9% verified uptime.",
            exact_quote="Verity supports over 1,200 organizations worldwide with guaranteed 99.9% service availability.",
            valid_from="2026-01-01",
            valid_until="2026-12-31",
            approved_by="Product Operations",
            source_document="Annual Operational Metrics Review 2026"
        ),
        ApprovedFact(
            id="FACT-05",
            category="product",
            subject="Supported Ingestion Formats",
            fact_statement="Verity natively reviews DOCX, PDF, rich text, and raster image banners (PNG/JPEG) before publication.",
            exact_quote="Native format support includes DOCX documents, PDF files, raw text, and PNG/JPEG banner visuals.",
            valid_from="2026-01-01",
            valid_until="2026-12-31",
            approved_by="Chief Architect",
            source_document="Platform Capability Matrix 2026"
        ),
        ApprovedFact(
            id="FACT-33",
            category="legal",
            subject="Data Privacy & Zero Data Retention",
            fact_statement="All uploaded draft assets are scrubbed of PII and never stored in third-party foundation model training corpora.",
            exact_quote="All client drafts are processed under zero-data-retention isolation and are never used to train external models.",
            valid_from="2026-01-01",
            valid_until="2026-12-31",
            approved_by="Data Protection Officer",
            source_document="Privacy & Security Whitepaper 2026"
        )
    ]
    for f in facts:
        db.add(f)

    # 3. Brand Assets
    assets = [
        BrandAsset(
            id="ASSET-01",
            name="Brand Primary Palette",
            asset_type="palette",
            rules_json={
                "navy": "#0F172A",
                "royal_blue": "#1E3A8A",
                "accent_blue": "#3B82F6",
                "background_white": "#FFFFFF",
                "light_tint": "#EFF6FF",
                "danger": "#EF4444",
                "warning": "#F59E0B",
                "success": "#10B981"
            }
        ),
        BrandAsset(
            id="ASSET-02",
            name="Official Vector Logo",
            asset_type="logo",
            rules_json={
                "min_clear_space_px": 24,
                "aspect_ratio": "3.5:1",
                "monochrome_allowed": True
            }
        )
    ]
    for a in assets:
        db.add(a)

    db.commit()
