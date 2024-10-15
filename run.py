from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware


# database connection
from api.db.Connect import get_db, engine
# router
from api.router import FacesRO
from api.router import RecognizedFaceRO
from api.router import UnrecognizedFaceRO
from api.router import AdminRO
# schema for validation user input
from api.Schema.AdminSC import AdminLogin

from api.auth.JwtToke import create_access_token
from api.auth.authenticate import authenticate_admin


ACCESS_TOKEN_EXPIRE_MINUTES = 20  #! to config file

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# init router
app.include_router(AdminRO.router)
app.include_router(FacesRO.router)
app.include_router(RecognizedFaceRO.router)
app.include_router(UnrecognizedFaceRO.router)



@app.post("/login")
async def login(login_data: AdminLogin, db=Depends(get_db)):
    admin = authenticate_admin(db, login_data.login_name, login_data.password)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.login_name}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
