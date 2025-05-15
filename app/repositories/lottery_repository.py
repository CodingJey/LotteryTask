from app.models.lottery import Lottery
from app.repositories.base_repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.orm import Session
import logging 
from datetime import date
from typing import List, Optional

logger = logging.getLogger("app")

class LotteryRepository(BaseRepository[Lottery]):
    def __init__(self, session: Session):
        super().__init__(session, Lottery)

    def create_lottery(self, input_date: date, closed: bool = False) -> Optional[Lottery]:
        logger.debug(f"Creating Lottery on Date={input_date}")
        lottery = self._init_lottery(input_date, closed)
        if lottery is None:
            return None
        self.session.add(lottery)
        self.session.commit()
        logger.info(f"Created Lottery with ID={lottery.lottery_id}")
        return self._refresh(lottery)

    def get_by_date(self, target_date: date) -> Optional[Lottery]:
        """
        Fetch the Lottery whose Date == target_date.
        Returns None if no such lottery exists.
        """
        logger.debug(f"Fetching Lottery with Date={target_date}")
        stmt = select(self.model).where(self.model.lottery_date == target_date)
        result = self.session.execute(stmt)
        lottery = result.scalars().first()
        if lottery:
            logger.info(f"Found Lottery ID={lottery.lottery_id} for Date={target_date}")
        else:
            logger.warning(f"No Lottery found for Date={target_date}")
        return lottery

    def get_lottery(self, lottery_id) -> Optional[Lottery]:
        return self.get(lottery_id)

    def list_lotteries(self) -> List[Lottery]:
        return self.list_all()

    def _init_lottery(self, input_date: date, closed: bool) -> Optional[Lottery]:
        l = self.model()
        l.lottery_date = input_date
        if closed:
            return None
        l.closed = closed
        return l

def get_lottery_repository(session: Session
) -> LotteryRepository:
    return LotteryRepository(session)