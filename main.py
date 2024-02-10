from fastapi import Form, HTTPException, Depends, APIRouter
from sqlalchemy import Float
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

app = FastAPI(docs_url="/")

SQLALCHEMY_DATABASE_URL = "sqlite:///./St.db"
engin = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engin)

Base = declarative_base()

#Класс категорий
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    games = relationship("Game", back_populates="category")

#Класс игр
class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="games")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engin)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



#Определение моделей данных для запросов
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


user_router = APIRouter(prefix="",tags=["Управление пользователями"])
#все методы
#Регистрация
@user_router.post("/register/")
async def register_user(user: UserIn, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Эмаил уже зарегистрирован")

    #Создаю нового пользователя
    db_user = User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    return {"message": "Юзер успешно зарегистрировался"}

#Метод входа
@user_router.post("/login/")
async def login_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Не верный логин или пароль")
    return {"message": "Успешный вход"}

#Получение списка пользователей
@user_router.get("/users/", response_model=List[UserOut])
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

#инфа по пользователю через ид
@user_router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

#метод удаления пользователя по ид
@user_router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return {"message": f"Юзер с ид {user_id} был удален"}
    else:
        raise HTTPException(status_code=404, detail=f"Юзер с ид {user_id} не найден")




game_router = APIRouter(prefix="",tags=["Управление играми"])
#Метод добавелния игры
@game_router.post("/games/", response_model=GameOut)
async def create_game(game: GameIn, db: Session = Depends(get_db)):
    db_game = Game(name=game.name, price=game.price, category_id=game.category_id)
    db.add(db_game)
    db.commit()
    return db_game

#Метод просмотра спикска игр
@game_router.get("/games/", response_model=List[GameOut])
async def list_games(db: Session = Depends(get_db)):
    return db.query(Game).all()

@game_router.put("/games/{game_id}", response_model=GameOut)
async def update_game(game_id: int, game_update: GameUpdate, db: Session = Depends(get_db)):
    db_game = db.query(Game).filter(Game.id == game_id).first()
    if not db_game:
        raise HTTPException(status_code=404, detail=f"Game with id {game_id} not found")

    if game_update.name:
        db_game.name = game_update.name
    if game_update.price:
        db_game.price = game_update.price

    db.commit()
    return db_game

#Улаление игры по названию
@game_router.delete("/games/{name}/")
async def delete_game(name: str, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.name == name).first()
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена")
    db.delete(game)
    db.commit()
    return {"message": f"Игра {name} удалена"}

@game_router.delete("/game/{game_id}")
async def delete_game(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if game:
        db.delete(game)
        db.commit()
        return {"message": f"Игра с ид {game_id} был удален"}
    else:
        raise HTTPException(status_code=404, detail=f"Игра с ид {game_id} не найдена")




category_router = APIRouter(prefix="/categories", tags=["Управление категориями"])
#создание категории
@category_router.post("/", response_model=CategoryOut)
async def create_category(category: CategoryIn, db: Session = Depends(get_db)):
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

#обновление категории по ид
@category_router.put("/{category_id}", response_model=CategoryOut)
async def update_category(category_id: int, category: CategoryIn, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    db_category.name = category.name
    db.commit()
    return db_category

#получение списка игр по категории
@category_router.get("/{category_id}/games", response_model=List[GameOut])
async def get_games_by_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category.games

#удаление категории по ид
@category_router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    db.delete(db_category)
    db.commit()
    return {"message": f"Категория с ид {category_id} удалена"}

app.include_router(user_router)
app.include_router(game_router)
app.include_router(category_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
