# models/admin.py


from sqlalchemy import Column, String, CHAR
from api.db.Connect import Base

class Admin(Base):
    __tablename__ = "admin"

    login_name = Column(String(20), primary_key=True, nullable=False, comment="اسم الدخول")
    full_name = Column(String(40), nullable=False, comment="الاسم بالكامل")
    phone_no = Column(String(10), nullable=False, comment="رقم الهاتف")
    email = Column(String(50), nullable=False, comment="البريد الإلكتروني")
    password = Column(String(64), nullable=False, comment="كلمة السر Sha256")

