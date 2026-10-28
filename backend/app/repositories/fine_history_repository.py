from app.models.fine_history import FineHistory

from app.repositories.base_repository import BaseRepository


class FineHistoryRepository(BaseRepository):

    def __init__(self):
        super().__init__(FineHistory)

    def find_by_fine(self, fine_id):

        return (
            FineHistory.query
            .filter_by(fine_id=fine_id)
            .order_by(
                FineHistory.change_date.desc()
            )
            .all()
        )

    def latest(self, fine_id):

        return (
            FineHistory.query
            .filter_by(fine_id=fine_id)
            .order_by(
                FineHistory.change_date.desc()
            )
            .first()
        )