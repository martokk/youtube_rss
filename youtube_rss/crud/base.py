from typing import Any, Generic, Type, TypeVar

from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import Session, SQLModel, select

from youtube_rss.crud.exceptions import DeleteError, RecordNotFoundError

ModelClass = TypeVar("ModelClass", bound=SQLModel)
ModelCreateClass = TypeVar("ModelCreateClass", bound=SQLModel)
ModelReadClass = TypeVar("ModelReadClass", bound=SQLModel)


class BaseCRUD(Generic[ModelClass, ModelCreateClass, ModelReadClass]):
    def __init__(self, model: Type[ModelClass], session: Session) -> None:
        """
        Initialize the CRUD object.

        Args:
            model: The model class to operate on.
            session: The SQLAlchemy session to use.
        """
        self.model = model
        self.session = session

    async def get_all(self) -> list[ModelClass] | None:
        """
        Get all records for the model.

        Returns:
            A list of all records, or None if there are none.
        """
        statement = select(self.model)
        return self.session.exec(statement).all()

    async def get(self, *args: BinaryExpression[Any], **kwargs: Any) -> ModelClass:
        """
        Get a record by its primary key(s).

        Args:
            args: Binary expressions to filter by.
            kwargs: Keyword arguments to filter by.

        Returns:
            The matching record.

        Raises:
            RecordNotFoundError: If no matching record is found.
        """
        statement = select(self.model).filter(*args).filter_by(**kwargs)

        result = self.session.exec(statement).first()
        if result is None:
            raise RecordNotFoundError(
                f"{self.model.__name__}({args=} {kwargs=}) not found in database"
            )
        return result

    async def get_or_none(self, *args: BinaryExpression[Any], **kwargs: Any) -> ModelClass | None:
        """
        Get a record by its primary key(s), or return None if no matching record is found.

        Args:
            args: Binary expressions to filter by.
            kwargs: Keyword arguments to filter by.

        Returns:
            The matching record, or None.
        """
        try:
            result = await self.get(*args, **kwargs)
        except RecordNotFoundError:
            return None
        return result

    async def get_many(self, *args: BinaryExpression[Any], **kwargs: Any) -> list[ModelClass]:
        """
        Retrieve multiple rows from the database that match the given criteria.

        Args:
            args: Binary expressions used to filter the rows to be retrieved.
            kwargs: Keyword arguments used to filter the rows to be retrieved.

        Returns:
            A list of records that match the given criteria.
        """

        statement = select(self.model).filter(*args).filter_by(**kwargs)
        return self.session.exec(statement).fetchmany()

    async def create(self, in_obj: ModelClass) -> ModelClass:
        """
        Create a new record.

        Args:
            in_obj: The object to create.

        Returns:
            The created object.
        """
        self.session.add(in_obj)
        self.session.commit()
        self.session.refresh(in_obj)
        return in_obj

    async def update(
        self, in_obj: ModelCreateClass, *args: BinaryExpression[Any], **kwargs: Any
    ) -> ModelClass:
        """
        Update an existing record.

        Args:
            in_obj: The updated object.
            args: Binary expressions to filter by.
            kwargs: Keyword arguments to filter by.

        Returns:
            The updated object.

        """

        db_obj = await self.get(*args, **kwargs)

        in_obj_update_data = in_obj.dict(exclude_unset=True, exclude_none=True)
        for key, value in in_obj_update_data.items():
            setattr(db_obj, key, value)

        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    async def delete(self, *args: BinaryExpression[Any], **kwargs: Any) -> None:
        """
        Delete a record.

        Args:
            args: Binary expressions to filter by.
            kwargs: Keyword arguments to filter by.

        Raises:
            DeleteError: If an error occurs while deleting the record.
        """
        db_obj = await self.get(*args, **kwargs)
        try:
            self.session.delete(db_obj)
            self.session.commit()
        except Exception as exc:
            raise DeleteError("Error while deleting") from exc
