from sqlalchemy import Column, Integer, TIMESTAMP, Enum, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


from api.db.Connect import Base


class UnrecognizedFace(Base):
    __tablename__ = 'unrecognized_faces'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='رقم تسلسلي')
    date_time = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, comment='بصمة التاريخ والوقت')
    category = Column(Enum('ENTERING', 'LEAVING', name='category_enum'), nullable=False, comment='التصنيف: دخول ام خروج')
    snapshot = Column(LargeBinary, nullable=False, comment='لقطة عند التعرف')
