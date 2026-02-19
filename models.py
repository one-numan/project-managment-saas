# models.py

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Enum as SqlEnum,
    Time
)
from sqlalchemy.orm import relationship
from database import Base  # <-- Use the shared Base from database.py

# -------------------------
# ENUMS
# -------------------------
class UserRole(Enum):
    PROJECT_MANAGER = "project_manager"
    LEAD = "lead"
    DEVELOPER = "developer"


class TaskStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


# -------------------------
# USERS TABLE
# -------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    role = Column(SqlEnum(UserRole), nullable=False)
    email = Column(String(255), unique=True, nullable=False)  # email column
    password = Column(String(255), nullable=False)            # password column
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_projects = relationship(
        "Project",
        back_populates="creator",
        foreign_keys="Project.created_by"
    )

    owned_projects = relationship(
        "Project",
        back_populates="owner",
        foreign_keys="Project.project_owner"
    )

    created_requirements = relationship(
        "Requirement",
        back_populates="creator"
    )

    created_tasks = relationship(
        "Task",
        back_populates="creator",
        foreign_keys="Task.created_by"
    )

    assigned_tasks = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assigned_to"
    )



# -------------------------
# PROJECTS TABLE
# -------------------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    project_owner = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship(
        "User", back_populates="owned_projects", foreign_keys=[project_owner]
    )
    creator = relationship(
        "User", back_populates="created_projects", foreign_keys=[created_by]
    )
    requirements = relationship(
        "Requirement", back_populates="project", cascade="all, delete"
    )
    tasks = relationship("Task", back_populates="project", cascade="all, delete")


# -------------------------
# REQUIREMENTS TABLE
# -------------------------
class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    requirement = Column(Text, nullable=False)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="requirements")
    creator = relationship("User", back_populates="created_requirements")
    tasks = relationship("Task", back_populates="requirement", cascade="all, delete")


# -------------------------
# TASKS TABLE
# -------------------------
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String(255), nullable=False)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    effort = Column(Time, nullable=True)

    status = Column(SqlEnum(TaskStatus), default=TaskStatus.NOT_STARTED)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    requirement = relationship("Requirement", back_populates="tasks")
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[created_by])
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to])
