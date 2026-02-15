from types import SimpleNamespace

from app.services.gap_analysis import compute_gap_summary


class FakeDB:
    def __init__(self, reqs, users, skills):
        self.reqs = reqs
        self.users = users
        self.skills = skills

    def execute(self, query):
        class R:
            def __init__(self, rows):
                self._rows = rows

            def scalars(self):
                return self

            def all(self):
                return self._rows

        text = str(query)
        if 'role_requirements' in text:
            return R(self.reqs)
        return R(self.users)

    def get(self, model, pk):
        return SimpleNamespace(canonical_name=self.skills[pk])


def test_gap_formula():
    db = FakeDB(
        reqs=[SimpleNamespace(skill_id=1, required_level=4.0, weight=2.0, must_have=True)],
        users=[SimpleNamespace(skill_id=1, level_estimate=3.0)],
        skills={1: 'Python'},
    )
    out = compute_gap_summary(db, 'p1', 1)
    assert round(out['coverage_score'], 3) == 0.75
    assert len(out['must_have_missing']) == 1
