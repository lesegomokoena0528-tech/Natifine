from marshmallow import Schema, fields


class DashboardStatisticsSchema(Schema):

    total_users = fields.Integer()

    total_officers = fields.Integer()

    total_citizens = fields.Integer()

    total_vehicles = fields.Integer()

    total_fines = fields.Integer()

    unpaid_fines = fields.Integer()

    paid_fines = fields.Integer()

    disputed_fines = fields.Integer()

    total_payments = fields.Integer()

    total_revenue = fields.Decimal(as_string=True)

    today_revenue = fields.Decimal(as_string=True)


class DashboardChartSchema(Schema):

    month = fields.String()

    fines = fields.Integer()

    payments = fields.Decimal(as_string=True)


class DashboardRecentActivitySchema(Schema):

    title = fields.String()

    description = fields.String()

    created_at = fields.DateTime()


class DashboardSchema(Schema):

    statistics = fields.Nested(

        DashboardStatisticsSchema

    )

    revenue_chart = fields.List(

        fields.Nested(DashboardChartSchema)

    )

    recent_activities = fields.List(

        fields.Nested(

            DashboardRecentActivitySchema

        )

    )