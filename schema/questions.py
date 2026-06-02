from pydantic import BaseModel
from typing import List, Optional


class OptionSchema(BaseModel):
    option_text: str


class OptionResponseSchema(OptionSchema):
    option_id: int

    class Config:
        from_attributes = True


class QuestionSchema(BaseModel):
    question_type: str
    question_text: str
    options: Optional[List[OptionSchema]] = []

    class Config:
        arbitrary_types_allowed = True


class QuestionResponseSchema(QuestionSchema):
    question_id: int
    options: List[OptionResponseSchema]

    class Config:
        from_attributes = True


class QuestionsSchema(BaseModel):
    question_id: int
    question_text: str

    class Config:
        from_attributes = True
