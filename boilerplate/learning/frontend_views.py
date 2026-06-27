"""Serve the static frontend HTML pages from the repo-root `frontend/` directory."""

from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse

FRONTEND_DIR = Path(settings.BASE_DIR).parent / 'frontend'

PAGE_MAP = {
    '': 'index.html',
    'login': 'login.html',
    'notes': 'notes.html',
    'panel': 'panel.html',
    'account': 'account.html',
    'logout': 'logout.html',
}


def serve_frontend_page(request, page: str = ''):
    """Return a frontend HTML page by route slug."""

    filename = PAGE_MAP.get(page.strip('/'))
    if not filename:
        raise Http404('Page not found.')

    filepath = FRONTEND_DIR / filename
    if not filepath.is_file():
        raise Http404('Page not found.')

    return FileResponse(filepath.open('rb'), content_type='text/html; charset=utf-8')


def serve_frontend_config(request):
    """Expose frontend runtime config from environment variables."""

    payload = {
        'apiBase': settings.API_BASE_URL,
        'adminUrl': settings.ADMIN_URL,
        'siteBaseUrl': settings.SITE_BASE_URL,
    }
    body = f'window.APP_CONFIG = window.APP_CONFIG || {json.dumps(payload)};\n'
    return HttpResponse(body, content_type='application/javascript; charset=utf-8')
