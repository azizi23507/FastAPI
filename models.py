"""SQLAlchemy ORM models (DB tables)"""

from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


# SleepReadingDB is a Python class that models the sleep_readings table
# in the PostgreSQL database.
# SleepReadingDB class inheriting from Base, registers it with SQLAlchemy as an ORM model, and
# linking this class(SleepReadingDB) to that table from psql(sleep_readings).
class SleepReadingDB(Base):
    __tablename__ = "sleep_readings"  # which database table this class represents.

    def __repr__(self):
        return (f"<SleepReadingDB id={self.id} patient_id={self.patient_id}"
                f" hours={self.sleep_duration_hours} raw_device_data={self.raw_device_data}>")

    # maps python/SQLAlchemy attributes to database columns
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    sleep_duration_hours = Column(Float, nullable=False)
    heart_rate = Column(Integer, nullable=False)
    is_deep_sleep = Column(Boolean, default=False)
    raw_device_data = Column(JSONB, nullable=True)

