from pydantic import BaseModel, EmailStr, Field


class CreateAdmin(BaseModel):
    login_name: str
    full_name: str
    phone_no: str
    email: EmailStr
    password: str


class AdminInDB(BaseModel):
    login_name: str
    full_name: str
    phone_no: str
    email: EmailStr


class AdminLogin(BaseModel):
    login_name: str
    password: str
