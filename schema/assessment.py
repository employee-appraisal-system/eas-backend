# schemas/assessment.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import date


class RatingBase(BaseModel):
    parameter_id: int
    rating: int = Field(..., ge=1, le=4)
    specific_input: Optional[str] = None


class RatingRequest(RatingBase):
    cycle_id: int
    employee_id: int
    discussion_date: date


class RatingResponse(RatingBase):
    lead_rating_id: int
    allocation_id: int
    cycle_id: int
    employee_id: int
    discussion_completion: date

    class Config:
        from_attributes = True


class BatchRatingRequest(BaseModel):
    cycle_id: int
    employee_id: int
    discussion_date: date
    ratings: List[RatingBase]


class AssessmentStatus(BaseModel):
    cycle_id: int
    cycle_name: str
    cycle_status: str
    employee_id: int
    employee_name: str
    role: str
    parameters: List[Dict[str, Any]]
    completion_percentage: float

    class Config:
        from_attributes = True
