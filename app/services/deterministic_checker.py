import re
import math
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.db_models import BrandRule

class DeterministicChecker:
    """
    High-speed, predictable rule enforcement:
    - Regex / terminology scanner (preferred vs banned words)
    - Flesch-Kincaid readability scoring
    - WCAG color contrast validation
    - Image accessibility (alt-text presence)
    """

    @staticmethod
    def calculate_relative_luminance(r: int, g: int, b: int) -> float:
        """Converts sRGB to relative luminance per WCAG 2.1 specifications."""
        def channel_lum(val: int) -> float:
            c = val / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * channel_lum(r) + 0.7152 * channel_lum(g) + 0.0722 * channel_lum(b)

    @classmethod
    def calculate_contrast_ratio(cls, hex1: str, hex2: str) -> float:
        """Calculates contrast ratio (L1 + 0.05) / (L2 + 0.05) between two hex colors."""
        def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
            hex_code = hex_code.lstrip("#")
            if len(hex_code) == 3:
                hex_code = "".join([c * 2 for c in hex_code])
            return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

        rgb1 = hex_to_rgb(hex1)
        rgb2 = hex_to_rgb(hex2)
        lum1 = cls.calculate_relative_luminance(*rgb1)
        lum2 = cls.calculate_relative_luminance(*rgb2)

        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        ratio = (lighter + 0.05) / (darker + 0.05)
        return round(ratio, 2)

    @classmethod
    def check_wcag_compliance(cls, fg_hex: str, bg_hex: str, font_size_pt: float = 16.0, is_bold: bool = False) -> Dict[str, Any]:
        ratio = cls.calculate_contrast_ratio(fg_hex, bg_hex)
        is_large_text = font_size_pt >= 18.0 or (font_size_pt >= 14.0 and is_bold)

        passes_aa = ratio >= 3.0 if is_large_text else ratio >= 4.5
        passes_aaa = ratio >= 4.5 if is_large_text else ratio >= 7.0

        return {
            "ratio": ratio,
            "passes_aa_normal": ratio >= 4.5,
            "passes_aa_large": ratio >= 3.0,
            "passes_aaa_normal": ratio >= 7.0,
            "status": "PASS" if passes_aa else "FAIL",
            "recommendation": None if passes_aa else f"Increase contrast between {fg_hex} and {bg_hex} to achieve at least 4.5:1 (current: {ratio}:1)."
        }

    @staticmethod
    def calculate_readability(text: str) -> Dict[str, Any]:
        """Calculates Flesch Reading Ease and estimated Grade Level."""
        words = re.findall(r'\b[A-Za-z0-9\'-]+\b', text)
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if not words or not sentences:
            return {"grade_level": 5.0, "reading_ease": 80.0, "assessment": "Standard"}

        total_words = len(words)
        total_sentences = len(sentences)

        def count_syllables(word: str) -> int:
            word = word.lower()
            count = len(re.findall(r'[aeiouy]+', word))
            if word.endswith('e') and not word.endswith('le') and count > 1:
                count -= 1
            return max(1, count)

        total_syllables = sum(count_syllables(w) for w in words)

        # Flesch-Kincaid Grade Level formula
        grade = 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59
        reading_ease = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)

        grade = max(1.0, round(grade, 1))
        reading_ease = round(max(0.0, min(100.0, reading_ease)), 1)

        assessment = "Easy to read" if grade <= 8.0 else ("Moderate" if grade <= 12.0 else "Difficult / Formal")

        return {
            "grade_level": grade,
            "reading_ease": reading_ease,
            "assessment": assessment,
            "word_count": total_words,
            "sentence_count": total_sentences
        }

    @classmethod
    def scan_deterministic_rules(cls, text: str, db: Session) -> List[Dict[str, Any]]:
        """Scans text against all active deterministic BrandRules."""
        rules = db.query(BrandRule).filter(BrandRule.is_active == True).all()
        findings = []

        for rule in rules:
            if not rule.banned_pattern:
                continue

            patterns = [p.strip() for p in rule.banned_pattern.split('|') if p.strip()]
            for pattern_str in patterns:
                try:
                    regex = re.compile(pattern_str, re.IGNORECASE)
                except re.error:
                    # Fallback to literal
                    regex = re.compile(re.escape(pattern_str), re.IGNORECASE)

                for match in regex.finditer(text):
                    flagged = match.group(0)
                    start, end = match.span()

                    # Generate replacement recommendation
                    replacement = rule.preferred_pattern or ""
                    if rule.id == "TERM-12":
                        # Preserve inflection or case
                        if flagged.lower() == "client":
                            replacement = "customer" if flagged.islower() else "Customer"
                        elif flagged.lower() == "clients":
                            replacement = "customers" if flagged.islower() else "Customers"

                    # For claim rules, verdict is UNVERIFIABLE to trigger human reviewer routing
                    verdict = "UNVERIFIABLE" if rule.category == "claim" else "VIOLATION"
                    findings.append({
                        "rule_or_fact_id": rule.id,
                        "category": rule.category,
                        "severity": rule.severity,
                        "claim_verdict": verdict,
                        "flagged_text": flagged,
                        "start_char": start,
                        "end_char": end,
                        "explanation": f"Rule {rule.id}: {rule.description}",
                        "cited_source": rule.source_reference,
                        "cited_excerpt": rule.exact_source_text,
                        "suggested_fix": replacement
                    })

        # Check for image tags without alt text: e.g. [image: banner.png] or ![](...)
        img_pattern = re.compile(r'\[image:\s*([^\]]+)\]', re.IGNORECASE)
        for match in img_pattern.finditer(text):
            flagged = match.group(0)
            start, end = match.span()
            # If line doesn't mention alt or description
            line_context = text[max(0, start-50):min(len(text), end+50)]
            if "alt text" not in line_context.lower() and "alt=" not in line_context.lower():
                rule_acc = db.query(BrandRule).filter(BrandRule.id == "ACC-01").first()
                findings.append({
                    "rule_or_fact_id": "ACC-01",
                    "category": "accessibility",
                    "severity": "HIGH",
                    "claim_verdict": "VIOLATION",
                    "flagged_text": flagged,
                    "start_char": start,
                    "end_char": end,
                    "explanation": "Image tag detected without descriptive alternative text.",
                    "cited_source": rule_acc.source_reference if rule_acc else "WCAG 2.1 Guideline 1.1",
                    "cited_excerpt": rule_acc.exact_source_text if rule_acc else "Non-text content must have text alternative.",
                    "suggested_fix": f"[image: banner.png | alt: Official promotional banner for summer offer]"
                })

        return findings
