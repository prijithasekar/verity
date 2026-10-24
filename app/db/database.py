import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# In serverless environments like Vercel (Linux / Lambda), root directory is read-only.
# Using tempfile.gettempdir() ensures cross-platform portability (/tmp on Linux, %TEMP% on Windows).
if os.getenv("VERCEL"):
    temp_dir = tempfile.gettempdir()
    db_path = os.path.join(temp_dir, "verity.db").replace("\\", "/")
    DATABASE_URL = f"sqlite:///{db_path}"
else:
    DATABASE_URL = "sqlite:///./verity.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
