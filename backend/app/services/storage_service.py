import os

try:
    from vercel.blob import sync as vercel_blob
except ImportError:  # pragma: no cover - optional dependency for local dev
    vercel_blob = None


class StorageConfigurationError(RuntimeError):
    pass


class StorageService:
    """Persist files locally or in Vercel Blob.

    The backend is selected from ``STORAGE_BACKEND``:
      - ``auto`` (default): Vercel Blob when credentials are available.
      - ``vercel_blob``: always Vercel Blob.
      - ``local``: always the local filesystem (development/tests).
    """

    def __init__(self, local_folder="uploads"):
        self.local_folder = local_folder

    @staticmethod
    def _config(name, default=None):
        try:
            from flask import current_app

            value = current_app.config.get(name)
            if value is not None:
                return value
        except RuntimeError:
            pass

        return os.getenv(name, default)

    @property
    def backend(self):
        configured = str(
            self._config("STORAGE_BACKEND", "auto") or "auto"
        ).strip().lower()
        is_vercel = bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV"))
        token = (
            self._config("BLOB_READ_WRITE_TOKEN")
            or self._config("VERCEL_BLOB_READ_WRITE_TOKEN")
        )
        store_id = self._config("BLOB_STORE_ID")
        has_credentials = bool(token or store_id)

        if configured in ("local", "filesystem", "disk"):
            if is_vercel:
                raise StorageConfigurationError(
                    "Local file storage is not persistent on Vercel. "
                    "Connect a Vercel Blob store and set STORAGE_BACKEND "
                    "to 'auto' or 'vercel_blob'."
                )
            return "local"

        if configured in ("vercel_blob", "vercel-blob", "blob", "vercel"):
            if not has_credentials:
                if is_vercel:
                    return "vercel_blob"
                raise StorageConfigurationError(
                    "Vercel Blob is enabled but neither "
                    "BLOB_READ_WRITE_TOKEN nor BLOB_STORE_ID is configured."
                )
            return "vercel_blob"

        if configured != "auto":
            raise StorageConfigurationError(
                f"Unsupported storage backend: {configured!r}."
            )

        if has_credentials:
            return "vercel_blob"
        if is_vercel:
            return "vercel_blob"
        return "local"

    @property
    def use_blob(self):
        return self.backend == "vercel_blob"

    @property
    def access(self):
        access = str(self._config("BLOB_ACCESS", "private") or "private")
        access = access.strip().lower()
        return access if access in ("public", "private") else "private"

    def _blob(self):
        token = (
            self._config("BLOB_READ_WRITE_TOKEN")
            or self._config("VERCEL_BLOB_READ_WRITE_TOKEN")
        )
        store_id = self._config("BLOB_STORE_ID")

        if not (token or store_id):
            raise StorageConfigurationError(
                "Vercel Blob is enabled but neither "
                "BLOB_READ_WRITE_TOKEN nor BLOB_STORE_ID is configured."
            )

        if vercel_blob is None:
            raise StorageConfigurationError(
                "Vercel Blob is enabled but the 'vercel-blob' package is not "
                "installed. Run: pip install -r requirements.txt"
            )
        return vercel_blob

    def save_bytes(
        self,
        data,
        blob_pathname,
        local_path,
        content_type=None,
        overwrite=False,
    ):
        """Store bytes and return a path that can later be read back."""
        size = len(data)

        if self.use_blob:
            result = self._blob().put_blob(
                blob_pathname,
                data,
                access=self.access,
                content_type=content_type,
                allow_overwrite=overwrite,
            )
            return {
                "path": result.url,
                "url": result.url,
                "pathname": result.pathname,
                "size": size,
                "storage": "vercel_blob",
            }

        folder = os.path.dirname(local_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(local_path, "wb") as handle:
            handle.write(data)

        return {
            "path": local_path,
            "url": None,
            "pathname": blob_pathname,
            "size": size,
            "storage": "local",
        }

    def save_file(
        self,
        file,
        blob_pathname,
        local_path,
        overwrite=False,
    ):
        data = file.read()
        return self.save_bytes(
            data,
            blob_pathname=blob_pathname,
            local_path=local_path,
            content_type=getattr(file, "mimetype", None),
            overwrite=overwrite,
        )

    def read(self, path):
        if not path:
            raise FileNotFoundError("No storage path was provided.")

        if str(path).startswith(("http://", "https://")):
            result = self._blob().get_blob(path, access=self.access)
            return result.body

        with open(path, "rb") as handle:
            return handle.read()

    def delete(self, path):
        if not path:
            return

        if str(path).startswith(("http://", "https://")):
            self._blob().delete_blob(path)
            return

        try:
            os.remove(path)
        except FileNotFoundError:
            pass
