from app.factory import create_app


def test_email_templates_are_available_to_backend_function():
    app = create_app()
    template_names = (
        "email/base.html",
        "email/dispute_status.html",
        "email/fine_issued.html",
        "email/fine_notification.html",
        "email/password_reset.html",
        "email/payment_receipt.html",
        "email/welcome.html",
    )

    with app.app_context():
        for name in template_names:
            app.jinja_env.get_template(name)

        rendered = app.jinja_env.get_template("email/base.html").render(
            title="Test",
            message="Test message",
        )

    assert "Test message" in rendered
