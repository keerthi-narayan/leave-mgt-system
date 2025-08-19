from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, List, Literal

app = FastAPI(title="Leave Management System")

# --- Schemas ---
class EmployeeCreate(BaseModel):
    id: int  # User provides ID
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    department: str = Field(..., min_length=1, max_length=100)
    joining_date: date
    leave_balance: int = 20

class EmployeeOut(EmployeeCreate):
    class Config:
        from_attributes = True

class LeaveApply(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None

class LeaveOut(BaseModel):
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

# --- In-memory storage ---
employees: List[EmployeeCreate] = []
leaves: List[LeaveOut] = []

# --- Routes ---

@app.post("/add-employee", response_model=EmployeeOut)
def add_employee(emp: EmployeeCreate):
    for e in employees:
        if e.email == emp.email:
            raise HTTPException(status_code=400, detail="Email already exists")
        if e.id == emp.id:
            raise HTTPException(status_code=400, detail="Employee ID already exists")
    employees.append(emp)
    return emp

@app.get("/employees", response_model=List[EmployeeOut])
def list_employees():
    return employees

@app.post("/apply-leave", response_model=LeaveOut)
def apply_leave(leave: LeaveApply):
    emp = next((e for e in employees if e.id == leave.employee_id), None)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    days = (leave.end_date - leave.start_date).days + 1
    if days > emp.leave_balance:
        raise HTTPException(status_code=400, detail="Insufficient leave balance")
    leave_record = LeaveOut(
        employee_id=leave.employee_id,
        start_date=leave.start_date,
        end_date=leave.end_date,
        days=days,
        status="PENDING",
        reason=leave.reason
    )
    leaves.append(leave_record)
    return leave_record

@app.get("/leaves", response_model=List[LeaveOut])
def list_leaves():
    return leaves

@app.post("/approve-reject/{employee_id}", response_model=List[LeaveOut])
def approve_reject(employee_id: int, ar: ApproveReject):
    emp_leaves = [l for l in leaves if l.employee_id == employee_id and l.status=="PENDING"]
    if not emp_leaves:
        raise HTTPException(status_code=404, detail="No pending leaves found for this employee")
    
    updated_leaves = []
    for lv in emp_leaves:
        lv.status = "APPROVED" if ar.action=="APPROVE" else "REJECTED"
        if lv.status=="APPROVED":
            emp = next((e for e in employees if e.id==lv.employee_id))
            emp.leave_balance -= lv.days
        updated_leaves.append(lv)
    return updated_leaves
