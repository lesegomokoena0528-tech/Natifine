import os
import tempfile
import uuid
from datetime import datetime

from app.services.storage_service import StorageService
from app.utils.pdf_export import PDFExporter
from app.utils.excel_export import ExcelExporter
from app.utils.csv_export import CSVExporter


class ExportService:

    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    EXPORT_FOLDER = os.path.join(BASE_DIR, "exports", "reports")

    CONTENT_TYPES = {
        "pdf": "application/pdf",
        "xlsx": (
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        "csv": "text/csv",
    }

    def __init__(self):

        self.storage = StorageService(self.EXPORT_FOLDER)

        if not self.storage.use_blob:
            try:
                os.makedirs(
                    self.EXPORT_FOLDER,
                    exist_ok=True
                )
            except OSError:
                pass

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

        result = self.storage.save_bytes(
            data,
            blob_pathname=f"exports/reports/{filename}",
            local_path=os.path.join(
                self.EXPORT_FOLDER,
                filename
            ),
            content_type=self.CONTENT_TYPES.get(extension),
            overwrite=True
        )

        return self._response(
            filename,
            result["path"],
            result["url"]
        )

    @staticmethod
    def _filename(name, extension):

        return (

            f"{name}_"

            f"{datetime.utcnow():%Y%m%d_%H%M%S}_"

            f"{uuid.uuid4().hex[:8]}."

            f"{extension}"

        )

    @staticmethod
    def _response(filename, path, url=None):

        return {

            "filename": filename,

            "path": path,

            "url": url

        }
