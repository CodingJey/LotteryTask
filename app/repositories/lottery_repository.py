from app.models.lottery import Lottery
from app.repositories.base_repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.orm import Session
import logging 
from datetime import date
from typing import List, Optional
from fastapi import HTTPException

logger = logging.getLogger("app")

class LotteryRepository(BaseRepository[Lottery]):
    def __init__(self, session: Session):
        super().__init__(session, Lottery)

    def _init_lottery(self, input_date: date, closed: bool) -> Optional[Lottery]:
        l = self.model()
        l.lottery_date = input_date
        if closed:
            return None
        l.closed = closed
        return l

    def create_lottery(self, input_date: date, closed: bool = False) -> Optional[Lottery]:
        logger.debug(f"Attempting to create Lottery for Date={input_date}, Closed={closed}")
        lottery = self._init_lottery(input_date, closed)
        if lottery is None:
            logger.warning(f"Initialization of Lottery for Date={input_date} with Closed={closed} returned None. Lottery not created.")
            return None
        try:
            self.session.add(lottery)
            self.session.commit()
            refreshed_lottery = self._refresh(lottery)
            logger.info(f"Successfully created Lottery with ID={refreshed_lottery.lottery_id} for Date={refreshed_lottery.lottery_date}")
            return refreshed_lottery
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to create Lottery for Date={input_date}: {e}", exc_info=True)
            return None

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
            raise HTTPException(status_code=409, detail="Lottery already closed") 
        else:
            logger.warning(f"No Lottery found for Date={target_date}")
        return lottery

    def get_lottery(self, lottery_id) -> Optional[Lottery]:
        return self.get(lottery_id)

    def list_lotteries(self) -> List[Lottery]:
        return self.list_all()

    def mark_as_closed(self, lottery_id: int) -> Optional[Lottery]:
        """
        Marks a lottery as closed by its ID.
        Sets the 'closed' attribute to True and persists the change.
        Returns the updated lottery instance or None if not found.
        """
        logger.debug(f"Attempting to mark Lottery ID={lottery_id} as closed")
        lottery = self.get_lottery(lottery_id)
        if lottery:
            if lottery.closed:
                logger.info(f"Lottery ID={lottery_id} is already closed.")
                return lottery
            try:
                lottery.closed = True
                self.session.add(lottery) 
                self.session.commit()
                refreshed_lottery = self._refresh(lottery)
                logger.info(f"Successfully marked Lottery ID={refreshed_lottery.lottery_id} as closed.")
                return refreshed_lottery
            except Exception as e:
                self.session.rollback()
                logger.error(f"Failed to mark Lottery ID={lottery_id} as closed: {e}", exc_info=True)
                return None 
        else:
            logger.warning(f"Lottery ID={lottery_id} not found. Cannot mark as closed.")
            return None

    def close_lottery_by_date(self, target_date: date) -> Optional[Lottery]:
        """
        Marks a lottery as closed by its date.
        Sets the 'closed' attribute to True and persists the change.
        Returns the updated lottery instance or None if not found.
        """
        logger.debug(f"Attempting to close Lottery for Date={target_date}")
        lottery = self.get_by_date(target_date)
        if lottery:
            if lottery.closed:
                logger.info(f"Lottery for Date={target_date} (ID={lottery.lottery_id}) is already closed.")
                return lottery # Already closed
            try:
                lottery.closed = True
                self.session.add(lottery)
                self.session.commit()
                refreshed_lottery = self._refresh(lottery)
                logger.info(f"Successfully closed Lottery ID={refreshed_lottery.lottery_id} for Date={target_date}.")
                return refreshed_lottery
            except Exception as e:
                self.session.rollback()
                logger.error(f"Failed to close Lottery for Date={target_date}: {e}", exc_info=True)
                return None
        else:
            logger.warning(f"Lottery for Date={target_date} not found. Cannot close.")
            return None



def get_lottery_repository(session: Session) -> LotteryRepository:
    return LotteryRepository(session)