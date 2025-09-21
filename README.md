# OrderedDiscipline – laptop ➜ phone sharing kit

This starter project bundles a FastAPI application, a QR code splash page, and optional reverse proxy / tunnelling helpers so you can share anything running on your laptop with your phone in seconds.

## Features

- 📱 **QR splash page** – just scan from your phone to open the link.
- ⚡️ **FastAPI + Uvicorn** – lightweight web server for APIs or static hosting.
- 🔐 **Caddy reverse proxy** – serve HTTPS on your LAN with an automatically trusted certificate.
- ☁️ **Cloudflared tunnel** – expose the service to the internet securely without router changes.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/run_local.sh
```

By default the app binds to `0.0.0.0:8000` and attempts to detect your LAN IP. Point your phone browser to the printed URL or just scan the QR code at `http://<laptop-ip>:8000`.

> **Tip** – override the link encoded in the QR by exporting `SHARE_URL="https://your-public-url"` before launching the server.

## Project layout

```
app/
  main.py          # FastAPI app with QR landing page
Caddyfile          # HTTPS reverse proxy (optional)
cloudflared.yml    # Sample config for a named Cloudflare Tunnel
requirements.txt   # Python dependencies
scripts/run_local.sh
templates/landing.html
```

## Running behind Caddy (HTTPS on LAN)

1. Install Caddy (`brew install caddy` on macOS).
2. Start the FastAPI server: `./scripts/run_local.sh`.
3. In a new terminal run `caddy run --config Caddyfile`.
4. On your phone visit `https://<laptop-ip>:8443` and accept the certificate once.

The bundled `Caddyfile` enables gzip/zstd compression and enforces HSTS for good defaults.

## Cloudflare Tunnel (public URL without port-forwarding)

1. Install cloudflared (`brew install cloudflared`).
2. With the FastAPI server running, launch an ad-hoc tunnel:
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```
   The CLI prints a `https://trycloudflare.com` URL. Export this as `SHARE_URL` so the QR code directs phones to the public address:
   ```bash
   SHARE_URL="https://<random>.trycloudflare.com" ./scripts/run_local.sh
   ```
3. For repeatable tunnels using your own hostname, log into Cloudflare, create a named tunnel, and adapt the sample `cloudflared.yml`.

## ngrok alternative

```bash
brew install ngrok
ngrok config add-authtoken <YOUR_TOKEN>
ngrok http 8000
```

Use `SHARE_URL=$(ngrok url https) ./scripts/run_local.sh` if you want the QR page to point at the ngrok domain automatically.

## Health check & API

- `GET /` – HTML landing page with QR code
- `GET /api/info` – returns `{ "share_url": "..." }`
- `GET /health` – simple JSON health indicator for monitoring

## Security checklist

- Only bind to `0.0.0.0` on trusted networks.
- Prefer Cloudflare Tunnel or ngrok over router port-forwarding.
- Protect any sensitive routes with auth (Basic, OAuth, JWT, etc.).
- Keep dependencies patched (`pip install --upgrade -r requirements.txt`).

## License

[CC0 1.0](LICENSE)
