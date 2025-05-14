from sqlalchemy import Column, ForeignKey, Index, Integer, String, Date,Numeric
from sqlalchemy.orm import relationship
from app.models.base import Base

class Ballot(Base):
    __tablename__ = 'ballots'

    ballot_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('participants.user_id'), nullable=False)
    lottery_id = Column(Integer, ForeignKey('lotteries.lottery_id'), nullable=False)
    ballot_number = Column(Integer)
    expiry_date = Column(Date)

    users = relationship("Participant", back_populates="ballots") 
    lottery = relationship("Lottery", back_populates="ballots") 

    winning_entry = relationship("WinningBallot", back_populates="ballot", uselist=False)

    __table_args__ = (
        Index('idx_ballots_user', 'user_id'),
        Index('idx_ballots_lottery', 'lottery_id'),
    )
    