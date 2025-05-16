from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from typing import Optional 

class LotteryBase(BaseModel):
    lottery_id: int = Field(..., example="123")
    lottery_date: date = Field(..., example="2025-05-15")

    model_config = ConfigDict(from_attributes=True)

class LotteryResponse(BaseModel):
    lottery_id: int = Field(..., example="123")
    lottery_date: date = Field(..., example="2025-05-15")
    closed: bool = Field(..., example="false")

    model_config = ConfigDict(from_attributes=True)

class CreateLotteryRequest(BaseModel):
    target_date: date