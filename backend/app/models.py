# backend/app/models.py
"""
FoodFresh AI - Models (Compatibility Module)
"""
try:
    from sqlalchemy import Column, Integer, String
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()

    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True, index=True)
        email = Column(String, unique=True, index=True, nullable=False)
        full_name = Column(String, nullable=True)
        hashed_password = Column(String, nullable=False)
except ImportError:
    Base = object

    class User:
        pass
