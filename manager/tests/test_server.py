from fastapi.testclient import TestClient

from workstation_manager.server.app import create_app

from .test_core import workspace  # noqa: F401


def test_api(workspace):  # noqa: F811
    client = TestClient(create_app(workspace))
    assert {a["id"] for a in client.get("/api/applications").json()} >= {"claude-code"}
    assert client.get("/api/applications/claude-code").json()["folder"] == "ai/claude"
    assert client.get("/api/applications/nope").status_code == 404
    assert client.get("/api/applications/jq/files/../../profiles/dev.yaml").status_code == 404
    assert client.get("/api/profiles").json() == ["dev"]

    response = client.put("/api/profiles/dev", json={"selected": ["claude-code"]})
    assert response.json()["implied"] == ["jq"]
    assert response.json()["inline"][0]["label"] == "VSCode"
    assert client.put("/api/profiles/dev", json={"selected": ["nope"]}).status_code == 422
