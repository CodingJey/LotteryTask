from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date

# Shared properties
class BallotBase(BaseModel):
    UserID: int = Field(..., description="ID of the Participant who owns this ballot")
    LotteryID: int = Field(..., description="ID of the Lottery this ballot belongs to")
    ExpiryDate: date = Field(None, description="Date when this ballot expires")

# Properties to receive on creation
class BallotCreate(BallotBase):
    pass

class BallotResponse(BaseModel):
    UserID: int = Field(..., description="ID of the Participant who owns this ballot")
    LotteryID: int = Field(..., description="ID of the Lottery this ballot belongs to")
    ExpiryDate: date = Field(None, description="Date when this ballot expires")
    model_config = ConfigDict(from_attributes=True)


class BallotRead(BallotBase):
    BallotID: int = Field(..., description="Primary key of the ballot")

    model_config = ConfigDict(from_attributes=True)

