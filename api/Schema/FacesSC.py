
from pydantic import BaseModel, Field
import base64
from pydantic import field_validator

class FaceSchema(BaseModel):
    ref_no: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=50)
    data: str  # Change from bytes to str

    @field_validator('data', mode='before')
    def encode_data(cls, v):
        return base64.b64encode(v).decode('utf-8')

    class Config:
        from_attributes = True  # Updated from orm_mode = True

