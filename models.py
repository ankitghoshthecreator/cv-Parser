from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Enum, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
from datetime import datetime

Base = declarative_base()

class UserRole(enum.Enum):
    STUDENT = "student"
    EMPLOYER = "employer"
    MANAGEMENT = "management"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # For students
    cv_text = Column(Text, nullable=True)
    skills = Column(Text, nullable=True) # Comma-separated or JSON string

class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False)
    code = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(Text, nullable=False) # Comma-separated or JSON string
    employer_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    employer = relationship("User")

# Database Setup
DATABASE_URL = "sqlite:///./platform.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
