# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ==============================
# DATABASE CONFIGURATION
# ==============================


DB_USER = "project_user"
DB_PASSWORD = "project_pass"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "project_management"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)  # echo prints SQL statements
print("Engine",engine)



# ==============================
# SESSION CONFIGURATION
# ==============================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)

# ==============================
# BASE CLASS FOR MODELS
# ==============================

Base = declarative_base()

# ==============================
# DEPENDENCY (For FastAPI)
# ==============================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()