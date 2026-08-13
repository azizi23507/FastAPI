"""Pydantic models (request/response validation)"""
from pydantic import BaseModel
# SleepReadingBase defines the shared/common fields for the Sleep Reading
# Pydantic schemas. Other schemas (Create, Update, Response) inherit from
# it to avoid repeating the same fields — it's not tied to the DB directly,
# just the base set of validated fields.
class SleepReadingBase(BaseModel):
    patient_id: int
    sleep_duration_hours: float
    heart_rate: float
    is_deep_sleep: bool