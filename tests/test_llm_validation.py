import pytest

from app.schemas.contracts import IntakeCheckResult
from app.services.llm import LLMClient, structured_completion


class BadClient(LLMClient):
    def __init__(self):
        self.calls = 0

    def complete_json(self, prompt: str) -> str:
        self.calls += 1
        if self.calls == 1:
            return '{"proceed": true'
        return '{"proceed": true, "confidence": 0.8, "missing_fields": [], "questions": []}'


def test_structured_repair_retry():
    out = structured_completion(BadClient(), 'x', IntakeCheckResult)
    assert out.proceed is True
    assert out.confidence == 0.8
