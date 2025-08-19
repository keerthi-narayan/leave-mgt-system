from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, List, Literal

class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    department: str = Field(..., min_length=1, max_length=100)
    joining_date: date
    leave_balance: int = 20

class EmployeeOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    joining_date: date
    leave_balance: int

    class Config:
        from_attributes = True

class LeaveApply(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None

class LeaveOut(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    days: int
    status: Literal["PENDING","APPROVED","REJECTED"]
    reason: Optional[str] = None

    class Config:
        from_attributes = True

class ApproveReject(BaseModel):
    action: Literal["APPROVE","REJECT"]
