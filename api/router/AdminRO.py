from fastapi import APIRouter, Depends, HTTPException
from api.Schema.AdminSC import CreateAdmin, AdminInDB  # Ensure correct import
from api.auth.authenticate import get_password_hash
from api.models.AdminMO import Admin
from sqlalchemy.orm import Session
from api.db.Connect import get_db

router = APIRouter(prefix="/admin", tags=["Admin-Endpoints"])


@router.post("/create", response_model=AdminInDB)  # Use Pydantic model for response
async def create_admin(admin: CreateAdmin, db: Session = Depends(get_db)):
    try:
        # Check if admin already exists
        admin_datas = db.query(Admin).filter(Admin.login_name == admin.login_name).first()
        if admin_datas:
            raise HTTPException(status_code=404, detail="Admin already exists")

        # Create admin_data with all required fields
        hashed_password = get_password_hash(admin.password)
        admin_data = Admin(
            full_name=admin.full_name,
            phone_no=admin.phone_no,
            email=admin.email,
            password=hashed_password,
            login_name=admin.login_name,  # Include login_name
        )
        db.add(admin_data)
        db.commit()
        db.refresh(admin_data)
        return AdminInDB(
            full_name=admin.full_name,
            phone_no=admin.phone_no,
            email=admin.email,
            login_name=admin.login_name,
        )
    except HTTPException as http_exc:
        raise http_exc  # Re-raise the HTTPException without modification
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")  # Ensure a valid response is returned
