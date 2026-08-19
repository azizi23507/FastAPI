"""Pydantic models (request/response validation)"""
from pydantic import BaseModel, ConfigDict
from datetime import date


# SleepReading defines the shared/common fields for the Sleep Reading
# Pydantic schemas. Other schemas (Response, Patch) inherit from
# it to avoid repeating the same fields — it's not tied to the DB directly,
# just the base set of validated fields.
class SleepReading(BaseModel):
    patient_id: int
    sleep_duration_hours: float
    heart_rate: int
    is_deep_sleep: bool
    raw_device_data: dict | None = None
    recorded_at: date
    sleep_quality_score: int | None = None


# SleepReadingPatch mirrors SleepReading's fields but makes every one
# optional, so a PATCH request can send only the field(s) being changed
# without Pydantic requiring the rest.
class SleepReadingPatch(BaseModel):
    patient_id: int | None = None
    sleep_duration_hours: float | None = None
    heart_rate: int | None = None
    is_deep_sleep: bool | None = None
    raw_device_data: dict | None = None
    recorded_at: date | None = None
    sleep_quality_score: int | None = None

# Patient defines the shared/common fields for Patient schemas.
class Patient(BaseModel):
    name: str
    age: int

class PatientPatch(BaseModel):
    name: str | None = None
    age: int | None = None

# SleepReadingResponse is what gets returned to the client — adds the
# DB-generated id on top of SleepReading's fields. from_attributes lets
# Pydantic build this directly from a SleepReadingDB ORM object.

# response_model=SleepReadingResponse — controls what this endpoint is
# allowed to send back, independent of what the DB/ORM object contains.
#
# Without it: FastAPI serializes the raw SQLAlchemy object via an
# undocumented __dict__ fallback — every column gets exposed, in an
# unpredictable order, with no control. Adding a new column to the model
# later would silently leak it into every response, with zero code change.
#
# With it: only the fields declared in SleepReadingResponse are returned,
# in the declared order — a deliberate, stable contract that stays correct
# even if the DB schema changes later.

class SleepReadingResponse(SleepReading):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SleepReadingWithPatient(SleepReading):
    id: int
    patient: PatientResponse | None = None
    model_config = ConfigDict(from_attributes=True)


# PatientResponse adds the DB-generated id for returning to the client.
class PatientResponse(Patient):
    id: int
    model_config = ConfigDict(from_attributes=True)