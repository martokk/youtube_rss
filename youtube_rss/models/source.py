from sqlmodel import Field, SQLModel


class SourceBase(SQLModel):
    url: str = Field()


class Source(SourceBase, table=True):
    source_id: str = Field(primary_key=True, nullable=False)
    name: str = Field()


class SourceCreate(SourceBase):
    pass
