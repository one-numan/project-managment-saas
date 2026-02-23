# 🚀 Project Management SaaS – MVP

## 📌 Overview

This project is a **Project Management SaaS Application** built using:

* **FastAPI** (Backend Framework)
* **Jinja2 Templates** (Server-Side Rendering)
* **PostgreSQL** (Database)
* **SQLAlchemy ORM (2.0 style)**

The primary goal of this project is:

> ✅ To build a **Simple MVP (Minimum Viable Product)**
> 
> ✅ To understand real-world **Project Management workflow**
> 
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

## Login

<img width="2784" height="1774" alt="image" src="https://github.com/user-attachments/assets/0ad1dff4-8426-4dc8-8dca-c4f9b36d6e21" />



## 🧑‍💼 Project Manager

* Create Project
* Add Client Ask
* Assign Lead

<img width="1392" height="887" alt="Screenshot 2026-02-23 at 3 43 35 PM" src="https://github.com/user-attachments/assets/f601fb50-2f27-47a8-9346-6cf3615ae485" />

---

## 🧑‍💻 Lead

* Add Client Requirements
* Break requirements into Tasks
* Assign Tasks to Developers

We have two leads, each with separate views and isolated data in our multi-tenant system:

1. Mr. Jeevan
2. Mrs. Sonika

### 1. Dashboad Page
<img width="1392" height="887" alt="Screenshot 2026-02-23 at 3 47 22 PM" src="https://github.com/user-attachments/assets/133e28cb-9f8b-443f-a9b7-90ebb6bd5a34" />

<img width="1392" height="887" alt="Screenshot 2026-02-23 at 3 49 03 PM" src="https://github.com/user-attachments/assets/4ab3e3c1-1c94-4327-8fed-0792e3151f4f" />


### 2. Projects 
<img width="1276" height="299" alt="image" src="https://github.com/user-attachments/assets/55b092c6-20d8-415e-8ad6-749c35c083ef" />


### 3. Task List
<img width="2552" height="972" alt="image" src="https://github.com/user-attachments/assets/2a8fdcd2-2485-458f-a727-ea37abff6428" />


### 4. Calender
<img width="2784" height="1774" alt="image" src="https://github.com/user-attachments/assets/23829fdb-4b46-4a29-a889-73cae4280098" />

---

## 👨‍💻 Developer

<img width="1392" height="887" alt="Screenshot 2026-02-23 at 3 48 44 PM" src="https://github.com/user-attachments/assets/8dc87e78-d857-4f18-bd3c-9436de65c551" />


* View assigned tasks
* Update task status
* Add remarks/comments


---

# 🏗 Architecture Design

## 1️⃣ MVP First Approach

This project intentionally avoids overengineering.

✔ Simple role system<br>
✔ Minimal tables<br>
✔ Clean relationships<br>
✔ Server-side rendering (Jinja)<br>
✔ No heavy frontend frameworks<br>

Goal: **Understand core  Multi-Tenent logic before scaling**

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
