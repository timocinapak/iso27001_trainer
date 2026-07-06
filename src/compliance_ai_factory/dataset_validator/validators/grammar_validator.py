import re

from typing import Any

from compliance_ai_factory.common.models.base import DatasetSample
from compliance_ai_factory.dataset_validator import Validator


class GrammarValidator(Validator):
    def __init__(self, knowledge_pack: Any = None) -> None:
        self.knowledge_pack = knowledge_pack

    PLACEHOLDER_PATTERNS = [
        r"TODO", r"FIXME", r"lorem ipsum", r"placeholder",
        r"sample text", r"to be filled",
    ]

    def validate(self, sample: DatasetSample) -> list[str]:
        errors: list[str] = []
        text_values = [str(v) for v in sample.content.values() if isinstance(v, str)]
        for text in text_values:
            if not text:
                continue
            if len(text.split()) < 3:
                errors.append(f"Content too short: '{text[:50]}'")
                continue
            caps = sum(1 for c in text if c.isupper())
            if len(text) > 0 and caps / len(text) > 0.5:
                errors.append("Excessive capitalization detected")
            if re.search(r"[!?]{3,}", text):
                errors.append("Repeated punctuation detected")
            for pattern in self.PLACEHOLDER_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    errors.append(f"Placeholder text detected: '{pattern.lower()}'")
                    break
            sentences = re.split(r'[.!?]+', text)
            for sent in sentences:
                word_count = len(sent.split())
                if word_count > 100:
                    errors.append(f"Overly long sentence ({word_count} words)")
        return errors
