import os
import uuid

from werkzeug.utils import secure_filename

from app.services.storage_service import StorageService


class UploadService:

    ALLOWED_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "pdf"
    }

    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    def __init__(self):

        self.storage = StorageService(self.UPLOAD_FOLDER)

        if not self.storage.use_blob:

            try:
                os.makedirs(
                    self.UPLOAD_FOLDER,
                    exist_ok=True
                )
            except OSError:
                # Serverless filesystems are read-only; uploads will only
                # work once a Blob store is connected.
                pass

    def allowed_file(self, filename):

        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower()
            in self.ALLOWED_EXTENSIONS
        )

    def save(self, file):

        information = self.upload(file, "disputes")

        return information["path"]

    def upload(self, file, category="uploads"):
        """
        Store an uploaded file and return its metadata.

        Returns a dictionary with the stored file name, original name,
        MIME type, size and storage path, matching what the dispute
        service expects when recording a supporting document.
        """

        if not self.allowed_file(file.filename):

            raise ValueError("Unsupported file type.")

        extension = file.filename.rsplit(".", 1)[1].lower()

        filename = secure_filename(
            f"{uuid.uuid4().hex}.{extension}"
        )

        pathname = f"{category}/{filename}"

        local_path = os.path.join(
            self.UPLOAD_FOLDER,
            category,
            filename
        )

        result = self.storage.save_file(
            file,
            blob_pathname=pathname,
            local_path=local_path
        )

        return {

            "file_name": filename,

            "original_name": file.filename,

            "mime_type": getattr(
                file,
                "mimetype",
                None
            ) or "application/octet-stream",

            "size": result["size"],

            "path": result["path"],

            "url": result["url"]

        }
