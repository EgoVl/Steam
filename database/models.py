from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
from database.database import SessionLocal
from pydantic import BaseModel
from typing import Optional
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    games = relationship("Game", back_populates="category", cascade="all, delete-orphan")

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="games")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



#Определение моделей данных для запросов
class GameWithCategoryOut(BaseModel):
    name:str
    id:int
    category:int
    price:float

class CategoryIn(BaseModel):
    name: str

class CategoryOut(BaseModel):
    id: int
    name: str

class UserIn(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    username: str
    email: str


class GameIn(BaseModel):
    name: str
    price: float
    category_id: int

class GameUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None


class GameOut(BaseModel):
    name: str
    price: float
