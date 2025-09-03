import os
from pathlib import Path
from typing import List
from uuid import uuid4
import zipfile

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

AGENT_TOKEN = os.getenv("AGENT_TOKEN", "dev-token")
AGENT_ROOT = Path(os.getenv("AGENT_ROOT", "./workspace")).resolve()
AGENT_ROOT.mkdir(parents=True, exist_ok=True)


def verify_token(authorization: str = Header(...)) -> None:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != AGENT_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


def resolve_path(rel: str) -> Path:
    rel = rel.lstrip("/")
    candidate = (AGENT_ROOT / rel).resolve()
    if AGENT_ROOT not in candidate.parents and candidate != AGENT_ROOT:
        raise HTTPException(status_code=400, detail="Invalid path")
    return candidate


class FileSpec(BaseModel):
    path: str
    content: str
    executable: bool = False


class ZipSpec(BaseModel):
    paths: List[str]


app = FastAPI(title="FileAgent")


def write_file(spec: FileSpec) -> dict:
    path = resolve_path(spec.path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(spec.content)
    if spec.executable:
        path.chmod(path.stat().st_mode | 0o111)
    rel = path.relative_to(AGENT_ROOT)
    return {"path": str(path), "url": f"/v1/download?path={rel}"}


@app.post("/v1/files")
def create_file(spec: FileSpec, _: None = Depends(verify_token)) -> dict:
    return write_file(spec)


@app.post("/v1/batch")
def create_batch(specs: List[FileSpec], _: None = Depends(verify_token)) -> List[dict]:
    return [write_file(s) for s in specs]


@app.get("/v1/download")
def download(path: str = Query(...), _: None = Depends(verify_token)) -> FileResponse:
    file_path = resolve_path(path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(file_path)


@app.post("/v1/zip")
def create_zip(spec: ZipSpec, _: None = Depends(verify_token)) -> dict:
    bundle = AGENT_ROOT / f"bundle-{uuid4().hex}.zip"
    with zipfile.ZipFile(bundle, "w") as z:
        for rel in spec.paths:
            file_path = resolve_path(rel)
            if not file_path.is_file():
                raise HTTPException(status_code=400, detail=f"Missing file: {rel}")
            z.write(file_path, arcname=Path(rel).name)
    rel = bundle.relative_to(AGENT_ROOT)
    return {"path": str(bundle), "url": f"/v1/download?path={rel}"}


def create_app() -> FastAPI:
    return app
