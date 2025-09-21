import importlib

import pytest
from fastapi.testclient import TestClient

import fileagent.main as main


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_ROOT", str(tmp_path))
    monkeypatch.setenv("AGENT_TOKEN", "test-token")
    importlib.reload(main)
    app = main.create_app()
    return TestClient(app)


def auth_header():
    return {"Authorization": "Bearer test-token"}


def test_path_confinement(client):
    res = client.post(
        "/v1/files",
        json={"path": "../evil.txt", "content": "bad"},
        headers=auth_header(),
    )
    assert res.status_code == 400


def test_auth_failure(client):
    res = client.post("/v1/files", json={"path": "a.txt", "content": "hi"})
    assert res.status_code == 401


def test_write_and_download(client, tmp_path):
    res = client.post(
        "/v1/files",
        json={"path": "a.txt", "content": "hi"},
        headers=auth_header(),
    )
    assert res.status_code == 200
    url = res.json()["url"]
    res = client.get(url, headers=auth_header())
    assert res.status_code == 200
    assert res.text == "hi"


def test_batch(client):
    payload = [
        {"path": "a.txt", "content": "1"},
        {"path": "b/b.txt", "content": "2"},
    ]
    res = client.post("/v1/batch", json=payload, headers=auth_header())
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_zip(client):
    client.post(
        "/v1/files",
        json={"path": "a.txt", "content": "1"},
        headers=auth_header(),
    )
    client.post(
        "/v1/files",
        json={"path": "b.txt", "content": "2"},
        headers=auth_header(),
    )
    res = client.post(
        "/v1/zip",
        json={"paths": ["a.txt", "b.txt"]},
        headers=auth_header(),
    )
    assert res.status_code == 200
    url = res.json()["url"]
    res = client.get(url, headers=auth_header())
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
