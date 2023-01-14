from typing import Any, Generic, Type, TypeVar

from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import Session, SQLModel, select

from youtube_rss.crud import DeleteError, RecordNotFoundError

ModelClass = TypeVar("ModelClass", bound=SQLModel)
SchemaCreateClass = TypeVar("SchemaCreateClass", bound=SQLModel)
SchemaUpdateClass = TypeVar("SchemaUpdateClass", bound=SQLModel)


class BaseCRUD(Generic[ModelClass, SchemaCreateClass, SchemaUpdateClass]):
    def __init__(self, model: Type[ModelClass]) -> None:
        """
        Initialize the CRUD object.

        Args:
            model: The model class to operate on.
        """
        self.model = model

    async def get_all(self, db: Session) -> list[ModelClass] | None:
        """
        Get all records for the model.

        Args:
            db (Session): The database session.

        Returns:
            A list of all records, or None if there are none.
        """
        statement = select(self.model)
        return db.exec(statement).all()

    async def get(self, *args: BinaryExpression[Any], db: Session, **kwargs: Any) -> ModelClass:
        """
        Get a record by its primary key(s).

        Args:
            args: Binary expressions to filter by.
            kwargs: Keyword arguments to filter by.
            db (Session): The database session.

        Returns:
            The matching record.

        Raises:
            RecordNotFoundError: If no matching record is found.
        """
        statement = select(self.model).filter(*args).filter_by(**kwargs)

        result = db.exec(statement).first()
        if result is None:
            raise RecordNotFoundError(
                f"{self.model.__name__}({args=} {kwargs=}) not found in database"
            )
        return result

    async def get_or_none(
        self, db: Session, *args: BinaryExpression[Any], **kwargs: Any
    ) -> ModelClass | None:
        """
        Get a record by its primary key(s), or return None if no matching record is found.

        Args:
            args: Binary expressions to filter by.
            kwargs: Keyword arguments to filter by.
            db (Session): The database session.

        Returns:
            The matching record, or None.
        """
        try:
            result = await self.get(*args, db=db, **kwargs)
        except RecordNotFoundError:
            return None
        return result

    async def get_many(
        self, db: Session, *args: BinaryExpression[Any], **kwargs: Any
    ) -> list[ModelClass]:
        """
        Retrieve multiple rows from the database that match the given criteria.

        Args:
            args: Binary expressions used to filter the rows to be retrieved.
            kwargs: Keyword arguments used to filter the rows to be retrieved.
            db (Session): The database session.

        Returns:
            A list of records that match the given criteria.
        """

        statement = select(self.model).filter(*args).filter_by(**kwargs)
        return db.exec(statement).fetchmany()

    async def create(self, db: Session, in_obj: SchemaCreateClass) -> ModelClass:
        """
        Create a new record.

        Args:
            in_obj: The object to create.
            db (Session): The database session.

        Returns:
            The created object.
        """
        out_obj = self.model(**in_obj.dict())

        db.add(out_obj)
        db.commit()
        db.refresh(out_obj)
        return out_obj

    async def update(
        self,
        in_obj: SchemaCreateClass | SchemaUpdateClass,
        *args: BinaryExpression[Any],
        db: Session,
        **kwargs: Any,
    ) -> ModelClass:
        """
        Update an existing record.

        Args:
            in_obj: The updated object.
            args: Binary expressions to filter by.
            db (Session): The database session.
            kwargs: Keyword arguments to filter by.

        Returns:
            The updated object.

        """

        db_obj = await self.get(*args, db=db, **kwargs)

        in_obj_values = in_obj.dict(exclude_unset=True, exclude_none=True)
        db_obj_values = db_obj.dict()
        for in_obj_key, in_obj_value in in_obj_values.items():
            if in_obj_value != db_obj_values[in_obj_key]:
                setattr(db_obj, in_obj_key, in_obj_value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    async def delete(self, *args: BinaryExpression[Any], db: Session, **kwargs: Any) -> None:
        """
        Delete a record.

        Args:
            args: Binary expressions to filter by.
            kwargs: Keyword arguments to filter by.
            db (Session): The database session.

        Raises:
            DeleteError: If an error occurs while deleting the record.
        """
        db_obj = await self.get(*args, db=db, **kwargs)
        try:
            db.delete(db_obj)
            db.commit()
        except Exception as exc:
            raise DeleteError("Error while deleting") from exc
