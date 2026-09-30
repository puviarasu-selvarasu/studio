"""Execute validated Studio Animation IR inside Blender.

No LLM runs inside Blender. This module receives JSON data only and maps
validated semantic actions to Studio-owned deterministic Blender functions.
"""

from __future__ import annotations

import json
import sys
from math import floor
from pathlib import Path
from typing import Any

import bpy


PROJECT_ROOT = Path(__file__).resolve().parents[4]
KERNEL_ROOT = PROJECT_ROOT / "studio_kernel"

for bootstrap_path in (
    PROJECT_ROOT,
    KERNEL_ROOT,
):
    bootstrap_text = str(
        bootstrap_path
    )

    if bootstrap_text not in sys.path:
        sys.path.insert(
            0,
            bootstrap_text,
        )


from kernel.animation_ir.models import (
    AnimationAction,
    AnimationScene,
    CharacterAnimation,
)
from kernel.adapters.blender.semantic_dispatcher import (
    compile_animation_scene,
    execute_animation_scene,
)
from kernel.adapters.blender.deterministic_shot import (
    clear_scene,
    configure_render,
    create_camera,
    create_debug_body,
    create_ground,
)
from kernel.adapters.blender.humanoid_rig import (
    create_humanoid_armature,
)
from kernel.adapters.blender.toolkit_level0 import (
    configure_timeline,
    set_location,
)


RIG_NAME = "StudioShotRig"

START_FRAME = 1
FPS = 24

PREVIEW_FPS = 12
PREVIEW_FRAME_STEP = FPS // PREVIEW_FPS


def parse_arguments() -> tuple[Path, Path, Path]:
    """Read trusted paths passed after Blender's -- separator."""

    if "--" not in sys.argv:
        raise RuntimeError(
            "Studio AI-shot arguments were not supplied."
        )

    args = sys.argv[
        sys.argv.index("--") + 1 :
    ]

    if len(args) != 3:
        raise RuntimeError(
            "Expected blend path, preview path and Animation IR path."
        )

    return (
        Path(args[0]).resolve(),
        Path(args[1]).resolve(),
        Path(args[2]).resolve(),
    )


def _mapping(
    value: object,
    *,
    label: str,
) -> dict[str, Any]:
    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            f"{label} must be an object."
        )

    return value


def _exact_keys(
    value: dict[str, Any],
    *,
    keys: set[str],
    label: str,
) -> None:
    if set(value) != keys:
        raise RuntimeError(
            f"{label} contains unsupported fields."
        )


def _text(
    value: object,
    *,
    label: str,
) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        raise RuntimeError(
            f"{label} must be a non-empty string."
        )

    return value


def _number(
    value: object,
    *,
    label: str,
) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(
            value,
            (
                int,
                float,
            ),
        )
    ):
        raise RuntimeError(
            f"{label} must be numeric."
        )

    return float(
        value
    )


def load_animation_scene(
    ir_path: Path,
) -> AnimationScene:
    """Reconstruct the narrow trusted AnimationScene JSON contract."""

    try:
        raw = json.loads(
            ir_path.read_text(
                encoding="utf-8"
            )
        )
    except (
        OSError,
        json.JSONDecodeError,
    ) as exc:
        raise RuntimeError(
            f"Unable to load Animation IR: {exc}"
        ) from exc

    root = _mapping(
        raw,
        label="Animation IR",
    )

    _exact_keys(
        root,
        keys={
            "scene_id",
            "duration_seconds",
            "characters",
        },
        label="Animation IR",
    )

    raw_characters = root[
        "characters"
    ]

    if not isinstance(
        raw_characters,
        list,
    ):
        raise RuntimeError(
            "characters must be an array."
        )

    characters: list[
        CharacterAnimation
    ] = []

    for character_index, raw_character in enumerate(
        raw_characters
    ):
        character = _mapping(
            raw_character,
            label=(
                f"characters[{character_index}]"
            ),
        )

        _exact_keys(
            character,
            keys={
                "character_id",
                "actions",
            },
            label=(
                f"characters[{character_index}]"
            ),
        )

        raw_actions = character[
            "actions"
        ]

        if not isinstance(
            raw_actions,
            list,
        ):
            raise RuntimeError(
                "actions must be an array."
            )

        actions: list[
            AnimationAction
        ] = []

        for action_index, raw_action in enumerate(
            raw_actions
        ):
            action = _mapping(
                raw_action,
                label=(
                    f"actions[{action_index}]"
                ),
            )

            _exact_keys(
                action,
                keys={
                    "action",
                    "start_seconds",
                    "duration_seconds",
                },
                label=(
                    f"actions[{action_index}]"
                ),
            )

            actions.append(
                AnimationAction(
                    action=_text(
                        action["action"],
                        label="action",
                    ),
                    start_seconds=_number(
                        action["start_seconds"],
                        label="start_seconds",
                    ),
                    duration_seconds=_number(
                        action["duration_seconds"],
                        label="duration_seconds",
                    ),
                )
            )

        characters.append(
            CharacterAnimation(
                character_id=_text(
                    character["character_id"],
                    label="character_id",
                ),
                actions=tuple(
                    actions
                ),
            )
        )

    scene = AnimationScene(
        scene_id=_text(
            root["scene_id"],
            label="scene_id",
        ),
        duration_seconds=_number(
            root["duration_seconds"],
            label="duration_seconds",
        ),
        characters=tuple(
            characters
        ),
    )

    compile_animation_scene(
        scene,
        fps=FPS,
    )

    return scene


def timeline_end_frame(
    scene: AnimationScene,
) -> int:
    """Return the inclusive final frame for the shot."""

    return max(
        1,
        floor(
            scene.duration_seconds
            * FPS
            + 0.5
        ),
    )


def render_preview_frames(
    frames_directory: Path,
    *,
    end_frame: int,
) -> int:
    """Render the hardware-safe 12fps engineering sequence."""

    frames_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    scene = bpy.context.scene

    count = 0

    for frame in range(
        START_FRAME,
        end_frame + 1,
        PREVIEW_FRAME_STEP,
    ):
        scene.frame_set(
            frame
        )

        scene.render.filepath = str(
            frames_directory
            / f"frame_{count:04d}.png"
        )

        bpy.ops.render.render(
            write_still=True
        )

        count += 1

    return count


def build_ai_shot(
    animation_scene: AnimationScene,
) -> tuple[int, tuple[object, ...]]:
    """Build the rig and execute only trusted semantic actions."""

    end_frame = timeline_end_frame(
        animation_scene
    )

    configure_timeline(
        start_frame=START_FRAME,
        end_frame=end_frame,
        fps=FPS,
    )

    create_ground()
    create_camera()

    rig = create_humanoid_armature(
        RIG_NAME
    )

    create_debug_body(
        rig
    )

    set_location(
        RIG_NAME,
        (
            0.0,
            0.0,
            0.0,
        ),
    )

    commands = execute_animation_scene(
        animation_scene,
        armature_name=RIG_NAME,
        fps=FPS,
    )

    return (
        end_frame,
        commands,
    )


def main() -> None:
    """Create and render an AI-planned Studio engineering shot."""

    (
        blend_path,
        preview_path,
        ir_path,
    ) = parse_arguments()

    blend_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    animation_scene = load_animation_scene(
        ir_path
    )

    clear_scene()

    (
        end_frame,
        commands,
    ) = build_ai_shot(
        animation_scene
    )

    configure_render(
        preview_path
    )

    bpy.context.scene.frame_set(
        end_frame
    )

    bpy.context.view_layer.update()

    bpy.ops.wm.save_as_mainfile(
        filepath=str(
            blend_path
        )
    )

    bpy.ops.render.render(
        write_still=True
    )

    frames_directory = (
        preview_path.parent
        / "frames"
    )

    frame_count = render_preview_frames(
        frames_directory,
        end_frame=end_frame,
    )

    print("STUDIO_AI_SHOT_OK")
    print("STUDIO_AI_IR_EXECUTED_OK")

    print(
        f"STUDIO_PREVIEW_FRAME_COUNT="
        f"{frame_count}"
    )

    print(
        f"STUDIO_PREVIEW_FPS="
        f"{PREVIEW_FPS}"
    )

    print(
        f"STUDIO_TIMELINE="
        f"{START_FRAME}:{end_frame}:{FPS}"
    )

    print(
        "STUDIO_ACTIONS="
        + ",".join(
            command.action
            for command in commands
        )
    )

    print(
        f"STUDIO_BLEND_PATH="
        f"{blend_path}"
    )

    print(
        f"STUDIO_PREVIEW_PATH="
        f"{preview_path}"
    )

    print(
        f"STUDIO_PREVIEW_FRAMES_DIR="
        f"{frames_directory}"
    )


if __name__ == "__main__":
    main()
