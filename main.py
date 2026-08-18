"""FastAPI app instance and routes"""

"""Client request → FastAPI parses it against Pydantic model → 
validation passes → validated data goes into the route function → 
you build an ORM model object from it → SQLAlchemy session sends it to Postgres."""
from sqlalchemy.exc import IntegrityError
from models import SleepReadingDB, PatientDB # must be imported so Base knows about it
from database import SessionLocal
from fastapi import Depends, HTTPException
from schemas import SleepReading, SleepReadingPatch, SleepReadingResponse, Patient, PatientResponse, PatientPatch
from sqlalchemy.orm import Session
from fastapi import FastAPI
app = FastAPI()
# Generator dependency: creates a new DB session per request, yields it
# to the endpoint (via Depends), then closes it automatically once the
# endpoint finishes — even if an error occurred.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""Reading endpoints"""

@app.get("/readings/{reading_id}", response_model=SleepReadingResponse)
def get_reading(reading_id: int, db: Session = Depends(get_db)):
    reading = db.query(SleepReadingDB).filter(SleepReadingDB.id == reading_id).first()
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    return reading


@app.post("/readings", response_model=SleepReadingResponse)
def create_reading(sleep_reading: SleepReading ,db: Session = Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == sleep_reading.patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    new_reading = SleepReadingDB(**sleep_reading.model_dump())
    try:
        db.add(new_reading)
        db.commit()
        db.refresh(new_reading)
        return new_reading
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A reading for this patient on this date already exists."
        )


@app.delete("/readings/{reading_id}")
def delete_reading(reading_id: int, db:Session = Depends(get_db)):
    reading = db.query(SleepReadingDB).filter(SleepReadingDB.id == reading_id).first()
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    db.delete(reading)
    db.commit()
    return {"detail": "reading deleted"}

@app.put("/readings/{reading_id}", response_model=SleepReadingResponse)
def update_reading(reading_id: int, sleep_reading: SleepReading ,db: Session = Depends(get_db)):
    existing = db.query(SleepReadingDB).filter(SleepReadingDB.id == reading_id).first()
    if existing is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    # compares the patient's id from the request with the patient's id from the patient table
    # if the id from the request is not in the patient table, we cannot update because of the relationship
    # between sleep_reading table and the patient table
    patient = db.query(PatientDB).filter(PatientDB.id == sleep_reading.patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    # update the existing object's attributes from the validated input
    for key, value in sleep_reading.model_dump().items():
        # Sets/overwrites the given attribute (key) on the object with the new value —
        # same as writing existing.<key> = value, but with the attribute name as a variable.
        setattr(existing, key, value)

    try:
        db.commit()
        db.refresh(existing)
        return existing

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A reading for this patient on this date already exists."
        )



@app.patch("/readings/{reading_id}", response_model=SleepReadingResponse)
def patch_reading(reading_id: int, sleep_reading: SleepReadingPatch, db: Session = Depends(get_db)):
    existing = db.query(SleepReadingDB).filter(SleepReadingDB.id == reading_id).first()
    if existing is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    if sleep_reading.patient_id is not None:
        patient = db.query(PatientDB).filter(PatientDB.id == sleep_reading.patient_id).first()
        if patient is None:
            raise HTTPException(status_code=404, detail="Patient not found")
    # Only update fields the client actually sent; leave all other existing
    # values unchanged. model_dump(exclude_unset=True)
    for key, value in sleep_reading.model_dump(exclude_unset=True).items():
        # Convert the Pydantic model to a dict and update each field on the existing DB object.
        setattr(existing, key, value)

    try:
        db.commit()
        db.refresh(existing)
        return existing
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A reading for this patient on this date already exists."
        )
"""Patients endpoints"""


@app.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.post("/patients", response_model=PatientResponse)
def create_patient(patient: Patient, db: Session = Depends(get_db)):
    new_patient = PatientDB(**patient.model_dump())
    try:
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return new_patient
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A patient with this name and age already exists."
        )


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()
    return {"detail": "patient deleted"}


@app.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient: Patient, db: Session = Depends(get_db)):
    existing = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if existing is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    for key, value in patient.model_dump().items():
        setattr(existing, key, value)

    try:
        db.commit()
        db.refresh(existing)
        return existing
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A patient with this name and age already exists."
        )


@app.patch("/patients/{patient_id}", response_model=PatientResponse)
def patch_patient(patient_id: int, patient: PatientPatch,  db: Session = Depends(get_db)):
    existing = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if existing is None:
       raise HTTPException(status_code=404, detail="Patient not found")

    for key, value in patient.model_dump(exclude_unset=True).items():
        # Convert the Pydantic model to a dict and update each field on the existing DB object.
        setattr(existing, key, value)

    try:
        db.commit()
        db.refresh(existing)
        return existing
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A patient with this name and age already exists."
        )
















"""Base.metadata is a registry that tracked every model class
    you defined with class X(Base): — in this case, SleepReadingDB. 
    Calling .create_all(bind=engine) tells SQLAlchemy:
    "generate CREATE TABLE for every model I know about, 
    and run it against this engine's database — but only for tables that
     don't already exist."""
#Base.metadata.create_all(bind=engine)


"""
db = SessionLocal()
all_readings = db.query(SleepReadingDB).all()
print(all_readings)
------------------
db = SessionLocal()
new_reading = SleepReadingDB(
    patient_id=5,
    sleep_duration_hours=7.5,
    heart_rate=62.0,
    is_deep_sleep=True,
    raw_device_data={"device": "OuraRing", "battery": 84}
)

db.add(new_reading)
db.commit()
db.refresh(new_reading)
print(new_reading.id)  # auto-generated by Postgres, now available

# Get all readings
all_readings = db.query(SleepReadingDB).all()
print(all_readings)

# Get one by id
one_reading = db.query(SleepReadingDB).filter(SleepReadingDB.id == 1).first()
print(one_reading)

# Get with a condition
long_sleep = db.query(SleepReadingDB).filter(SleepReadingDB.sleep_duration_hours > 7).all()
print(long_sleep)

# for updating first need to be read then update
reading = db.query(SleepReadingDB).filter(SleepReadingDB.id == 1).first()
reading.heart_rate = 58.0
db.commit()

reading = db.query(SleepReadingDB).filter(SleepReadingDB.id == 2).first()
db.delete(reading)
db.commit()"""