import os
import uuid
from datetime import datetime

from app.utils.pdf_export import PDFExporter
from app.utils.excel_export import ExcelExporter
from app.utils.csv_export import CSVExporter


class ExportService:

    EXPORT_FOLDER = "exports/reports"

    def __init__(self):

        os.makedirs(
            self.EXPORT_FOLDER,
            exist_ok=True
        )

    def export_pdf(self, report_name, data):

        filename = self._filename(report_name, "pdf")

        path = os.path.join(
            self.EXPORT_FOLDER,
            filename
        )

        PDFExporter().generate(
            path,
            report_name,
            data
        )

        return self._response(filename, path)

    def export_excel(self, report_name, data):

        filename = self._filename(
            report_name,
            "xlsx"
        )

        path = os.path.join(
            self.EXPORT_FOLDER,
            filename
        )

        ExcelExporter().generate(
            path,
            data
        )

        return self._response(filename, path)

    def export_csv(self, report_name, data):

        filename = self._filename(
            report_name,
            "csv"
        )

        path = os.path.join(
            self.EXPORT_FOLDER,
            filename
        )

        CSVExporter().generate(
            path,
            data
        )

        return self._response(filename, path)

    @staticmethod
    def _filename(name, extension):

        return (

            f"{name}_"

            f"{datetime.utcnow():%Y%m%d_%H%M%S}_"

            f"{uuid.uuid4().hex[:8]}."

            f"{extension}"

        )

    @staticmethod
    def _response(filename, path):

        return {

            "filename": filename,

            "path": path

        }