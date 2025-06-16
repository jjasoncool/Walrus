from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import Config
import datetime

Base = declarative_base()

class MarineData(Base):
    __tablename__ = "marine_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_time = Column(String, nullable=False)
    station = Column(String, nullable=False)
    tide_height = Column(Float)
    wave_height = Column(Float)
    wave_direction = Column(String)
    wave_period = Column(Float)
    wind_speed_ms = Column(Float)
    wind_speed_level = Column(Integer)
    wind_direction = Column(String)
    max_wind_speed_ms = Column(Float)
    max_wind_speed_level = Column(Integer)
    sea_temperature = Column(Float)
    air_temperature = Column(Float)
    air_pressure = Column(Float)
    sea_current_direction = Column(String)
    sea_current_speed_ms = Column(Float)
    sea_current_speed_knots = Column(Float)
    recorded_at = Column(DateTime, default=datetime.datetime.now)

    __table_args__ = (
        UniqueConstraint("date_time", "station", name="uq_date_station"),
        Index("idx_date_time", "date_time"),
        Index("idx_station", "station"),
    )

def init_db():
    engine = create_engine(Config.DATABASE_URL)
    Base.metadata.create_all(engine, checkfirst=True)
    return sessionmaker(bind=engine)()
