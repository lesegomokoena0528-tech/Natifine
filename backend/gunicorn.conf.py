"""Gunicorn configuration for the NatiFine SA API (Render).

Run locally (Linux/WSL) / production:
    gunicorn -c gunicorn.conf.py "app.factory:create_app()"
"""

import multiprocessing
import os

# Render assigns the port through the PORT environment variable.
bind = "0.0.0.0:" + os.getenv("PORT", "5000")

# Project is a small academic API; cap workers to stay within
# Render's smaller instance memory limits.
workers = int(os.getenv("WEB_CONCURRENCY", str(min(multiprocessing.cpu_count() * 2 + 1, 4))))

worker_class = "sync"
threads = int(os.getenv("GUNICORN_THREADS", "2"))

# Receipt PDF generation can be slow; allow generous request timeouts.
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
graceful_timeout = 30
keepalive = 5

# Log to stdout/stderr so Render captures them.
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# Trust Render's proxy headers for correct client IPs / scheme.
forwarded_allow_ips = "*"
