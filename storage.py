from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Time, Enum
from datetime import datetime
import enum
import os
from dotenv import load_dotenv

load_dotenv() # This loads the variables from your .env file

Base = declarative_base()

class TaskStatus(enum.Enum):
    expired = "expired"
    completed = "completed"

class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    priority = Column(String(50))
    date_added = Column(DateTime, default=datetime.utcnow)
    end_time = Column(Time)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.expired)

db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)

engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)