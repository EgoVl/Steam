from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from database.models import get_db
from database.models import Category

category_router = APIRouter(prefix="/categories", tags=["Categories"])

@category_router.post("/")
async def create_category(name: str = Form, db: Session = Depends(get_db)):
    db_category = Category(name=name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

#получение списка категорий
@category_router.get("/")
async def get_all_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

#данные категории ид
@category_router.get("/{category_id}")
async def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="категория не найдена")
    return category

#обновление категории по ид
@category_router.put("/{category_id}")
async def update_category(category_id: int, name: str, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="категория не найдена")
    category.name = name
    db.commit()
    return category

#удаление категории
@category_router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="категория не удалена")
    db.delete(category)
    db.commit()
    return {"message": "категория удалена"}
