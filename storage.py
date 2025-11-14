import os
from datetime import datetime, time
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Time, Enum as SQLAlchemyEnum
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

if db_url and db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)


engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()



class Task(Base):

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    priority = Column(String(50))
    date_added = Column(DateTime(timezone=True), default=lambda: datetime.now(datetime.timezone.utc))
    end_time = Column(String(10)) 
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default='Active')


if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")