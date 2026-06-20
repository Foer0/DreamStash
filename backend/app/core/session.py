from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings


engine = create_engine(f'{settings.driver}://{settings.user}:{settings.password}@'
                       f'{settings.host}/{settings.db_name}', echo=True)


SessionLocal = sessionmaker(bind=engine)
