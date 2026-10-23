import difflib
from typing import Dict, Any, List

class SuggestionGenerator:
    """
    Produces intent-preserving rewrites and visual diffs.
    Guarantees the author's primary communicative purpose is respected 
    while bringing the phrasing into full brand compliance.
    """

    @staticmethod
    def generate_diff(original: str, replacement: str) -> Dict[str, Any]:
        """Generates inline HTML diff highlighting removals and additions."""
        words_orig = original.split()
        words_repl = replacement.split()

        matcher = difflib.SequenceMatcher(None, words_orig, words_repl)
        diff_fragments = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                diff_fragments.append(" ".join(words_orig[i1:i2]))
            elif tag == 'delete':
                diff_fragments.append(f'<del class="bg-red-200 text-red-900 line-through px-1 rounded">{" ".join(words_orig[i1:i2])}</del>')
            elif tag == 'insert':
                diff_fragments.append(f'<ins class="bg-green-200 text-green-900 no-underline font-semibold px-1 rounded">{" ".join(words_repl[j1:j2])}</ins>')
            elif tag == 'replace':
                diff_fragments.append(f'<del class="bg-red-200 text-red-900 line-through px-1 rounded">{" ".join(words_orig[i1:i2])}</del> '
                                      f'<ins class="bg-green-200 text-green-900 no-underline font-semibold px-1 rounded">{" ".join(words_repl[j1:j2])}</ins>')

        diff_html = " ".join(diff_fragments)
        return {
            "original": original,
            "replacement": replacement,
            "diff_html": diff_html
        }

    @classmethod
    def apply_suggestion_to_text(cls, full_text: str, flagged_text: str, suggested_fix: str) -> str:
        """Applies accepted suggestion cleanly to the draft document."""
        if not suggested_fix or not flagged_text:
            return full_text
        
        # Replace first occurrence
        return full_text.replace(flagged_text, suggested_fix, 1)
