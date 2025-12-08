from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import engine, Base
from sqlalchemy import text
from routes import users
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connected to database")
    except Exception as e:
        print("Failed to connect to database", e)
    yield
    engine.dispose()
    print("Disconnected from database")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Welcome to StreakChain API - track your daily habit streaks with ease."}

app.include_router(users.router)