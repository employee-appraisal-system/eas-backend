import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dao.appraisal_cycle import get_completed_and_lead_assessment_active_cycles


class FakeQuery:
    def __init__(self):
        self.filter_criterion = None

    def filter(self, criterion):
        self.filter_criterion = criterion
        return self

    def all(self):
        return ["completed-cycle", "active-cycle"]


class FakeSession:
    def __init__(self):
        self.query_obj = FakeQuery()

    def query(self, _model):
        return self.query_obj


def test_lead_assessment_report_cycles_include_active_and_completed():
    db = FakeSession()

    result = get_completed_and_lead_assessment_active_cycles(db)

    assert result == ["completed-cycle", "active-cycle"]
    assert str(db.query_obj.filter_criterion.left) == "appraisal_cycle.status"
    assert db.query_obj.filter_criterion.right.value == ["completed", "active"]