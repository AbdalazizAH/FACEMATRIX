from fastapi import APIRouter


router = APIRouter(prefix="/RecognizedFace", tags=["RecognizedFace"])



@router.get("/")
def ping():
    return {"message": "pong"}
