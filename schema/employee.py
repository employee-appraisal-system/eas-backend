from pydantic import BaseModel
from typing import Optional


class EmployeeListResponse(BaseModel):
    employee_id: int
    employee_name: str
    reporting_manager_name: str | None


class EmployeeResponse(BaseModel):
    employee_id: int
    employee_name: str
    role: str
    reporting_manager_name: Optional[str] = None
    previous_reporting_manager_name: Optional[str] = None

    class Config:
        orm_mode = True


class EmployeeRoleResponse(BaseModel):
    role: str
