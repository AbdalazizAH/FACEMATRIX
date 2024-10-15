from api.models.AdminMO import Admin
from passlib.context import CryptContext



pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")




def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password) #hash using sha256


def authenticate_admin(db, login_name: str, password: str):
    admin = db.query(Admin).filter(Admin.login_name == login_name).first()

    if not admin:
        return False
    if not verify_password(password, admin.password):
        return False
    return admin
