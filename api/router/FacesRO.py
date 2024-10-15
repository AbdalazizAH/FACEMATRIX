from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
#
from api.models.FacesMO import Face  
from api.db.Connect import get_db
from api.Schema.FacesSC import FaceSchema

#
router = APIRouter(prefix="/fases" , tags=["Fases-EndPoint"])



# جلب جميع الوجوه
@router.get("/faces/", response_model=List[FaceSchema])
def get_all_faces(db: Session = Depends(get_db)):
    faces = db.query(Face).all()
    return faces


# جلب وجه بناءً على id
@router.get("/faces/{id}", response_model=FaceSchema)
def get_face_by_id(id: int, db: Session = Depends(get_db)):
    face = db.query(Face).filter(Face.id == id).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")
    return face


# جلب وجه بناءً على ref_no
@router.get("/faces/by_ref_no/{ref_no}", response_model=FaceSchema)
def get_face_by_ref_no(ref_no: str, db: Session = Depends(get_db)):
    face = db.query(Face).filter(Face.ref_no == ref_no).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")
    return face


# جلب وجه بناءً على name
@router.get("/faces/by_name/{name}", response_model=List[FaceSchema])
def get_face_by_name(name: str, db: Session = Depends(get_db)):
    faces = db.query(Face).filter(Face.name == name).all()
    if not faces:
        raise HTTPException(status_code=404, detail="Face not found")
    return faces

