from pydantic import BaseModel, ConfigDict, Field
from datetime import date

class ParticipantBase(BaseModel):
    first_name: str = Field(..., example="Alice")
    last_name: str = Field(..., example="Smith")
    birth_date: date
    
    model_config = ConfigDict(from_attributes=True)

class ParticipantCreate(ParticipantBase):
    pass

class ParticipantResponse(BaseModel):
    user_id : int = Field(..., example=231)
    first_name: str = Field(..., example="Alice")
    last_name: str = Field(..., example="Smith")
    birth_date: date
    
    model_config = ConfigDict(from_attributes=True)