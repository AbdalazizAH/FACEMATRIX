from sqlalchemy import Column, String, Integer, LargeBinary
from sqlalchemy.orm import relationship
from api.db.Connect import Base
from api.models.RecognizedFaceMO import RecognizedFace  # Add this import


class Face(Base):
    __tablename__ = 'faces'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='رقم تسلسلي')
    ref_no = Column(String(20), unique=True, nullable=False, comment='الرقم التعريفي للشخصية كالرقم الوظيفي مثلا')
    name = Column(String(50), nullable=False, index=True, comment='اسم الشخصية')
    data = Column(LargeBinary, nullable=False, comment='البصمة الرقمية للوجه')
    recognized_faces = relationship("RecognizedFace", back_populates="face") 




