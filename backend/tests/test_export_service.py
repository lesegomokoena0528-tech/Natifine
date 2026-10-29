from app.services.export_service import ExportService


def test_csv_export_returns_downloadable_file(app):
    service = ExportService()

    with app.test_request_context():
        response = service.export_csv(
            "system_report",
            {"users": 3, "revenue": 125.50},
        )
        response.direct_passthrough = False

    assert response.mimetype == "text/csv"
    assert response.headers["Content-Disposition"].startswith(
        "attachment; filename=system_report_"
    )
    assert response.get_data().startswith(b"Field,Value")


def test_pdf_export_returns_downloadable_file(app):
    service = ExportService()

    with app.test_request_context():
        response = service.export_pdf(
            "system_report",
            {"users": 3, "revenue": 125.50},
        )
        response.direct_passthrough = False

    assert response.mimetype == "application/pdf"
    assert response.headers["Content-Disposition"].startswith(
        "attachment; filename=system_report_"
    )
    assert response.get_data().startswith(b"%PDF-")


def test_excel_export_returns_downloadable_file(app):
    service = ExportService()

    with app.test_request_context():
        response = service.export_excel(
            "system_report",
            {"users": 3, "revenue": 125.50},
        )
        response.direct_passthrough = False

    assert response.mimetype == (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert response.headers["Content-Disposition"].startswith(
        "attachment; filename=system_report_"
    )
    assert response.get_data().startswith(b"PK")
