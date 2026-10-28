from app.config.celery import celery

from app.services.export_service import ExportService

service = ExportService()


@celery.task(
    name="reports.export_pdf"
)
def export_pdf_task(

        report_name,

        data

):

    return service.export_pdf(

        report_name,

        data

    )


@celery.task(
    name="reports.export_excel"
)
def export_excel_task(

        report_name,

        data

):

    return service.export_excel(

        report_name,

        data

    )


@celery.task(
    name="reports.export_csv"
)
def export_csv_task(

        report_name,

        data

):

    return service.export_csv(

        report_name,

        data

    )