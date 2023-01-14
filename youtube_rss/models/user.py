from typing import TYPE_CHECKING, Any

from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel

from youtube_rss.services.uuid import generate_uuid_from_string

if TYPE_CHECKING:
    from youtube_rss.models.source import Source


class UserBase(SQLModel):
    id: str = Field(primary_key=True, index=True, nullable=False, default=None)
    username: str = Field(index=True, nullable=False)
    email: str = Field(unique=True, nullable=False)


class UserDB(UserBase, table=True):
    password: str = Field(nullable=False)
    sources: list["Source"] = Relationship(
        back_populates="created_user",
        sa_relationship_kwargs={
            "cascade": "all, delete",  # Instruct the ORM how to track changes to local objects
        },
    )


class UserCreate(UserBase):
    password: str = Field(nullable=False)

    @root_validator(pre=True)
    def set_pre_validation_defaults(cls, values: dict[str, Any]) -> dict[str, Any]:
        _id = generate_uuid_from_string(string=values["username"])
        return {**values, "id": _id}


class UserUpdate(UserBase):
    pass


class UserRead(UserBase):
    pass


class UserLogin(SQLModel):
    username: str
    password: str
