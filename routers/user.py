from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List
from database.models import get_db
from database.models import UserIn, UserOut, User

user_router = APIRouter(prefix="/users", tags=["Управление юзерами"])

#метод регистрации
@user_router.post("/register/")
async def register_user(user: UserIn, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="эмаил уже зареган")

    db_user = User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    return {"message": "Победа! юзер зареган"}

#метод входа
@user_router.post("/login/")
async def login_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if not user:
        raise HTTPException(status_code=401, detail="не правильное имя или пароль")
    return {"message": "успешный вход"}

#получение списка пользователей
@user_router.get("/", response_model=List[UserOut])
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

#получение информации пользователя по его ид
@user_router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="юзер не найден")
    return user

#удаление пользователя по его ид
@user_router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return {"message": f"юзер с ид {user_id} был удален"}
    else:
        raise HTTPException(status_code=404, detail=f"юзер с ид {user_id} не был найден")
