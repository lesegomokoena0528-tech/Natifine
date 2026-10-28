from sqlalchemy import or_, func

from app.models.vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType
)

from app.repositories.base_repository import BaseRepository


class VehicleRepository(BaseRepository):

    def __init__(self):
        super().__init__(Vehicle)

    # ==========================================================
    # FINDERS
    # ==========================================================

    def find_by_registration(self, registration_number):

        return Vehicle.query.filter(
            func.upper(Vehicle.registration_number)
            == registration_number.upper()
        ).first()

    def find_by_vin(self, vin):

        return Vehicle.query.filter_by(
            vin=vin
        ).first()

    def find_by_engine_number(self, engine_number):

        return Vehicle.query.filter_by(
            engine_number=engine_number
        ).first()

    def find_by_owner(self, owner_id):

        return Vehicle.query.filter_by(
            owner_id=owner_id
        ).all()

    def find_active_by_owner(self, owner_id):

        return Vehicle.query.filter(
            Vehicle.owner_id == owner_id,
            Vehicle.status == VehicleStatus.ACTIVE
        ).all()

    # ==========================================================
    # STATUS
    # ==========================================================

    def find_by_status(self, status):

        return Vehicle.query.filter(
            Vehicle.status == status
        ).all()

    def active_vehicles(self):

        return self.find_by_status(
            VehicleStatus.ACTIVE
        )

    def stolen_vehicles(self):

        return self.find_by_status(
            VehicleStatus.STOLEN
        )

    def scrapped_vehicles(self):

        return self.find_by_status(
            VehicleStatus.SCRAPPED
        )

    def sold_vehicles(self):

        return self.find_by_status(
            VehicleStatus.SOLD
        )

    # ==========================================================
    # TYPE
    # ==========================================================

    def find_by_vehicle_type(self, vehicle_type):

        return Vehicle.query.filter(
            Vehicle.vehicle_type == vehicle_type
        ).all()

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(self, keyword):

        keyword = f"%{keyword}%"

        return Vehicle.query.filter(

            or_(

                Vehicle.registration_number.ilike(keyword),

                Vehicle.make.ilike(keyword),

                Vehicle.model.ilike(keyword),

                Vehicle.vin.ilike(keyword),

                Vehicle.engine_number.ilike(keyword)

            )

        ).all()

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def exists_registration(self, registration_number):

        return self.find_by_registration(
            registration_number
        ) is not None

    def exists_vin(self, vin):

        return self.find_by_vin(vin) is not None

    def exists_engine_number(self, engine_number):

        return self.find_by_engine_number(
            engine_number
        ) is not None

    # ==========================================================
    # FILTERS
    # ==========================================================

    def filter(

        self,

        owner_id=None,

        status=None,

        vehicle_type=None,

        year=None

    ):

        query = Vehicle.query

        if owner_id:
            query = query.filter(
                Vehicle.owner_id == owner_id
            )

        if status:
            query = query.filter(
                Vehicle.status == status
            )

        if vehicle_type:
            query = query.filter(
                Vehicle.vehicle_type == vehicle_type
            )

        if year:
            query = query.filter(
                Vehicle.year == year
            )

        return query.all()

    # ==========================================================
    # PAGINATION
    # ==========================================================

    def paginate(

        self,

        page=1,

        per_page=20

    ):

        return Vehicle.query.order_by(

            Vehicle.created_at.desc()

        ).paginate(

            page=page,

            per_page=per_page,

            error_out=False

        )

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def count_all(self):

        return Vehicle.query.count()

    def count_active(self):

        return Vehicle.query.filter(

            Vehicle.status == VehicleStatus.ACTIVE

        ).count()

    def count_stolen(self):

        return Vehicle.query.filter(

            Vehicle.status == VehicleStatus.STOLEN

        ).count()

    def count_scrapped(self):

        return Vehicle.query.filter(

            Vehicle.status == VehicleStatus.SCRAPPED

        ).count()

    def count_by_owner(self, owner_id):

        return Vehicle.query.filter(

            Vehicle.owner_id == owner_id

        ).count()

    # ==========================================================
    # OWNERSHIP
    # ==========================================================

    def transfer_owner(

        self,

        vehicle,

        new_owner_id

    ):

        vehicle.owner_id = new_owner_id

        self.update()

        return vehicle

    # ==========================================================
    # RECENT
    # ==========================================================

    def recent(

        self,

        limit=10

    ):

        return Vehicle.query.order_by(

            Vehicle.created_at.desc()

        ).limit(limit).all()