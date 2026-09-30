"""Validation rules for Studio animation projects."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .models import StudioProject


_PROJECT_ID_PATTERN = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
)


@dataclass(frozen=True)
class ProjectValidationError:
    """Represent one project validation failure."""

    field: str
    message: str


def validate_project(
    project: StudioProject,
) -> list[ProjectValidationError]:
    """Validate a Studio animation project."""

    errors: list[ProjectValidationError] = []

    if not project.project_id.strip():
        errors.append(
            ProjectValidationError(
                field="project_id",
                message="Project ID must not be empty.",
            )
        )
    elif not _PROJECT_ID_PATTERN.fullmatch(
        project.project_id
    ):
        errors.append(
            ProjectValidationError(
                field="project_id",
                message=(
                    "Project ID must use lowercase letters, "
                    "numbers, and single hyphens only."
                ),
            )
        )

    if not project.title.strip():
        errors.append(
            ProjectValidationError(
                field="title",
                message="Project title must not be empty.",
            )
        )

    if not project.format.strip():
        errors.append(
            ProjectValidationError(
                field="format",
                message="Project format must not be empty.",
            )
        )

    normalized_genres: set[str] = set()

    for index, genre in enumerate(project.genres):
        if not genre.strip():
            errors.append(
                ProjectValidationError(
                    field=f"genres[{index}]",
                    message="Genre must not be empty.",
                )
            )
            continue

        normalized = genre.strip().casefold()

        if normalized in normalized_genres:
            errors.append(
                ProjectValidationError(
                    field=f"genres[{index}]",
                    message=(
                        "Genres must not contain duplicates."
                    ),
                )
            )

        normalized_genres.add(normalized)

    return errors