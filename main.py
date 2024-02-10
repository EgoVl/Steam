from fastapi import FastAPI
from routers import user, category, game
from database.database import Base, engine

app = FastAPI(docs_url="/")

Base.metadata.create_all(bind=engine)

app.include_router(user.user_router)
app.include_router(game.game_router, prefix="")
app.include_router(category.category_router, prefix="")
