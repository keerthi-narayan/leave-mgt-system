# Mini Leave Management System (MVP)

FastAPI-based MVP for a 50-employee startup. HR can add employees, apply/approve/reject leaves, and track balances.

## ✅ Features
- Add Employee
- Apply for Leave
- Approve/Reject Leave
- Fetch Leave Balance
- Edge-case validations

## 🗂️ Tech
- FastAPI, SQLAlchemy, Pydantic
- SQLite (MVP) → switch to Postgres/MySQL for growth

## 📦 Setup (Local)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Swagger UI: http://127.0.0.1:8000/docs

## 🔗 API Endpoints
- `POST /employees` – Add employee
- `POST /leaves` – Apply leave
- `POST /leaves/{id}/approve` – Approve
- `POST /leaves/{id}/reject` – Reject
- `GET /employees/{id}/leave-balance` – Balance
- `GET /employees/{id}/leaves` – List leaves

See `api-examples.http` for ready-made requests (VS Code REST Client).

## 🧠 Assumptions
- **Leave balance** starts at 20 days (configurable when creating employee).
- **Calendar days** counted inclusive (weekends/holidays not excluded in MVP).
- Balance is **deducted on approval**, not on application.
- Overlap check blocks overlaps with **PENDING** or **APPROVED** requests.
- No half-days. No official holiday calendar in MVP.
- No authentication in MVP (can be added with JWT roles later).

## 🧪 Edge Cases Handled
- Apply before joining date → `400`
- Apply more days than available → `400`
- Overlapping leave requests → `400`
- Employee not found → `404`
- Invalid date range (end < start) → `400`
- Duplicate emails on employee creation → `400`
- Double-approve / double-reject → `400`
- Rejecting an already approved leave (revocation not supported) → `400`

## 📈 Scaling Plan (50 → 500)
- Switch DB to **PostgreSQL** and add indexes.
- Add **Alembic** migrations.
- Use **gunicorn/uvicorn workers** behind a reverse proxy.
- Add **optimistic concurrency / row locks** on leave approval.
- Extract services (Auth, Accrual, Holidays, Notifications).

## 🚀 Deploy (Render example)
1. Push repo to GitHub.
2. Create a **Render Web Service**:
   - Runtime: Python
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
3. Add a persistent disk if you need to keep SQLite, or switch to Render PostgreSQL.
4. Open the URL and test via `/docs`.

## 📄 HLD & Diagrams
See `HLD.md` (Mermaid diagrams for architecture & ER).

## 🔧 Potential Improvements
- JWT auth & roles (HR vs Employee).
- Accrual policy (monthly credit) and carry-forward rules.
- Company holiday calendar and weekday-only day-count.
- Email/Slack notifications.
- CSV import/export for employees.
- Revocation/Cancel flow after approval with audit trail.
- Idempotency keys and pagination for lists.
- Soft-deletes and audit logs.

## 👀 Screenshots (optional)
Use Swagger UI `/docs` to test visually.

---
**Created:** 2025-08-19
