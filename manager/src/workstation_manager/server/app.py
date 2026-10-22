from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

from ..core import (
    EDITABLE_FLAGS,
    Application,
    CatalogError,
    ProfileError,
    ProfileState,
    Workspace,
    set_flag,
)
from ..core.runs import clean_output, list_runs, load_run, output_file
from ..core.state import default_state_dir


class ApplicationSummary(BaseModel):
    id: str
    name: str
    kind: str
    description: str
    tags: list[str]
    dependencies: list[str]
    homepage: str | None
    fundamental: bool
    deprecated: bool
    archived: bool
    trial: bool
    order: int
    folder: str


class StepView(BaseModel):
    file: str
    kind: str


class ApplicationDetail(ApplicationSummary):
    readme: str
    steps: list[StepView]
    files: list[str]


class InlineEntryView(BaseModel):
    label: str
    data: dict


class ProfileView(BaseModel):
    name: str
    fundamentals: list[str]
    selected: list[str]
    implied: list[str]
    missing: list[str]
    inline: list[InlineEntryView]
    install_order: list[str]


class SavedSearchView(BaseModel):
    name: str
    query: str
    builtin: bool


class SettingsView(BaseModel):
    searches: list[SavedSearchView]


class FlagsUpdate(BaseModel):
    deprecated: bool | None = None
    archived: bool | None = None


class SelectionUpdate(BaseModel):
    selected: list[str]


def _hidden(path: Path) -> bool:
    return any(part.startswith(".") or part == "__pycache__" for part in path.parts)


def create_app(
    workspace: Workspace, static_dir: Path | None = None, state_dir: Path | None = None
) -> FastAPI:
    app = FastAPI(title="Workstation Manager")
    state_dir = state_dir or default_state_dir()

    def summary(application: Application) -> ApplicationSummary:
        return ApplicationSummary(
            id=application.id,
            name=application.name,
            kind=application.kind,
            description=application.description,
            tags=list(application.tags),
            dependencies=list(application.dependencies),
            homepage=application.homepage,
            fundamental=application.fundamental,
            deprecated=application.deprecated,
            archived=application.archived,
            trial=application.trial,
            order=application.order,
            folder=str(application.path.relative_to(workspace.applications_dir)),
        )

    def profile_view(state: ProfileState) -> ProfileView:
        return ProfileView(
            name=state.profile.name,
            fundamentals=state.fundamentals,
            selected=state.selected,
            implied=state.implied,
            missing=state.missing,
            inline=[
                InlineEntryView(label=e.label, data=e.data)
                for e in state.profile.inline
            ],
            install_order=state.install_order,
        )

    def get_application(id: str) -> Application:
        catalog = workspace.catalog()
        if id not in catalog:
            raise HTTPException(404, f"Unknown application id '{id}'")
        return catalog.get(id)

    @app.exception_handler(CatalogError)
    async def catalog_error(_, e: CatalogError) -> JSONResponse:
        return JSONResponse({"detail": str(e)}, status_code=500)

    @app.get("/api/applications")
    def applications() -> list[ApplicationSummary]:
        return [summary(a) for a in workspace.catalog()]

    @app.get("/api/applications/{id}")
    def application(id: str) -> ApplicationDetail:
        application = get_application(id)
        files = sorted(
            str(p.relative_to(application.path))
            for p in application.path.rglob("*")
            if p.is_file() and not _hidden(p.relative_to(application.path))
        )
        return ApplicationDetail(
            **summary(application).model_dump(),
            readme=application.body,
            steps=[StepView(file=s.file, kind=s.kind) for s in application.steps],
            files=files,
        )

    @app.patch("/api/applications/{id}")
    def update_flags(id: str, update: FlagsUpdate) -> ApplicationSummary:
        readme = get_application(id).path / "README.md"
        for flag in EDITABLE_FLAGS:
            value = getattr(update, flag)
            if value is not None:
                set_flag(readme, flag, value)
        return summary(workspace.catalog().get(id))

    @app.get("/api/applications/{id}/files/{path:path}")
    def application_file(id: str, path: str) -> FileResponse:
        root = get_application(id).path.resolve()
        file = (root / path).resolve()
        if not file.is_relative_to(root) or not file.is_file():
            raise HTTPException(404, f"No file '{path}' in '{id}'")
        return FileResponse(file)

    @app.get("/api/settings")
    def settings() -> SettingsView:
        return SettingsView(
            searches=[
                SavedSearchView(name=s.name, query=s.query, builtin=s.builtin)
                for s in workspace.settings().searches
            ]
        )

    @app.get("/api/runs")
    def runs() -> list[dict]:
        """Run summaries, latest first; steps are left out."""
        return [{k: v for k, v in run.items() if k != "steps"} for run in list_runs(state_dir)]

    @app.get("/api/runs/{id}")
    def run(id: str) -> dict:
        found = load_run(state_dir, id)
        if found is None:
            raise HTTPException(404, f"Unknown run '{id}'")
        return found

    @app.get("/api/runs/{id}/output/{name}")
    def run_output(id: str, name: str) -> PlainTextResponse:
        file = output_file(state_dir, id, name)
        if file is None:
            raise HTTPException(404, f"No output '{name}' in run '{id}'")
        return PlainTextResponse(clean_output(file.read_bytes()))

    @app.get("/api/applications/{id}/history")
    def application_history(id: str) -> list[dict]:
        """This application's executed steps across runs, latest run first."""
        get_application(id)
        return [
            {**step, "run": run["id"]}
            for run in list_runs(state_dir)
            for step in run["steps"]
            if step["app"] == id
        ]

    @app.get("/api/profiles")
    def profiles() -> list[str]:
        return workspace.profiles()

    @app.get("/api/profiles/{name}")
    def profile(name: str) -> ProfileView:
        try:
            return profile_view(workspace.state(name))
        except ProfileError as e:
            raise HTTPException(404, str(e)) from None

    @app.put("/api/profiles/{name}")
    def update_profile(name: str, update: SelectionUpdate) -> ProfileView:
        try:
            return profile_view(workspace.update_selection(name, update.selected))
        except ProfileError as e:
            raise HTTPException(404, str(e)) from None
        except CatalogError as e:
            raise HTTPException(422, str(e)) from None

    if static_dir and static_dir.is_dir():
        index = static_dir / "index.html"

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str) -> FileResponse:
            file = (static_dir / path).resolve()
            if path and file.is_relative_to(static_dir.resolve()) and file.is_file():
                return FileResponse(file)
            return FileResponse(index)

    return app
