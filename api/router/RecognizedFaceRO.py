from datetime import datetime
from typing import List
from fastapi import APIRouter ,Depends ,HTTPException
from sqlalchemy.orm import sessionmaker, relationship, Session
from api.db.Connect import get_db

from api.models.FacesMO import Face
from api.models.RecognizedFaceMO import RecognizedFace
router = APIRouter(prefix="/RecognizedFace", tags=["RecognizedFace"])


@router.get("/")
def ping():
    return {"message": "pong"}

#####################################################################
                             # on dev #
#####################################################################




from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.db.Connect import get_db
from api.models.FacesMO import Face
from pydantic import BaseModel, Field
import base64

router = APIRouter(prefix="/RecognizedFace", tags=["RecognizedFace"])

class FindFaceSchema(BaseModel):
    id: int = Field(..., description="Id")
    ref_no: str = Field(..., description="RefNo")
    name: str = Field(..., description="Name")
    data: str = Field(..., description="Image data in Base64 format")

@router.get("/findFace/{RefNo}/", response_model=FindFaceSchema)
async def findFace(RefNo: str, db: Session = Depends(get_db)):
    face = db.query(Face).filter(Face.ref_no == RefNo).first()
    if face is None:
        raise HTTPException(status_code=404, detail="Face not found")

    # تحويل البيانات الثنائية إلى Base64
    data_base64 = base64.b64encode(face.data).decode('utf-8')
    
    return FindFaceSchema(
        id=face.id,
        ref_no=face.ref_no,
        name=face.name,
        data=data_base64
    )

class RecognizedFaceSchema(BaseModel):
    date_time: int = Field(..., description="Id")
    category: str = Field(..., description="RefNo")
    name: str = Field(..., description="Name")
    snapshot: str = Field(..., description="Image data in Base64 format")


@router.get("/today", response_model=List[RecognizedFaceSchema])
async def today(db: Session = Depends(get_db)):
    """
    هذه الدالة تقوم بجلب جميع الوجوه المعترف بها لليوم الحالي.
    
    الوظيفة:
    1. تحديد التاريخ الحالي.
    2. استعلام قاعدة البيانات عن جميع الوجوه المعترف بها اليوم في فئة "ENTERING".
    3. تحويل البيانات إلى الصيغة المطلوبة، بما في ذلك تحويل الصور إلى صيغة Base64.
    4. إرجاع قائمة بجميع الوجوه المعترف بها لهذا اليوم.
    """
    today = datetime.now().date()
    # تصفية الوجوه المعترف بها لليوم الحالي
    recognized_faces = db.query(RecognizedFace).filter(
        RecognizedFace.date_time >= datetime.combine(today, datetime.min.time()),
        RecognizedFace.date_time <= datetime.combine(today, datetime.max.time()),
        RecognizedFace.category == "ENTERING"
    ).all()
    
    recognized_face_schemas = []
    for rf in recognized_faces:
        data_base64 = base64.b64encode(rf.snapshot).decode('utf-8')
        recognized_face_schemas.append(
            RecognizedFaceSchema(
                date_time=int(rf.date_time.timestamp()),
                category=rf.category,
                name=rf.face.name,  # استخراج الاسم باستخدام العلاقة
                snapshot=data_base64 
            )
        )
    
    return recognized_face_schemas
