# 🚀 Project Management SaaS – MVP

## 📌 Overview

This project is a **Project Management SaaS Application** built using:

* **FastAPI** (Backend Framework)
* **Jinja2 Templates** (Server-Side Rendering)
* **PostgreSQL** (Database)
* **SQLAlchemy ORM (2.0 style)**

The primary goal of this project is:

> ✅ To build a **Simple MVP (Minimum Viable Product)**
> ✅ To understand real-world **Project Management workflow**
> ✅ To design with future-ready **Multi-Tenant Architecture**

---

# 🎯 Project Goal

This system simulates a real software company structure:

```
Client → Project Manager → Lead → Developer
```

The application focuses on:

* Project creation
* Client requirement handling
* Task assignment
* Status tracking
* Role-based workflow

---

# 👥 Roles & Responsibilities

## 🧑‍💼 Project Manager

* Create Project
* Add Client Ask
* Assign Lead

---

## 🧑‍💻 Lead

* Add Client Requirements
* Break requirements into Tasks
* Assign Tasks to Developers

---

## 👨‍💻 Developer

* View assigned tasks
* Update task status
* Add remarks/comments

---

# 🏗 Architecture Design

## 1️⃣ MVP First Approach

This project intentionally avoids overengineering.

✔ Simple role system
✔ Minimal tables
✔ Clean relationships
✔ Server-side rendering (Jinja)
✔ No heavy frontend frameworks

Goal: **Understand core logic before scaling**

---

## 2️⃣ Database Structure (High Level)

Core Entities:

* `User`
* `Project`
* `ClientAsk`
* `Requirement`
* `Task`

Relationship Flow:

```
User (Manager)
   ↓
Project
   ↓
ClientAsk
   ↓
Requirement (Lead)
   ↓
Task (Developer)
```

---

# 🏢 Multi-Tenant Architecture (Future Vision)

Although MVP is single-tenant focused, the design allows future expansion.

### Multi-Tenant Strategy Options

### Option 1 – Shared Database, Tenant ID (Recommended for MVP Scaling)

Add:

```python
tenant_id = Column(Integer, index=True)
```

All queries filtered by `tenant_id`.

✔ Simple
✔ Cost-effective
✔ SaaS-friendly

---

### Option 2 – Schema Per Tenant

Each company gets its own PostgreSQL schema.

✔ More isolation
⚠ More complex

---

### Option 3 – Database Per Tenant

Highest isolation.

✔ Enterprise-grade
⚠ Operationally expensive

---

Current MVP is designed to easily support **Option 1** later.

---

# 🔐 Role-Based Access (Simple MVP Version)

No complex RBAC system.

Simple validation:

```python
if current_user.role != "manager":
    raise HTTPException(status_code=403)
```

Roles:

* `manager`
* `lead`
* `developer`

---

# 📁 Project Structure

```
project/
│
├── main.py
├── database.py
├── models.py
├── requirements.txt
│
├── templates/
│   ├── manager/
│   ├── lead/
│   ├── developer/
│
└── static/
```

---

# ⚙️ Installation

### 1️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run Application

```bash
uvicorn main:app --reload
```

---

# 🧠 Learning Objectives

This project teaches:

* FastAPI routing
* SQLAlchemy ORM relationships
* Clean architecture
* SaaS thinking
* Multi-tenant preparation
* Role-based workflows
* Real-world PM hierarchy

---

# 🚀 Future Improvements

* Authentication (JWT / Session-based)
* Proper RBAC middleware
* Tenant-based filtering
* Activity logs
* Notifications system
* API versioning
* Dashboard analytics
* REST API exposure for frontend apps

---

# 📌 Philosophy

> Build simple.
> Understand deeply.
> Scale wisely.

This project is not about features.
It is about architecture thinking.

---

If you want, next we can:

* 🔥 Improve this README to "Open Source Level"
* 📊 Add ER Diagram section
* 🏢 Add detailed Multi-Tenant Architecture document
* 🧩 Convert this into professional SaaS documentation style

Tell me what level you want now 👌
