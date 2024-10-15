from fastapi import APIRouter




router = APIRouter(prefix="/unrecognized_faces", tags=["Unrecognized Faces"])


@router.get("/")
def ping():
    return {"message": "pong"}
