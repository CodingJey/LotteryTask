import uuid
from sqlalchemy import Column, String, Date, Boolean, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.models.base import Base

class Lottery(Base):
    __tablename__ = 'lotteries'

    lottery_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False, unique=True)
    closed = Column(Boolean, default=False)

    ballots = relationship("Ballot", back_populates="lottery")
    winner = relationship("WinningBallot", back_populates="lottery", uselist=False)
