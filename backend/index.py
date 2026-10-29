"""Vercel Python entrypoint.

Vercel looks for a top-level ``app`` object in a recognised file. The local
``app.py`` cannot be imported as a module because ``app`` is also the backend
package name, so this thin entrypoint exposes the WSGI application instead.
"""

from app.factory import create_app

app = create_app()
