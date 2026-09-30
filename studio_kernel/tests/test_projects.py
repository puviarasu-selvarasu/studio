"""Tests for the Studio animation project domain."""

from __future__ import annotations

from kernel.projects import StudioProject, validate_project


def test_valid_animation_project_has_no_errors() -> None:
    project = StudioProject(
        project_id="moonfall",
        title="Moonfall",
        format="anime_series",
        genres=("fantasy", "adventure", "drama"),
    )

    assert validate_project(project) == []


def test_required_project_fields_are_validated() -> None:
    project = StudioProject(
        project_id="",
        title="",
        format="",
    )

    errors = validate_project(project)
    fields = {error.field for error in errors}

    assert "project_id" in fields
    assert "title" in fields
    assert "format" in fields


def test_project_id_must_be_filesystem_safe_slug() -> None:
    invalid_ids = (
        "Moonfall",
        "moon fall",
        "../moonfall",
        "moonfall/",
        "moonfall_01",
        "-moonfall",
        "moonfall-",
        "moonfall--series",
    )

    for project_id in invalid_ids:
        project = StudioProject(
            project_id=project_id,
            title="Moonfall",
            format="anime_series",
        )

        errors = validate_project(project)

        assert any(
            error.field == "project_id"
            for error in errors
        )


def test_duplicate_genres_are_rejected_case_insensitively() -> None:
    project = StudioProject(
        project_id="moonfall",
        title="Moonfall",
        format="anime_series",
        genres=("Fantasy", "fantasy"),
    )

    errors = validate_project(project)

    assert any(
        error.field == "genres[1]"
        for error in errors
    )


def test_empty_genre_is_rejected() -> None:
    project = StudioProject(
        project_id="moonfall",
        title="Moonfall",
        format="anime_series",
        genres=("fantasy", ""),
    )

    errors = validate_project(project)

    assert any(
        error.field == "genres[1]"
        for error in errors
    )