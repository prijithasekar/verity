import re
from typing import List, Dict, Any

class ClaimExtractor:
    """
    Extracts checkable factual, promotional, and statistical statements:
    - Numerical offers and discounts ("50% off", "$100", "1,200+")
    - Date constraints ("until 31 August", "valid through June")
    - Market leadership claims ("#1 in India", "guaranteed", "industry first")
    - Performance / SLA claims ("99.9% uptime", "zero latency")
    """

    PATTERNS = [
        # Percentage / Discount claims
        (r'(\b\d{1,3}%\s+off\b|\b\d{1,3}%\s+discount\b)', "offer_discount"),
        # Date & validity claims
        (r'(\buntil\s+\d{1,2}\s+[A-Za-z]+\b|\buntil\s+[A-Za-z]+\s+\d{1,2}\b)', "date_deadline"),
        # Superlatives and guarantees
        (r'(#1\s+in\s+[A-Za-z]+|#1\s+app|\bguaranteed!?|\b100%\s+guarantee\b|\bworld\'?s\s+best\b)', "superlative_guarantee"),
        # Metric / Scale claims
        (r'(\b\d{1,3}(?:,\d{3})+\+?\s+[A-Za-z]+|\b99\.\d+%\s+uptime\b)', "scale_metric")
    ]

    @classmethod
    def extract_claims(cls, text: str) -> List[Dict[str, Any]]:
        claims = []
        sentences = re.split(r'(?<=[.!?\n])\s+', text)

        char_offset = 0
        for sentence in sentences:
            stripped = sentence.strip()
            if not stripped:
                char_offset += len(sentence)
                continue

            sentence_start = text.find(stripped, char_offset)
            if sentence_start == -1:
                sentence_start = char_offset
            sentence_end = sentence_start + len(stripped)

            # Check if sentence contains checkable claim markers
            found_markers = []
            for pattern, c_type in cls.PATTERNS:
                matches = re.finditer(pattern, stripped, re.IGNORECASE)
                for m in matches:
                    found_markers.append({
                        "type": c_type,
                        "text": m.group(0),
                        "start": sentence_start + m.start(),
                        "end": sentence_start + m.end()
                    })

            if found_markers:
                claims.append({
                    "sentence": stripped,
                    "start_char": sentence_start,
                    "end_char": sentence_end,
                    "markers": found_markers
                })

            char_offset = sentence_end

        return claims
