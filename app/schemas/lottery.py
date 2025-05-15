from pydantic import BaseModel, ConfigDict, Field
from datetime import date

class LotteryBase(BaseModel):
    lottery_id: int = Field(..., example="123")
    lottery_date: date = Field(..., example="2025-05-15")
    closed: bool 

    model_config = ConfigDict(from_attributes=True)

class LotteryResponse(BaseModel):
    pass