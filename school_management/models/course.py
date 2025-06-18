from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))

    teacher = relationship("Teacher") # Basic relationship
