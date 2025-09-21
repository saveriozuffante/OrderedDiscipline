"""FastAPI application exposing a QR-code splash page for easy device pairing."""

from __future__ import annotations

import base64
import os
import socket
from functools import lru_cache
from io import BytesIO

import qrcode
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

TEMPLATES = Jinja2Templates(directory="templates")

app = FastAPI(title="OrderedDiscipline Share Server", version="0.1.0")


@lru_cache(maxsize=1)
def _local_ip() -> str:
    """Return the LAN IP address that other devices can reach."""

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("1.1.1.1", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def get_share_url() -> str:
    """Resolve the URL that should appear on the splash page."""

    return os.environ.get("SHARE_URL", f"http://{_local_ip()}:8000")


@lru_cache(maxsize=32)
def qr_for_url(url: str) -> str:
    """Return a base64-encoded PNG QR code for ``url``."""

    image = qrcode.make(url)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"


def share_url_dependency() -> str:
    return get_share_url()


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request, share_url: str = Depends(share_url_dependency)) -> HTMLResponse:
    """Render the splash page with a QR code that targets the share URL."""

    qr_image = qr_for_url(share_url)
    return TEMPLATES.TemplateResponse(
        "landing.html",
        {
            "request": request,
            "share_url": share_url,
            "qr_image": qr_image,
        },
    )


@app.get("/api/info")
async def info(share_url: str = Depends(share_url_dependency)) -> JSONResponse:
    """Provide metadata that clients can query programmatically."""

    return JSONResponse({"share_url": share_url})


@app.get("/health")
async def healthcheck() -> JSONResponse:
    """Simple health-check endpoint for reverse-proxy monitoring."""

    return JSONResponse({"status": "ok"})


__all__ = ["app"]
