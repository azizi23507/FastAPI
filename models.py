"""SQLAlchemy ORM models (DB tables)"""

from sqlalchemy import Column, Integer, Date, String, Float, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

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
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    sleep_duration_hours = Column(Float, nullable=False)
    heart_rate = Column(Integer, nullable=False)
    is_deep_sleep = Column(Boolean, default=False)
    raw_device_data = Column(JSONB, nullable=True)
    recorded_at = Column(Date, nullable=False)
    sleep_quality_score = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("patient_id", "recorded_at"),
    )

    patient = relationship("PatientDB", back_populates="readings")

class PatientDB(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint("name", "age"),
    )
    readings = relationship("SleepReadingDB", back_populates="patient")

    # Defines what print(obj) shows — readable info instead of a memory address.
    def __repr__(self):
        return f"<PatientDB id={self.id} name={self.name} age={self.age}>"


# back_populates isn't for the database — the ForeignKey alone already
# handles that. It's just Python convenience: it lets patient.readings
# and reading.patient auto-update each other in memory when you set one,
# so you don't have to write a query to get the other side, and don't
# have to manually set both by hand. It also means you can access one
# table's data through an object of the other table — e.g. patient.readings
# gets that patient's sleep readings without writing a separate query.