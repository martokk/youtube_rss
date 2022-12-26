from sqlmodel import Field, SQLModel


class Source(SQLModel, table=True):
    source_id: str = Field(primary_key=True, nullable=False)
    name: str = Field()
    url: str = Field()
