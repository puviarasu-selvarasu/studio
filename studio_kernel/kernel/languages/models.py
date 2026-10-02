"""Pure Studio spoken-language identities."""

from __future__ import annotations

from dataclasses import dataclass


class LanguageDomainError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class LanguageIdentity:
    language_code: str
    name: str
    native_name: str
    script: str

    def __post_init__(
        self,
    ) -> None:
        for field in (
            "language_code",
            "name",
            "native_name",
            "script",
        ):
            value = getattr(
                self,
                field,
            )

            if (
                not isinstance(
                    value,
                    str,
                )
                or not value.strip()
            ):
                raise LanguageDomainError(
                    field
                    + " must not be blank."
                )

            object.__setattr__(
                self,
                field,
                value.strip(),
            )
