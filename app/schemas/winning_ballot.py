from pydantic import BaseModel, ConfigDict, Field
from datetime import date

class WinningBallotBase(BaseModel):
    lottery_id: int = Field(..., example="123")
    ballot_id: int = Field(..., example="123")
    winning_date: date = Field(..., example="2025-05-15")
    winning_amount: int = Field(..., example="123")

    model_config = ConfigDict(from_attributes=True)

class WinningBallotResponse(WinningBallotBase):
    lottery_id: int = Field(..., example="123")
    ballot_id: int = Field(..., example="123")
    winning_date: date = Field(..., example="2025-05-15")
    winning_amount: int = Field(..., example="123")

    model_config = ConfigDict(from_attributes=True)
