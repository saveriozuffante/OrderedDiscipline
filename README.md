# FileAgent

FastAPI microservice that writes files to a confined root and serves them back.

## Environment
- `AGENT_ROOT` (default `./workspace`)
- `AGENT_TOKEN` (default `dev-token`)
- `PORT` (default `8787`)

## Run
```bash
export AGENT_TOKEN=dev-token
uvicorn fileagent.main:create_app --factory --host 0.0.0.0 --port ${PORT:-8787}
```

## Docker
```bash
docker build -t fileagent .
docker run -p 8787:8787 -e AGENT_TOKEN=dev-token fileagent
```

## Docker compose
`compose.yaml`
```yaml
services:
  fileagent:
    build: .
    ports: ["8787:8787"]
    environment:
      AGENT_TOKEN: dev-token
    volumes:
      - ./workspace:/workspace
```
Run with `docker compose up`.

## API
Bearer token auth for all requests.

### POST /v1/files
```bash
curl -X POST localhost:8787/v1/files \
 -H "Authorization: Bearer dev-token" \
 -H "Content-Type: application/json" \
 -d '{"path":"hi.txt","content":"hello"}'
```
Python helper:
```python
import requests
TOKEN = "dev-token"
res = requests.post(
    "http://localhost:8787/v1/files",
    json={"path": "hi.txt", "content": "hello"},
    headers={"Authorization": f"Bearer {TOKEN}"},
)
print(res.json())
```

### POST /v1/batch
Create many files at once.

### GET /v1/download
`curl -H "Authorization: Bearer dev-token" "http://localhost:8787/v1/download?path=hi.txt"`

### POST /v1/zip
Bundle existing files.
```bash
curl -X POST localhost:8787/v1/zip \
 -H "Authorization: Bearer dev-token" \
 -H "Content-Type: application/json" \
 -d '{"paths":["hi.txt"]}'
```

## Jupyter/Juno
```python
import requests
TOKEN="dev-token"
res = requests.post(
    "http://localhost:8787/v1/files",
    json={"path":"note.txt","content":"hello"},
    headers={"Authorization":f"Bearer {TOKEN}"},
)
text = requests.get(
    "http://localhost:8787" + res.json()["url"],
    headers={"Authorization":f"Bearer {TOKEN}"},
).text
print(text)
```

## Tests
`pytest`

## CI
GitHub Actions builds multi-arch images and pushes to `ghcr.io` on each push.
