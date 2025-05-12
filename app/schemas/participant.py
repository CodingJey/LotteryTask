from pydantic import BaseModel
from datetime import date
from uuid import UUID

class ParticipantBase(BaseModel):
    name: str
    last_name: str
    birth_date: date
    
    model_config = ConfigDict(from_attributes=True)