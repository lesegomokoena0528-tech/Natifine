from typing import Generic, TypeVar, Type, Optional

from sqlalchemy.exc import SQLAlchemyError

from app.config.database import db

T = TypeVar("T")


class BaseRepository(Generic[T]):

    def __init__(self, model: Type[T]):
        self.model = model

    # ------------------------
    # CREATE
    # ------------------------

    def save(self, entity: T) -> T:

        try:
            db.session.add(entity)
            db.session.commit()
            return entity

        except SQLAlchemyError:
            db.session.rollback()
            raise

    # ------------------------
    # UPDATE
    # ------------------------

    def update(self, entity: Optional[T] = None) -> None:

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()
            raise

    # ------------------------
    # DELETE
    # ------------------------

    def delete(self, entity: T) -> None:

        try:
            db.session.delete(entity)
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()
            raise

    # ------------------------
    # FIND BY ID
    # ------------------------

    def find_by_id(self, entity_id):

        return self.model.query.get(entity_id)

    # ------------------------
    # EXISTS
    # ------------------------

    def exists(self, entity_id):

        return self.find_by_id(entity_id) is not None

    # ------------------------
    # COUNT
    # ------------------------

    def count(self):

        return self.model.query.count()

    # ------------------------
    # FIND ALL
    # ------------------------

    def find_all(self):

        return self.model.query.all()

    # ------------------------
    # PAGINATION
    # ------------------------

    def paginate(self, page=1, size=10):

        return self.model.query.paginate(
            page=page,
            per_page=size,
            error_out=False
        )