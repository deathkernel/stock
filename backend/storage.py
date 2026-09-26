from sqlalchemy import create_engine, String, Float, DateTime, Text, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from datetime import datetime
from backend.config import settings

engine=create_engine(settings.database_url,connect_args={"check_same_thread":False} if settings.database_url.startswith("sqlite") else {})
SessionLocal=sessionmaker(bind=engine)

class Base(DeclarativeBase): pass

class Price(Base):
    __tablename__="prices"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    symbol:Mapped[str]=mapped_column(String(20),index=True)
    timestamp:Mapped[datetime]=mapped_column(DateTime,index=True)
    open:Mapped[float]=mapped_column(Float)
    high:Mapped[float]=mapped_column(Float)
    low:Mapped[float]=mapped_column(Float)
    close:Mapped[float]=mapped_column(Float)
    volume:Mapped[float]=mapped_column(Float)

class Prediction(Base):
    __tablename__="predictions"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    symbol:Mapped[str]=mapped_column(String(20),index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    horizon:Mapped[int]=mapped_column(Integer)
    model:Mapped[str]=mapped_column(String(80))
    point:Mapped[float]=mapped_column(Float)
    lower:Mapped[float]=mapped_column(Float)
    upper:Mapped[float]=mapped_column(Float)
    confidence:Mapped[float]=mapped_column(Float)

class NewsItem(Base):
    __tablename__="news"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    symbol:Mapped[str]=mapped_column(String(20),index=True)
    published_at:Mapped[datetime]=mapped_column(DateTime)
    headline:Mapped[str]=mapped_column(Text)
    url:Mapped[str]=mapped_column(Text)
    sentiment:Mapped[float]=mapped_column(Float)

def check_db() -> bool:
    from sqlalchemy import text
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True


def init_db(): Base.metadata.create_all(engine)
