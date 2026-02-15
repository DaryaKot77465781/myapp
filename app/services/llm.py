import json
from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.schemas.contracts import IntakeCheckResult, RecommendationResult, RoadmapPlanResult, SkillExtractResult

T = TypeVar('T', bound=BaseModel)


class LLMClient(ABC):
    @abstractmethod
    def complete_json(self, prompt: str) -> str: ...


class MockLLMClient(LLMClient):
    def complete_json(self, prompt: str) -> str:
        if 'IntakeCheckResult' in prompt:
            return json.dumps({'proceed': True, 'confidence': 0.86, 'missing_fields': [], 'questions': []})
        if 'SkillExtractResult' in prompt:
            return json.dumps({'skills': [
                {'raw_name': 'Python', 'canonical_name': 'Python', 'level_estimate': 4, 'confidence': 0.9, 'evidence_snippets': ['Built APIs in Python']},
                {'raw_name': 'SQL', 'canonical_name': 'SQL', 'level_estimate': 3, 'confidence': 0.84, 'evidence_snippets': ['Wrote analytics queries']}
            ]})
        if 'RoadmapPlanResult' in prompt:
            return json.dumps({'coverage_score': 0.6, 'must_have_missing': [], 'gaps': [], 'phases': []})
        return json.dumps({'items': []})


def _repair_json(raw: str) -> str:
    repaired = raw.strip()
    if not repaired.endswith('}'):
        repaired += '}'
    return repaired


def structured_completion(client: LLMClient, prompt: str, schema: type[T], retries: int = 2) -> T:
    last_err = None
    for _ in range(retries + 1):
        raw = client.complete_json(prompt)
        try:
            return schema.model_validate_json(raw)
        except (ValidationError, json.JSONDecodeError) as err:
            last_err = err
            try:
                repaired = _repair_json(raw)
                return schema.model_validate_json(repaired)
            except Exception as inner:
                last_err = inner
                continue
    raise ValueError(f'Failed structured output validation: {last_err}')


def intake_check(client: LLMClient, resume_text: str) -> IntakeCheckResult:
    prompt = f'Return IntakeCheckResult JSON only for resume: {resume_text[:1500]}'
    return structured_completion(client, prompt, IntakeCheckResult)


def extract_skills(client: LLMClient, resume_text: str) -> SkillExtractResult:
    prompt = f'Return SkillExtractResult JSON only for resume: {resume_text[:2000]}'
    return structured_completion(client, prompt, SkillExtractResult)


def generate_roadmap(client: LLMClient, context: str) -> RoadmapPlanResult:
    prompt = f'Return RoadmapPlanResult JSON only. Context: {context[:2000]}'
    return structured_completion(client, prompt, RoadmapPlanResult)


def generate_recommendations(client: LLMClient, context: str) -> RecommendationResult:
    prompt = f'Return RecommendationResult JSON only. Context: {context[:2000]}'
    return structured_completion(client, prompt, RecommendationResult)
