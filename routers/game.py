from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from database.models import Game, get_db, GameOut

game_router = APIRouter(prefix="/games", tags=["Игры"])

# Добавление игры
@game_router.post("/", response_model=GameOut)
async def create_game(name: str = Body(...), price: float = Body(...), category_id: int = Body(...), db: Session = Depends(get_db)):
    db_game = Game(name=name, price=price, category_id=category_id)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

# Список игр
@game_router.get("/", response_model=List[GameOut])
async def list_games(db: Session = Depends(get_db)):
    return db.query(Game).all()

# Обновление игры
@game_router.put("/{game_id}", response_model=GameOut)
async def update_game(game_id: int, name: str = Body(...), price: float = Body(...), category_id: int = Body(...), db: Session = Depends(get_db)):
    db_game = db.query(Game).filter(Game.id == game_id).first()
    if not db_game:
        raise HTTPException(status_code=404, detail=f"игра с id {game_id} не найдена")

    db_game.name = name
    db_game.price = price
    db_game.category_id = category_id

    db.commit()
    return db_game

# Удаление игры по идентификатору
@game_router.delete("/{game_id}", response_model=dict)
async def delete_game(game_id: int, db: Session = Depends(get_db)):
    db_game = db.query(Game).filter(Game.id == game_id).first()
    if not db_game:
        raise HTTPException(status_code=404, detail=f"игра с id {game_id} не найдена")

    db.delete(db_game)
    db.commit()
    return {"message": f"игра с id {game_id} была удалена"}
