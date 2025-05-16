from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date



class BallotBase(BaseModel):
    user_id: int = Field(..., description="ID of the Participant who owns this ballot")
    lottery_id: int = Field(..., description="ID of the Lottery this ballot belongs to")
    expiry_date: date = Field(None, example="2025-05-15", description="Date when this ballot expires. This field is optional.")

    model_config = ConfigDict(from_attributes=True)

class BallotCreate(BallotBase):
    user_id: int = Field(..., description="ID of the Participant who owns this ballot")
    lottery_id: int = Field(..., description="ID of the Lottery this ballot belongs to")
    expiry_date: date = Field(None, example="2025-05-15", description="Date when this ballot expires. This field is optional.")
    model_config = ConfigDict(from_attributes=True)

class BallotResponse(BallotBase):
    ballot_id: int = Field(..., description="Primary key of the ballot")
    user_id: int = Field(..., description="ID of the Participant who owns this ballot")
    lottery_id: int = Field(..., description="ID of the Lottery this ballot belongs to")
    ballot_number: int = Field(None, description="Number assigned to the ballot. Can be None.")
    expiry_date: date = Field(None,example="2025-05-15", description="Date when this ballot expires. Can be None.")

    model_config = ConfigDict(from_attributes=True)

