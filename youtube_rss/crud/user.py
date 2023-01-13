from sqlmodel import Session

from youtube_rss.db.database import engine
from youtube_rss.models.user import UserCreate, UserDB, UserRead

from .base import BaseCRUD


class UserCRUD(BaseCRUD[UserDB, UserCreate, UserRead]):
    def __init__(self, session: Session) -> None:
        super().__init__(model=UserDB, session=session)


with Session(engine) as _session:
    user_crud = UserCRUD(session=_session)
