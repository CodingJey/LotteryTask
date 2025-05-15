from sqlalchemy import Column, Date, ForeignKey, Numeric, Integer, Index
from sqlalchemy.orm import relationship
from app.models.base import Base


class WinningBallot(Base):
    __tablename__ = 'winningballots'

    lottery_id = Column(Integer, ForeignKey('lotteries.lottery_id'), primary_key=True)
    ballot_id = Column(Integer, ForeignKey('ballots.ballot_id'), nullable=False, unique=True)
    winning_date = Column(Date, nullable=False)
    winning_amount = Column(Integer, nullable=False)

    lottery = relationship("Lottery", back_populates="winning_ballot_entry")
    ballot = relationship("Ballot", back_populates="winning_entry")

    __table_args__ = (
        Index('idx_winning_date', 'winning_date'),
    )