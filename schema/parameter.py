from pydantic import BaseModel


class ParameterBase(BaseModel):
    parameter_title: str
    helptext: str
    cycle_id: int
    applicable_to_employee: bool
    applicable_to_lead: bool
    is_fixed_parameter: bool


class ParameterCreate(ParameterBase):
    pass


class ParameterResponse(ParameterBase):
    parameter_id: int

    class Config:
        orm_mode = True
