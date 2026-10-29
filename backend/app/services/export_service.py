import os
import tempfile
import uuid
from datetime import datetime
from io import BytesIO

from flask import send_file

from app.utils.pdf_export import PDFExporter
from app.utils.excel_export import ExcelExporter
from app.utils.csv_export import CSVExporter


class ExportService:

    CONTENT_TYPES = {
        "pdf": "application/pdf",
        "xlsx": (
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        "csv": "text/csv",
    }

    def export_pdf(self, report_name, data):

        return self._export(
            report_name,
            "pdf",
            lambda path: PDFExporter().generate(
                path,
                report_name,
                data
            )
        )

    def export_excel(self, report_name, data):

        return self._export(
            report_name,
            "xlsx",
            lambda path: ExcelExporter().generate(
                path,
                data
            )
        )

    def export_csv(self, report_name, data):

        return self._export(
            report_name,
            "csv",
            lambda path: CSVExporter().generate(
                path,
                data
            )
        )

    def _export(self, report_name, extension, producer):

        filename = self._filename(report_name, extension)

        handle, temp_path = tempfile.mkstemp(
            suffix=f".{extension}"
        )
        os.close(handle)

        try:
            producer(temp_path)

            with open(temp_path, "rb") as generated:
                data = generated.read()
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass

        return send_file(
            BytesIO(data),
            mimetype=self.CONTENT_TYPES[extension],
            as_attachment=True,
            download_name=filename,
        )

    @staticmethod
    def _filename(name, extension):

        return (

            f"{name}_"

            f"{datetime.utcnow():%Y%m%d_%H%M%S}_"

            f"{uuid.uuid4().hex[:8]}."

            f"{extension}"

        )
