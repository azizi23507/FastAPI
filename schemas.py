"""Pydantic models (request/response validation)"""
from pydantic import BaseModel
# SleepReadingBase defines the shared/common fields for the Sleep Reading
# Pydantic schemas. Other schemas (Create, Update, Response) inherit from
# it to avoid repeating the same fields — it's not tied to the DB directly,
# just the base set of validated fields.
class SleepReading(BaseModel):
    patient_id: int
    sleep_duration_hours: float
    heart_rate: int
    is_deep_sleep: bool
    raw_device_data: dict | None = None


# SleepReadingPatch mirrors SleepReading's fields but makes every one
# optional, so a PATCH request can send only the field(s) being changed
# without Pydantic requiring the rest.
class SleepReadingPatch(BaseModel):
    patient_id: int | None = None
    sleep_duration_hours: float | None = None
    heart_rate: int | None = None
    is_deep_sleep: bool | None = None
    raw_device_data: dict | None = None
