import uuid
from sqlalchemy import Column, String, Date, Boolean, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.models.base import Base


class WinningBallot(Base):
    __tablename__ = 'winningballots'

    lottery_id = Column(UUID(as_uuid=True), ForeignKey('lotteries.lottery_id'), primary_key=True)
    ballot_id = Column(UUID(as_uuid=True), ForeignKey('ballots.ballot_id'), nullable=False)
    winning_date = Column(Date, nullable=False)
    winning_amount = Column(DECIMAL(100, 2), nullable=False)

    lottery = relationship("Lottery", back_populates="winner")
    ballot = relationship("Ballot", back_populates="winner")
