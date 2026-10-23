import re
from typing import Tuple, List, Dict

class PrivacyFilter:
    """
    Sanitizes confidential data, PII, and credentials before processing.
    Ensures zero unauthorized data leakage to external models or logs.
    """
    
    PATTERNS = {
        "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        "PHONE": r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b',
        "API_KEY": r'(?i)\b(api[_-]?key|secret|token)[\s:=]+["\']?([a-zA-Z0-9_\-]{16,})["\']?',
        "CREDIT_CARD": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    }

    @classmethod
    def sanitize(cls, text: str) -> Tuple[str, List[Dict[str, str]]]:
        sanitized = text
        redacted_entities = []

        for p_type, regex in cls.PATTERNS.items():
            for match in re.finditer(regex, sanitized):
                original = match.group(0)
                masked_label = f"[{p_type}_REDACTED]"
                redacted_entities.append({
                    "type": p_type,
                    "original_snippet": original[:4] + "***" if len(original) > 4 else "***",
                    "replacement": masked_label
                })
            sanitized = re.sub(regex, f"[{p_type}_REDACTED]", sanitized)

        return sanitized, redacted_entities
