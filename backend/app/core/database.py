import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker




load_dotenv()


DATABASE_URL = URL.create(
    "postgresql+psycopg",
    username=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.getenv("POSTGRES_DB", "ai_food_nutrition"),
)


engine = create_engine(
    DATABASE_URL,
    echo=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# from app.models.analysis import Analysis
# from app.models.food import Food
# from app.models.nutrition import Nutrition
# from app.models.analysis import Analysis
# from app.models.food import Food
# from app.models.nutrition import Nutrition
# from app.models.user_profile import UserProfile