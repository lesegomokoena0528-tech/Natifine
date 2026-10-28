import os
import uuid

from werkzeug.utils import secure_filename


class UploadService:

    ALLOWED_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "pdf"
    }

    UPLOAD_FOLDER = "uploads/disputes"

    def __init__(self):

        os.makedirs(
            self.UPLOAD_FOLDER,
            exist_ok=True
        )

    def allowed_file(self, filename):

        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower()
            in self.ALLOWED_EXTENSIONS
        )

    def save(self, file):

        if not self.allowed_file(file.filename):

            raise ValueError("Unsupported file type.")

        extension = file.filename.rsplit(".", 1)[1]

        filename = f"{uuid.uuid4()}.{extension}"

        filename = secure_filename(filename)

        path = os.path.join(

            self.UPLOAD_FOLDER,

            filename

        )

        file.save(path)

        return path

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

        folder = os.path.join("uploads", category)

        os.makedirs(folder, exist_ok=True)

        path = os.path.join(folder, filename)

        file.save(path)

        return {

            "file_name": filename,

            "original_name": file.filename,

            "mime_type": getattr(
                file,
                "mimetype",
                None
            ) or "application/octet-stream",

            "size": os.path.getsize(path),

            "path": path

        }