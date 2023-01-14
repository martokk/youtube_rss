from youtube_rss.models.user import UserCreate, UserDB, UserUpdate

from .base import BaseCRUD


class UserCRUD(BaseCRUD[UserDB, UserCreate, UserUpdate]):
    pass


user = UserCRUD(UserDB)
