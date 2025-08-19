from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date

from . import models, schemas
from .utils import inclusive_days, dates_overlap

def create_employee(db: Session, emp: schemas.EmployeeCreate) -> models.Employee:
    # Check duplicate email
    existing = db.execute(select(models.Employee).where(models.Employee.email == emp.email)).scalar_one_or_none()
    if existing:
        raise ValueError("Employee with this email already exists.")
    m = models.Employee(
        name=emp.name,
        email=emp.email,
        department=emp.department,
        joining_date=emp.joining_date,
        leave_balance=emp.leave_balance,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def get_employee(db: Session, emp_id: int) -> models.Employee | None:
    return db.get(models.Employee, emp_id)

def get_employee_by_email(db: Session, email: str) -> models.Employee | None:
    return db.execute(select(models.Employee).where(models.Employee.email == email)).scalar_one_or_none()

def list_leaves_for_employee(db: Session, emp_id: int):
    return db.execute(select(models.LeaveRequest).where(models.LeaveRequest.employee_id == emp_id)).scalars().all()

def apply_leave(db: Session, req: schemas.LeaveApply) -> models.LeaveRequest:
    emp = get_employee(db, req.employee_id)
    if not emp:
        raise LookupError("Employee not found.")

    # Validate dates
    if req.end_date < req.start_date:
        raise ValueError("End date is before start date.")
    if req.start_date < emp.joining_date:
        raise ValueError("Cannot apply leave before joining date.")

    # Overlap with existing PENDING/APPROVED
    existing_leaves = list_leaves_for_employee(db, emp.id)
    for l in existing_leaves:
        if l.status in [models.LeaveStatus.PENDING, models.LeaveStatus.APPROVED]:
            if dates_overlap(req.start_date, req.end_date, l.start_date, l.end_date):
                raise ValueError("Overlapping with an existing leave request.")

    days = inclusive_days(req.start_date, req.end_date)

    # Check available balance at apply-time (soft check)
    if days > emp.leave_balance:
        raise ValueError("Requested days exceed available balance.")

    leave = models.LeaveRequest(
        employee_id=emp.id,
        start_date=req.start_date,
        end_date=req.end_date,
        days=days,
        status=models.LeaveStatus.PENDING,
        reason=req.reason,
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave

def approve_leave(db: Session, leave_id: int) -> models.LeaveRequest:
    leave = db.get(models.LeaveRequest, leave_id)
    if not leave:
        raise LookupError("Leave request not found.")
    if leave.status == models.LeaveStatus.APPROVED:
        raise ValueError("Leave already approved.")
    if leave.status == models.LeaveStatus.REJECTED:
        raise ValueError("Cannot approve a rejected leave.")

    emp = db.get(models.Employee, leave.employee_id)
    if leave.days > emp.leave_balance:
        raise ValueError("Insufficient balance at approval time.")

    # Deduct balance
    emp.leave_balance -= leave.days
    leave.status = models.LeaveStatus.APPROVED
    db.add(emp)
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave

def reject_leave(db: Session, leave_id: int) -> models.LeaveRequest:
    leave = db.get(models.LeaveRequest, leave_id)
    if not leave:
        raise LookupError("Leave request not found.")
    if leave.status == models.LeaveStatus.REJECTED:
        raise ValueError("Leave already rejected.")
    if leave.status == models.LeaveStatus.APPROVED:
        raise ValueError("Cannot reject an approved leave (revoke not supported in MVP).")

    leave.status = models.LeaveStatus.REJECTED
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave
