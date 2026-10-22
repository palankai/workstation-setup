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
    assert client.get("/api/settings").json()["searches"][0]["query"] == "is:fundamental"

    response = client.put("/api/profiles/dev", json={"selected": ["claude-code"]})
    assert response.json()["implied"] == ["jq"]
    assert response.json()["inline"][0]["label"] == "VSCode"
    assert client.put("/api/profiles/dev", json={"selected": ["nope"]}).status_code == 422

    response = client.patch("/api/applications/jq", json={"deprecated": True})
    assert (response.json()["deprecated"], response.json()["archived"]) == (True, False)
    assert client.patch("/api/applications/jq", json={"deprecated": False}).json()["deprecated"] is False


def test_runs_api(workspace, tmp_path):  # noqa: F811
    from workstation_manager.core.runs import RUNS, RunLog, StepResult

    log = RunLog(tmp_path / "state" / RUNS, "dev", ["jq"])
    output = log.output_path("jq", "10-run.sh")
    output.write_bytes(b"\x1b[1mhello\x1b[0m\n")
    log.add(StepResult("jq", "10-run.sh", "run", "ok", "t0", "t1", 0, output.name))
    log.finish("ok")

    client = TestClient(create_app(workspace, state_dir=tmp_path / "state"))
    assert [r["id"] for r in client.get("/api/runs").json()] == [log.id]
    assert client.get(f"/api/runs/{log.id}").json()["steps"][0]["app"] == "jq"
    assert client.get(f"/api/runs/{log.id}/output/{output.name}").text == "hello\n"
    assert client.get(f"/api/runs/{log.id}/output/..%2Frun.json").status_code == 404
    history = client.get("/api/applications/jq/history").json()
    assert [(h["run"], h["step"]) for h in history] == [(log.id, "10-run.sh")]
    assert client.get("/api/applications/bat/history").json() == []
