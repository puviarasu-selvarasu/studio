"""Filesystem workspace management for Studio projects."""

from __future__ import annotations

import json
from pathlib import Path

from .models import StudioProject
from .validator import validate_project


class ProjectWorkspaceError(Exception):
    """Represent a failure while creating a project workspace."""


_WORKSPACE_DIRECTORIES = (
    "bible",
    "bible/story",
    "bible/characters",
    "bible/visual",
    "characters",
    "world",
    "world/locations",
    "world/environments",
    "world/props",
    "episodes",
    "audio",
    "audio/dialogue",
    "audio/music",
    "audio/sfx",
    "audio/ambience",
    "production",
    "production/director",
    "production/animation",
    "production/revisions",
    "output",
    "output/previews",
    "output/frames",
    "output/renders",
    "output/final",
)


def create_project_workspace(
    project: StudioProject,
    projects_root: Path,
) -> Path:
    """Create an isolated filesystem workspace for a project."""

    validation_errors = validate_project(project)

    if validation_errors:
        details = "; ".join(
            f"{error.field}: {error.message}"
            for error in validation_errors
        )
        raise ProjectWorkspaceError(
            f"Project validation failed: {details}"
        )

    root = projects_root.resolve()
    project_path = (root / project.project_id).resolve()

    try:
        project_path.relative_to(root)
    except ValueError as exc:
        raise ProjectWorkspaceError(
            "Project path escapes the projects root."
        ) from exc

    if project_path.exists():
        raise ProjectWorkspaceError(
            f"Project workspace already exists: "
            f"{project.project_id}"
        )

    try:
        project_path.mkdir(parents=True, exist_ok=False)

        for relative_directory in _WORKSPACE_DIRECTORIES:
            (project_path / relative_directory).mkdir(
                parents=True,
                exist_ok=False,
            )

        manifest_path = project_path / "project.json"

        manifest = {
            "project_id": project.project_id,
            "title": project.title,
            "format": project.format,
            "genres": list(project.genres),
        }

        manifest_path.write_text(
            json.dumps(
                manifest,
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise ProjectWorkspaceError(
            f"Could not create project workspace: {exc}"
        ) from exc

    return project_path