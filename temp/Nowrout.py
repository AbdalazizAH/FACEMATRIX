from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from db import get_db, Base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, LargeBinary, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship


class GetAllFases(BaseModel):
    ref_no: str
    name: str
    data: bytes

    class Config:
        from_attributes = True


class FaceModel(BaseModel):
    ref_no: str
    name: str
    data: bytes

    class Config:
        from_attributes = True


class Face(BaseModel):
    ref_no: str
    name: str

    class Config:
        from_attributes = True


class RecognizedFace(BaseModel):
    face: Face
    timestamp: datetime
    category: str

    class Config:
        from_attributes = True


class RecognitionsDTO(BaseModel):
    list: List[RecognizedFace]

    class Config:
        from_attributes = True


class AttendanceStats(BaseModel):
    entry_count: int

    class Config:
        from_attributes = True


class AttendanceStat(BaseModel):
    present_days: int
    absent_days: int

    class Config:
        from_attributes = True


class Face(Base):
    __tablename__ = "faces"
    id = Column(Integer, primary_key=True, index=True)
    ref_no = Column(Integer, index=True)
    name = Column(String)
    data = Column(LargeBinary)


# Define the RecognizedFace SQLAlchemy model
class RecognizedFace(Base):
    __tablename__ = "recognized_faces"
    id = Column(Integer, primary_key=True, index=True)
    face_id = Column(Integer, ForeignKey("faces.id"))
    timestamp = Column(DateTime)
    category = Column(String)

    face = relationship("Face")  # Establish relationship with Face model


router = APIRouter(prefix="/knownfaces", tags=["knownfaces"])


@router.get("")
def ping():
    """Ping the FastAPI server."""
    return {"message": "ping FastAPI"}


@router.get("/{ref_no}")
async def find_face(ref_no: str, db: Session = Depends(get_db)):
    """
    Find a face by its reference number.

    Example usage:
    GET /knownfaces/12345
    """
    face = db.query(Face).filter(Face.ref_no == ref_no).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face not found!")
    return face.name


@router.get("/attendance/{ref_no}")
async def find_attendance(ref_no: str, db: Session = Depends(get_db)):
    """
    Find attendance records for a specific face by reference number.

    Example usage:
    GET /knownfaces/attendance/12345
    """
    face = db.query(Face).filter(Face.ref_no == ref_no).first()
    if not face:
        raise HTTPException(status_code=404, detail="RefNo not found!")
    recognitions = (
        db.query(RecognizedFace).filter(RecognizedFace.face_id == face.id).all()
    )
    if not recognitions:
        return Response(status_code=204)
    return RecognitionsDTO(list=recognitions)


@router.get("/attendance/{from_date}/{to_date}")
async def find_attendees(from_date: str, to_date: str, db: Session = Depends(get_db)):
    """
    Find all attendees within a date range.

    Example usage:
    GET /knownfaces/attendance/01-01-2023 00:00:00/31-01-2023 23:59:59
    """
    try:
        start_datetime = datetime.strptime(from_date, "%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strptime(to_date, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    recognitions = (
        db.query(RecognizedFace)
        .filter(RecognizedFace.timestamp.between(start_datetime, end_datetime))
        .all()
    )

    if not recognitions:
        return Response(status_code=204)
    return RecognitionsDTO(list=recognitions)


@router.get("/attendance/entries/{from_date}/{to_date}")
async def find_all_entries_by_date(
    from_date: str, to_date: str, db: Session = Depends(get_db)
):
    """
    Find all entry records within a date range.

    Example usage:
    GET /knownfaces/attendance/entries/01-01-2023 00:00:00/31-01-2023 23:59:59
    """
    try:
        start_datetime = datetime.strptime(from_date, "%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strptime(to_date, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    entries = (
        db.query(RecognizedFace)
        .filter(
            RecognizedFace.timestamp.between(start_datetime, end_datetime),
            RecognizedFace.category == "ENTERING",
        )
        .all()
    )

    if not entries:
        return Response(status_code=204)
    return RecognitionsDTO(list=entries)


@router.get("/attendance/leaves/{from_date}/{to_date}")
async def find_all_leaves_by_date(
    from_date: str, to_date: str, db: Session = Depends(get_db)
):
    """
    Find all leave records within a date range.

    Example usage:
    GET /knownfaces/attendance/leaves/01-01-2023 00:00:00/31-01-2023 23:59:59
    """
    try:
        start_datetime = datetime.strptime(from_date, "%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strptime(to_date, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    leaves = (
        db.query(RecognizedFace)
        .filter(
            RecognizedFace.timestamp.between(start_datetime, end_datetime),
            RecognizedFace.category == "LEAVING",
        )
        .all()
    )

    if not leaves:
        return Response(status_code=204)
    return RecognitionsDTO(list=leaves)


@router.get("/attendance/category/{ref_no}/{from_date}/{to_date}")
async def find_entries_and_leaves_by_face(
    ref_no: str, from_date: str, to_date: str, db: Session = Depends(get_db)
):
    """
    Find both entries and leaves for a specific face within a date range.

    Example usage:
    GET /knownfaces/attendance/category/12345/01-01-2023 00:00:00/31-01-2023 23:59:59
    """
    face = db.query(Face).filter(Face.ref_no == ref_no).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face not found!")

    try:
        start_datetime = datetime.strptime(from_date, "%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strptime(to_date, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    entries_and_leaves = (
        db.query(RecognizedFace)
        .filter(
            RecognizedFace.face == face,
            RecognizedFace.timestamp.between(start_datetime, end_datetime),
        )
        .all()
    )

    if not entries_and_leaves:
        return Response(status_code=204)
    return RecognitionsDTO(list=entries_and_leaves)


@router.get("/attendance/entries/{ref_no}/{from_date}/{to_date}")
async def find_entries_by_face_and_date(
    ref_no: str, from_date: str, to_date: str, db: Session = Depends(get_db)
):
    """
    Find entry records for a specific face within a date range.

    Example usage:
    GET /knownfaces/attendance/entries/12345/01-01-2023 00:00:00/31-01-2023 23:59:59
    """
    face = db.query(Face).filter(Face.ref_no == ref_no).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face not found!")

    try:
        start_datetime = datetime.strptime(from_date, "%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strptime(to_date, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    entries = (
        db.query(RecognizedFace)
        .filter(
            RecognizedFace.face == face,
            RecognizedFace.timestamp.between(start_datetime, end_datetime),
            RecognizedFace.category == "ENTERING",
        )
        .all()
    )

    if not entries:
        return Response(status_code=204)
    return RecognitionsDTO(list=entries)


@router.get("/attendance/leaves/{ref_no}/{from_date}/{to_date}")
async def find_leaves_by_face_and_date(
    ref_no: str, from_date: str, to_date: str, db: Session = Depends(get_db)
):
    """
    Find leave records for a specific face within a date range.

    Example usage:
    GET /knownfaces/attendance/leaves/12345/01-01-2023 00:00:00/31-01-2023 23:59:59
    """
    face = db.query(Face).filter(Face.ref_no == ref_no).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face not found!")

    try:
        start_datetime = datetime.strptime(from_date, "%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strptime(to_date, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    leaves = (
        db.query(RecognizedFace)
        .filter(
            RecognizedFace.face == face,
            RecognizedFace.timestamp.between(start_datetime, end_datetime),
            RecognizedFace.category == "LEAVING",
        )
        .all()
    )

    if not leaves:
        return Response(status_code=204)
    return RecognitionsDTO(list=leaves)


@router.get("/attendance/entries/stats/{from_date}/{to_date}")
async def get_entry_stats(from_date: str, to_date: str, db: Session = Depends(get_db)):
    """
    Get the count of entry records within a date range.

    Example usage:
    GET /knownfaces/attendance/entries/stats/01-01-2023 00:00:00/31-01-2023 23:59:59
    """
    try:
        start_datetime = datetime.strptime(from_date, "%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strptime(to_date, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    entry_count = (
        db.query(RecognizedFace)
        .filter(
            RecognizedFace.timestamp.between(start_datetime, end_datetime),
            RecognizedFace.category == "ENTERING",
        )
        .count()
    )

    return AttendanceStats(entry_count=entry_count)


@router.get("/attendance/stats/{ref_no}/{from_date}/{to_date}")
async def get_attendance_stats(
    ref_no: str, from_date: str, to_date: str, db: Session = Depends(get_db)
):
    """
    Get attendance statistics for a specific face within a date range.

    Example usage:
    GET /knownfaces/attendance/stats/12345/01-01-2023 00:00:00/31-01-2023 23:59:59
    """
    face = db.query(Face).filter(Face.ref_no == ref_no).first()
    if not face:
        raise HTTPException(status_code=404, detail="RefNo not found!")

    try:
        start_datetime = datetime.strptime(from_date, "%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strptime(to_date, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    present_days = (
        db.query(RecognizedFace.timestamp.date())
        .distinct()
        .filter(
            RecognizedFace.face == face,
            RecognizedFace.timestamp.between(start_datetime, end_datetime),
        )
        .count()
    )

    total_days = (end_datetime.date() - start_datetime.date()).days + 1
    absent_days = total_days - present_days

    return AttendanceStat(present_days=present_days, absent_days=absent_days)
