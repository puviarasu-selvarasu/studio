"""Tests for Studio project workspace creation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from kernel.projects import (
    ProjectWorkspaceError,
    StudioProject,
    create_project_workspace,
)


EXPECTED_DIRECTORIES = (
    "bible/story",
    "bible/characters",
    "bible/visual",
    "characters",
    "world/locations",
    "world/environments",
    "world/props",
    "episodes",
    "audio/dialogue",
    "audio/music",
    "audio/sfx",
    "audio/ambience",
    "production/director",
    "production/animation",
    "production/revisions",
    "output/previews",
    "output/frames",
    "output/renders",
    "output/final",
)


def make_project() -> StudioProject:
    return StudioProject(
        project_id="moonfall",
        title="Moonfall",
        format="anime_series",
        genres=("fantasy", "adventure", "drama"),
    )


def test_workspace_creates_expected_structure(
    tmp_path: Path,
) -> None:
    project_path = create_project_workspace(
        make_project(),
        tmp_path,
    )

    assert project_path == tmp_path / "moonfall"

    for relative_directory in EXPECTED_DIRECTORIES:
        assert (
            project_path / relative_directory
        ).is_dir()


def test_workspace_writes_project_manifest(
    tmp_path: Path,
) -> None:
    project_path = create_project_workspace(
        make_project(),
        tmp_path,
    )

    manifest = json.loads(
        (project_path / "project.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest == {
        "project_id": "moonfall",
        "title": "Moonfall",
        "format": "anime_series",
        "genres": [
            "fantasy",
            "adventure",
            "drama",
        ],
    }


def test_workspace_rejects_invalid_project(
    tmp_path: Path,
) -> None:
    project = StudioProject(
        project_id="../escape",
        title="Escape",
        format="anime_series",
    )

    with pytest.raises(
        ProjectWorkspaceError,
        match="validation failed",
    ):
        create_project_workspace(project, tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_workspace_does_not_overwrite_existing_project(
    tmp_path: Path,
) -> None:
    project = make_project()

    first_path = create_project_workspace(
        project,
        tmp_path,
    )

    marker = first_path / "do-not-delete.txt"
    marker.write_text(
        "existing production data",
        encoding="utf-8",
    )

    with pytest.raises(
        ProjectWorkspaceError,
        match="already exists",
    ):
        create_project_workspace(
            project,
            tmp_path,
        )

    assert marker.read_text(
        encoding="utf-8"
    ) == "existing production data"


def test_projects_are_isolated(
    tmp_path: Path,
) -> None:
    first = make_project()

    second = StudioProject(
        project_id="neon-district",
        title="Neon District",
        format="anime_series",
        genres=("science-fiction", "action"),
    )

    first_path = create_project_workspace(
        first,
        tmp_path,
    )

    second_path = create_project_workspace(
        second,
        tmp_path,
    )

    assert first_path != second_path
    assert first_path.name == "moonfall"
    assert second_path.name == "neon-district"

    assert (
        first_path / "project.json"
    ).is_file()

    assert (
        second_path / "project.json"
    ).is_file()