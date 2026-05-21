from pydantic import BaseModel
from typing import List, Optional


class OptionOut(BaseModel):
    option_id: int
    option_text: str


class QuestionOut(BaseModel):
    question_id: int
    question_text: str
    question_type: str
    allocation_id: Optional[int]
    options: List[OptionOut] = []

    class Config:
        from_attributes = True


class CycleOut(BaseModel):
    cycle_id: int
    name: str
    status: str

    class Config:
        from_attributes = True


class AssessmentResponseIn(BaseModel):
    cycle_id: int
    employee_id: int
    allocation_id: int
    question_id: int
    option_ids: Optional[List[int]] = None
    response_text: Optional[List[str]] = None


class AssessmentResponseOut(BaseModel):
    question_id: int
    question_text: str
    question_type: str
    option_ids: Optional[List[int]] = None
    response_text: Optional[List[str]] = None

    class Config:
        from_attributes = True
