
#######################################################################

# using this file to create database and table for this project functionlity manyly for dev

#######################################################################

from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, Enum, LargeBinary, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()

class Admin(Base):
    __tablename__ = 'admins'

    login_name = Column(String(20), primary_key=True, comment='اسم الدخول')
    full_name = Column(String(40), nullable=False, comment='الاسم بالكامل')
    phone_no = Column(String(10), nullable=False, comment='رقم الهاتف')
    email = Column(String(50), nullable=False, comment='البريد الإلكتروني')
    password = Column(String(64), nullable=False, comment='كلمة السر Sha256')

class Face(Base):
    __tablename__ = 'faces'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='رقم تسلسلي')
    ref_no = Column(String(20), unique=True, nullable=False, comment='الرقم التعريفي للشخصية كالرقم الوظيفي مثلا')
    name = Column(String(50), nullable=False, index=True, comment='اسم الشخصية')
    data = Column(LargeBinary, nullable=False, comment='البصمة الرقمية للوجه')

    recognized_faces = relationship("RecognizedFace", back_populates="face")

class RecognizedFace(Base):
    __tablename__ = 'recognized_faces'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='رقم تسلسلي')
    date_time = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, comment='بصمة التاريخ والوقت')
    face_id = Column(Integer, ForeignKey('faces.id'), nullable=False, comment='رابط سجل الوجه')
    snapshot = Column(LargeBinary, nullable=False, comment='لقطة عند التعرف')
    category = Column(Enum('ENTERING', 'LEAVING', name='category_enum'), nullable=False, comment='تصنيف : دخول والانصراف')

    face = relationship("Face", back_populates="recognized_faces")

class UnrecognizedFace(Base):
    __tablename__ = 'unrecognized_faces'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='رقم تسلسلي')
    date_time = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, comment='بصمة التاريخ والوقت')
    category = Column(Enum('ENTERING', 'LEAVING', name='category_enum'), nullable=False, comment='التصنيف: دخول ام خروج')
    snapshot = Column(LargeBinary, nullable=False, comment='لقطة عند التعرف')

def create_database_if_not_exists():
    # تعريف عنوان URL لقاعدة البيانات
    db_url = 'mysql+mysqlconnector://root:@localhost:3306/face_recognition_db'
    
    # إنشاء محرك قاعدة البيانات
    engine = create_engine(db_url)
    
    # التحقق من وجود قاعدة البيانات
    if not database_exists(engine.url):
        # إنشاء قاعدة البيانات إذا لم تكن موجودة
        create_database(engine.url)
        print("database is creation ")
    else:
        print("database already exists")
    
    # إنشاء الجداول
    Base.metadata.create_all(engine)
    print("table is creating")

    return engine

if __name__ == "__main__":
    engine = create_database_if_not_exists()