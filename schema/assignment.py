from pydantic import BaseModel
from typing import List


class AssignmentCreate(BaseModel):
    employee_ids: List[int]
    question_ids: List[int]
    cycle_id: int


class AssignmentResponse(BaseModel):
    employee_id: int
    cycle_id: int
    question_ids: List[int]

    class Config:
        from_attributes = True
