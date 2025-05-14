from sqlalchemy import Column, Date, Boolean, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base

class Lottery(Base):
    __tablename__ = 'lotteries'

    lottery_id = Column(Integer, primary_key=True, autoincrement=True)
    lottery_date = Column(Date, nullable=False, unique=True)
    closed = Column(Boolean, default=False)

    ballots = relationship("Ballot", back_populates="lottery")
    winning_ballot_entry = relationship("WinningBallot", back_populates="lottery", uselist=False)

