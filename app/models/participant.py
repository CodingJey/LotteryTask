import uuid
from sqlalchemy import  Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.models.base import Base

class Participant(Base):
    __tablename__ = 'participants'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)

    ballots = relationship("Ballot", back_populates="user")
