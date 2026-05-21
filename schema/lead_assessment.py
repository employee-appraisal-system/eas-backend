from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional


class LeadAssessmentRatingRequest(BaseModel):
    cycle_id: int
    employee_id: int
    ratings: List[dict]
    discussion_date: date

    class Config:
        orm_mode = True


class LeadAssessmentRatingResponse(BaseModel):
    employee_id: int
    parameter_rating: Optional[int]

    class Config:
        orm_mode = True
