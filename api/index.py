"""Vercel serverless function adapter for the Django backend.

This file is the entry point for Vercel's Python serverless functions.
It exposes the Django WSGI application so API routes under /api/ can be
served from the same Vercel deployment as the React frontend.

Note: Vercel serverless functions have cold-start and package-size limits.
For production workloads with heavy ML models, prefer a dedicated host.
"""

import os
from pathlib import Path

# Add the backend directory to the path so Django settings can be imported.
BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import sys

sys.path.insert(0, str(BASE_DIR / "backend"))

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()


def handler(request, response):
    """Vercel serverless function handler.

    Args:
        request: Vercel request object.
        response: Vercel response builder.

    Returns:
        WSGI response through the Django application.
    """
    from vercel_wsgi import handle_wsgi

    return handle_wsgi(application, request)
