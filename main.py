from math import ceil
from fastapi import Query
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from database import get_db,Base,engine
from models import User

from models import Project, Requirement, Task, User, UserRole, TaskStatus

from functools import wraps
from passlib.context import CryptContext
from typing import Optional

from fastapi.responses import PlainTextResponse
app = FastAPI()


# This creates all tables in PostgreSQL
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print(Base.metadata.tables.keys())

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def role_required(*roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):

            if "user_id" not in request.session:
                return RedirectResponse("/login", status_code=303)

            if request.session.get("role") not in roles:
                return RedirectResponse("/dashboard", status_code=303)

            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


@app.get('/')
def indexpage(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.trace("/")
async def tracecheck(request: Request):
    # Get raw body
    body = await request.body()

    # Build request line
    request_line = f"{request.method} {request.url.path} HTTP/{request.scope['http_version']}\n"

    # Collect headers
    headers = ""
    for key, value in request.headers.items():
        headers += f"{key}: {value}\n"

    # Combine everything
    full_request = request_line + headers + "\n" + body.decode("utf-8")

    return PlainTextResponse(
        content=full_request,
        status_code=200,
        media_type="message/http"
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    print("Email",email,"Password",password)
    user = db.query(User).filter(User.email == email).first()

    if not user or not pwd_context.verify(password, user.password):
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Invalid email or password"}
        )

    # Store session
    request.session["user_id"] = user.id
    request.session["name"] = user.name
    request.session["role"] = user.role.name  # IMPORTANT

    # Redirect to dashboard
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/dashboard")
def dashboard_redirect(request: Request):
    if "user_id" not in request.session:
        return RedirectResponse("/login", status_code=303)

    role = request.session.get("role")

    if role == "PROJECT_MANAGER":
        return RedirectResponse("/project-manager/dashboard", status_code=303)

    elif role == "LEAD":
        return RedirectResponse("/lead-manager/dashboard", status_code=303)

    elif role == "DEVELOPER":
        return RedirectResponse("/developer/dashboard", status_code=303)

    return RedirectResponse("/login", status_code=303)

from sqlalchemy import func
from models import Project, Requirement, User, UserRole
from fastapi import Depends
from database import get_db
from sqlalchemy.orm import Session

@app.get("/project-manager/dashboard")
@role_required("PROJECT_MANAGER")
async def manager_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    manager_id = request.session.get("user_id")

    # ===============================
    # Basic Stats
    # ===============================

    total_projects = db.query(Project).filter(
        Project.created_by == manager_id
    ).count()

    total_tasks = db.query(Task).join(Project).filter(
        Project.created_by == manager_id
    ).count()

    completed_tasks = db.query(Task).join(Project).filter(
        Project.created_by == manager_id,
        Task.status == TaskStatus.COMPLETED
    ).count()

    pending_tasks = db.query(Task).join(Project).filter(
        Project.created_by == manager_id,
        Task.status != TaskStatus.COMPLETED
    ).count()

    # ===============================
    # Alerts Section
    # ===============================

    projects_without_lead = db.query(Project).filter(
        Project.created_by == manager_id,
        Project.project_owner == None
    ).count()

    projects_without_requirements = db.query(Project).filter(
        Project.created_by == manager_id,
        ~Project.requirements.any()
    ).count()

    # ===============================
    # Recent Projects
    # ===============================

    recent_projects = db.query(Project).filter(
        Project.created_by == manager_id
    ).order_by(Project.created_at.desc()).limit(5).all()

    # ===============================
    # Lead Distribution
    # ===============================

    lead_distribution = db.query(
        User.name,
        func.count(Project.id)
    ).join(Project, Project.project_owner == User.id)\
     .filter(Project.created_by == manager_id)\
     .group_by(User.name).all()

    # ===============================
    # Overall Progress %
    # ===============================

    progress_percentage = 0
    if total_tasks > 0:
        progress_percentage = int((completed_tasks / total_tasks) * 100)

    return templates.TemplateResponse(
        "manager_dashboard.html",
        {
            "request": request,
            "total_projects": total_projects,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "projects_without_lead": projects_without_lead,
            "projects_without_requirements": projects_without_requirements,
            "recent_projects": recent_projects,
            "lead_distribution": lead_distribution,
            "progress_percentage": progress_percentage
        }
    )

@app.get("/lead-manager/dashboard")
@role_required("LEAD")
async def lead_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    lead_id = request.session.get("user_id")

    projects = db.query(Project).filter(
        Project.project_owner == lead_id
    ).all()

    dashboard_data = []

    total_tasks = 0
    completed_tasks = 0

    for project in projects:
        tasks = project.tasks

        project_total = len(tasks)
        project_completed = sum(
            1 for t in tasks if t.status == TaskStatus.COMPLETED
        )

        total_tasks += project_total
        completed_tasks += project_completed

        progress = 0
        if project_total > 0:
            progress = int((project_completed / project_total) * 100)

        dashboard_data.append({
            "project": project,
            "tasks": tasks,
            "total_tasks": project_total,
            "completed_tasks": project_completed,
            "progress": progress
        })

    overall_progress = 0
    if total_tasks > 0:
        overall_progress = int((completed_tasks / total_tasks) * 100)

    return templates.TemplateResponse(
        "lead_dashboard.html",
        {
            "request": request,
            "dashboard_data": dashboard_data,
            "total_projects": len(projects),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": total_tasks - completed_tasks,
            "overall_progress": overall_progress
        }
    )



@app.get("/developer/dashboard")
@role_required("DEVELOPER")
async def developer_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    developer_id = request.session.get("user_id")

    tasks = db.query(Task).filter(
        Task.assigned_to == developer_id
    ).all()

    total_tasks = len(tasks)

    completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
    in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
    not_started = sum(1 for t in tasks if t.status == TaskStatus.NOT_STARTED)

    progress = 0
    if total_tasks > 0:
        progress = int((completed / total_tasks) * 100)

    return templates.TemplateResponse(
        "developer_dashboard.html",
        {
            "request": request,
            "tasks": tasks,
            "total_tasks": total_tasks,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "progress": progress
        }
    )

@app.get("/developer/tasks/{task_id}/update")
@role_required("DEVELOPER")
async def update_task_page(
    request: Request,
    task_id: int,
    db: Session = Depends(get_db)
):
    developer_id = request.session.get("user_id")

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.assigned_to == developer_id
    ).first()

    if not task:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        "developer_update_task.html",
        {
            "request": request,
            "task": task
        }
    )

@app.post("/developer/tasks/{task_id}/update")
@role_required("DEVELOPER")
async def update_task(
    request: Request,
    task_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    developer_id = request.session.get("user_id")

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.assigned_to == developer_id
    ).first()

    if not task:
        raise HTTPException(status_code=404)

    task.status = TaskStatus[status]

    db.commit()

    return RedirectResponse(
        "/developer/dashboard",
        status_code=303
    )



@app.get("/logout")
def logout(request: Request):
    request.session.clear()  # remove all session data
    return RedirectResponse(url="/login", status_code=303)




# ============================
# Project List Page
# ============================

@app.get("/project-manager/projects")
@role_required("PROJECT_MANAGER")
async def project_list(
    request: Request,
    db: Session = Depends(get_db)
):
    manager_id = request.session.get("user_id")

    projects = db.query(Project).filter(
        Project.created_by == manager_id
    ).order_by(Project.created_at.desc()).all()

    return templates.TemplateResponse(
        "manager_projects.html",
        {
            "request": request,
            "projects": projects
        }
    )


# ============================
# Create Project Page (GET)
# ============================

@app.get("/project-manager/projects/create")
@role_required("PROJECT_MANAGER")
async def create_project_page(
    request: Request,
    db: Session = Depends(get_db)
):
    leads = db.query(User).filter(
        User.role == UserRole.LEAD
    ).all()

    return templates.TemplateResponse(
        "create_project.html",
        {
            "request": request,
            "leads": leads
        }
    )


# ============================
# Create Project (POST)
# ============================

@app.post("/project-manager/projects/create")
@role_required("PROJECT_MANAGER")
async def create_project(
    request: Request,
    name: str = Form(...),
    lead_id: int = Form(...),
    db: Session = Depends(get_db)
):
    manager_id = request.session.get("user_id")

    project = Project(
        name=name,
        created_by=manager_id,
        project_owner=lead_id
    )

    db.add(project)
    db.commit()

    return RedirectResponse(
        "/manager_dashboard.html",
        status_code=303
    )


from fastapi import HTTPException

@app.get("/project-manager/projects/{project_id}")
@role_required("PROJECT_MANAGER")
async def project_detail(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db)
):
    manager_id = request.session.get("user_id")

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.created_by == manager_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    total_requirements = len(project.requirements)
    total_tasks = len(project.tasks)

    completed_tasks = sum(
        1 for task in project.tasks
        if task.status == TaskStatus.COMPLETED
    )

    pending_tasks = total_tasks - completed_tasks

    progress_percentage = 0
    if total_tasks > 0:
        progress_percentage = int((completed_tasks / total_tasks) * 100)

    return templates.TemplateResponse(
        "project_detail.html",
        {
            "request": request,
            "project": project,
            "total_requirements": total_requirements,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "progress_percentage": progress_percentage
        }
    )

@app.get("/project-manager/projects/{project_id}/requirements/create")
@role_required("PROJECT_MANAGER")
async def add_requirement_page(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        "create_requirement.html",
        {
            "request": request,
            "project": project
        }
    )


@app.post("/project-manager/projects/{project_id}/requirements/create")
@role_required("PROJECT_MANAGER")
async def create_requirement(
    request: Request,
    project_id: int,
    requirement: str = Form(...),
    db: Session = Depends(get_db)
):
    manager_id = request.session.get("user_id")

    new_requirement = Requirement(
        requirement=requirement,
        project_id=project_id,
        created_by=manager_id
    )

    db.add(new_requirement)
    db.commit()

    return RedirectResponse(
        f"/project-manager/projects/{project_id}",
        status_code=303
    )

@app.get("/lead-manager/projects/{project_id}/tasks/create")
@role_required("LEAD")
async def create_task_page(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db)
):
    lead_id = request.session.get("user_id")

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.project_owner == lead_id
    ).first()

    if not project:
        raise HTTPException(status_code=404)

    developers = db.query(User).filter(
        User.role == UserRole.DEVELOPER
    ).all()

    return templates.TemplateResponse(
        "create_task.html",
        {
            "request": request,
            "project": project,
            "developers": developers
        }
    )


@app.post("/lead-manager/projects/{project_id}/tasks/create")
@role_required("LEAD")
async def create_task(
    request: Request,
    project_id: int,
    task: str = Form(...),
    requirement_id: int = Form(...),
    developer_id: int = Form(...),
    start_time: str = Form(None),
    end_time: str = Form(None),
    db: Session = Depends(get_db)
):
    lead_id = request.session.get("user_id")

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.project_owner == lead_id
    ).first()

    if not project:
        raise HTTPException(status_code=404)

    new_task = Task(
        task=task,
        project_id=project_id,
        requirement_id=requirement_id,
        created_by=lead_id,
        assigned_to=developer_id,
        status=TaskStatus.NOT_STARTED
    )

    # Optional datetime parsing
    if start_time:
        new_task.start_time = start_time

    if end_time:
        new_task.end_time = end_time

    db.add(new_task)
    db.commit()

    return RedirectResponse(
        f"/lead-manager/projects/{project_id}/tasks/create",
        status_code=303
    )

@app.get("/lead-manager/tasks/{task_id}/edit")
@role_required("LEAD")
async def edit_task_page(
    request: Request,
    task_id: int,
    db: Session = Depends(get_db)
):
    lead_id = request.session.get("user_id")

    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.project_owner == lead_id
    ).first()

    if not task:
        raise HTTPException(status_code=404)

    developers = db.query(User).filter(
        User.role == UserRole.DEVELOPER
    ).all()

    return templates.TemplateResponse(
        "edit_task.html",
        {
            "request": request,
            "task": task,
            "developers": developers
        }
    )

@app.post("/lead-manager/tasks/{task_id}/edit")
@role_required("LEAD")
async def edit_task(
    request: Request,
    task_id: int,
    task_name: str = Form(...),
    developer_id: int = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    lead_id = request.session.get("user_id")

    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.project_owner == lead_id
    ).first()

    if not task:
        raise HTTPException(status_code=404)

    task.task = task_name
    task.assigned_to = developer_id
    task.status = TaskStatus[status]

    db.commit()

    return RedirectResponse(
        f"/lead-manager/projects/{task.project_id}",
        status_code=303
    )


@app.get("/lead-manager/projects/{project_id}")
@role_required("LEAD")
async def lead_project_detail(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db)
):
    lead_id = request.session.get("user_id")

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.project_owner == lead_id
    ).first()

    if not project:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        "lead_project_detail.html",
        {
            "request": request,
            "project": project
        }
    )


@app.post("/lead-manager/tasks/{task_id}/delete")
@role_required("LEAD")
async def delete_task(
    request: Request,
    task_id: int,
    db: Session = Depends(get_db)
):
    lead_id = request.session.get("user_id")

    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.project_owner == lead_id
    ).first()

    if not task:
        raise HTTPException(status_code=404)

    project_id = task.project_id

    db.delete(task)
    db.commit()

    return RedirectResponse(
        f"/lead-manager/projects/{project_id}",
        status_code=303
    )


from datetime import datetime, timedelta

@app.get("/lead-manager/calendar")
@role_required("LEAD")
async def lead_calendar(
    request: Request,
    db: Session = Depends(get_db)
):
    lead_id = request.session.get("user_id")

    tasks = db.query(Task).join(Project).filter(
        Project.project_owner == lead_id,
        Task.start_time != None
    ).all()

    # Group tasks by date
    calendar_data = {}

    for task in tasks:
        date_key = task.start_time.date()

        if date_key not in calendar_data:
            calendar_data[date_key] = []

        calendar_data[date_key].append(task)

    return templates.TemplateResponse(
        "lead_calendar.html",
        {
            "request": request,
            "calendar_data": calendar_data
        }
    )


@app.get("/lead-manager/projects")
@role_required("LEAD")
async def lead_projects(
    request: Request,
    db: Session = Depends(get_db)
):
    lead_id = request.session.get("user_id")

    projects = db.query(Project).filter(
        Project.project_owner == lead_id
    ).all()

    return templates.TemplateResponse(
        "lead_projects.html",
        {
            "request": request,
            "projects": projects
        }
    )




@app.get("/lead-manager/tasks")
# @role_required("LEAD")
async def lead_all_tasks(
    request: Request,
    db: Session = Depends(get_db),
    project_id: Optional[int] = Query(None),
    page: int = Query(1)
):
    lead_id = request.session.get("user_id")

    page_size = 5
    offset = (page - 1) * page_size

    # Get lead projects for dropdown
    projects = db.query(Project).filter(
        Project.project_owner == lead_id
    ).all()

    # Base query
    query = db.query(Task).join(Project).filter(
        Project.project_owner == lead_id
    )

    # Filter by project
    if project_id:
        query = query.filter(Task.project_id == project_id)

    total_tasks = query.count()

    tasks = query.order_by(Task.created_at.desc()) \
                 .offset(offset) \
                 .limit(page_size) \
                 .all()

    total_pages = ceil(total_tasks / page_size) if total_tasks else 1

    return templates.TemplateResponse(
        "lead_all_tasks.html",
        {
            "request": request,
            "tasks": tasks,
            "projects": projects,
            "selected_project": project_id,
            "page": page,
            "total_pages": total_pages
        }
    )
