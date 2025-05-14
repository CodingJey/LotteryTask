from sqlalchemy import  Column, Integer, Date, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class Participant(Base):
    __tablename__ = 'participants'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    birth_date = Column(Date, nullable=False)

    ballots = relationship("Ballot", back_populates="users")
 