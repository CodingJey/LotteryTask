import uuid
from sqlalchemy import  Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.models.base import Base

class Ballot(Base):
    __tablename__ = 'ballots'

    ballot_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('participants.user_id'), nullable=False)
    lottery_id = Column(UUID(as_uuid=True), ForeignKey('lotteries.lottery_id'), nullable=False)
    ballot_number = Column(String)
    expiry_date = Column(Date)

    user = relationship("Participant", back_populates="ballots")
    lottery = relationship("Lottery", back_populates="ballots")
    winner = relationship("WinningBallot", back_populates="ballot", uselist=False)
