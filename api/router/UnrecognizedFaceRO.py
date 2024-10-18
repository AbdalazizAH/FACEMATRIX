from fastapi import APIRouter




router = APIRouter(prefix="/unrecognized_faces", tags=["Unrecognized Faces"])

#####################################################################
                             # on dev #
#####################################################################


@router.get("/")
def ping():
    return {"message": "pong"}
