from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///./school.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # check_same_thread for SQLite

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    # Import all modules here that define models so that
    # they are registered properly on the metadata. Otherwise
    # you will have to import them first before calling init_db()
    # Base.metadata.create_all(bind=engine) # We will call this explicitly after defining models
    pass
