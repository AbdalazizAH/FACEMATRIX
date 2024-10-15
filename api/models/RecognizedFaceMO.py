from sqlalchemy import Column, Integer, TIMESTAMP, Enum, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from api.db.Connect import Base


class RecognizedFace(Base):
    __tablename__ = 'recognized_faces'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='رقم تسلسلي')
    date_time = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, comment='بصمة التاريخ والوقت')
    face_id = Column(Integer, ForeignKey('faces.id'), nullable=False, comment='رابط سجل الوجه')
    snapshot = Column(LargeBinary, nullable=False, comment='لقطة عند التعرف')
    category = Column(Enum('ENTERING', 'LEAVING', name='category_enum'), nullable=False, comment='تصنيف : دخول والانصراف')

    face = relationship("Face", back_populates="recognized_faces")



