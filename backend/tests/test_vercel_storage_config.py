import pytest

from app.config.settings import (
    _database_url_from_env,
    _normalize_database_url,
)
from app.services.storage_service import (
    StorageConfigurationError,
    StorageService,
)
from app.services import storage_service


DATABASE_URL_VARIABLES = (
    "DATABASE_URL",
    "POSTGRES_URL",
    "POSTGRES_URL_NON_POOLING",
)


def _clear_storage_environment(monkeypatch):
    for name in (
        "VERCEL",
        "VERCEL_ENV",
        "STORAGE_BACKEND",
        "BLOB_READ_WRITE_TOKEN",
        "VERCEL_BLOB_READ_WRITE_TOKEN",
        "BLOB_STORE_ID",
    ):
        monkeypatch.delenv(name, raising=False)


def test_database_url_prefers_database_url(monkeypatch):
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://db.example/natifine")
    monkeypatch.setenv("POSTGRES_URL", "postgresql://other.example/natifine")

    assert _database_url_from_env() == "postgresql://db.example/natifine"
    assert _normalize_database_url(_database_url_from_env()) == (
        "postgresql+psycopg2://db.example/natifine"
    )


def test_vercel_requires_a_postgres_url(monkeypatch):
    for name in DATABASE_URL_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("VERCEL", "1")

    with pytest.raises(RuntimeError, match="requires DATABASE_URL"):
        _database_url_from_env()


def test_vercel_rejects_non_postgres_database_url(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("DATABASE_URL", "mysql://db.example/natifine")

    with pytest.raises(RuntimeError, match="requires a Postgres URL"):
        _database_url_from_env()


def test_vercel_environment_marker_requires_a_postgres_url(monkeypatch):
    for name in DATABASE_URL_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.setenv("VERCEL_ENV", "production")

    with pytest.raises(RuntimeError, match="requires DATABASE_URL"):
        _database_url_from_env()


def test_storage_uses_local_disk_outside_vercel_without_blob_credentials(
    monkeypatch,
):
    _clear_storage_environment(monkeypatch)

    assert StorageService().backend == "local"


def test_storage_fails_closed_on_vercel_without_blob_credentials(monkeypatch):
    _clear_storage_environment(monkeypatch)
    monkeypatch.setenv("VERCEL", "1")

    with pytest.raises(StorageConfigurationError, match="credentials are missing"):
        _ = StorageService().backend


def test_storage_uses_blob_when_store_id_is_configured(monkeypatch):
    _clear_storage_environment(monkeypatch)
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("BLOB_STORE_ID", "store-id")

    assert StorageService().backend == "vercel_blob"


def test_local_storage_cannot_be_forced_on_vercel(monkeypatch):
    _clear_storage_environment(monkeypatch)
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("STORAGE_BACKEND", "local")

    with pytest.raises(StorageConfigurationError, match="not persistent on Vercel"):
        _ = StorageService().backend


def test_blob_storage_round_trip_uses_sdk(monkeypatch):
    _clear_storage_environment(monkeypatch)
    monkeypatch.setenv("BLOB_STORE_ID", "store-id")
    calls = {}

    class BlobClient:
        @staticmethod
        def put_blob(pathname, data, **options):
            calls["put"] = (pathname, data, options)
            return type(
                "PutResult",
                (),
                {"url": "https://store.private.blob.vercel-storage.com/file.pdf",
                 "pathname": pathname},
            )()

        @staticmethod
        def get_blob(path, *, access):
            calls["get"] = (path, access)
            return type("GetResult", (), {"body": b"stored file"})()

        @staticmethod
        def delete_blob(path):
            calls["delete"] = path

    monkeypatch.setattr(storage_service, "vercel_blob", BlobClient)
    storage = StorageService()
    result = storage.save_bytes(
        b"stored file",
        blob_pathname="receipts/file.pdf",
        local_path="unused.pdf",
        content_type="application/pdf",
        overwrite=True,
    )

    assert result["storage"] == "vercel_blob"
    assert result["url"].endswith("/file.pdf")
    assert calls["put"] == (
        "receipts/file.pdf",
        b"stored file",
        {
            "access": "private",
            "content_type": "application/pdf",
            "allow_overwrite": True,
        },
    )

    assert storage.read(result["path"]) == b"stored file"
    assert calls["get"] == (result["path"], "private")
    storage.delete(result["path"])
    assert calls["delete"] == result["path"]
