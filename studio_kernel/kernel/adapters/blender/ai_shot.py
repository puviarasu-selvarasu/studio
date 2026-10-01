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
from kernel.adapters.blender.camera_direction import (
    CameraDirectionCommand,
    compile_camera_direction,
)
from kernel.adapters.blender.character_builder import (
    build_character,
)
from kernel.adapters.blender.semantic_dispatcher import (
    compile_animation_scene,
    execute_animation_scene,
)
from kernel.characters.production import (
    CHARACTER_PRODUCTION_FILENAME,
    CharacterProductionSpec,
    CharacterProductionSpecError,
    character_production_from_json,
)
from kernel.adapters.blender.deterministic_shot import (
    clear_scene,
    create_camera,
    create_ground,
)
from kernel.adapters.blender.toolkit_level0 import (
    configure_timeline,
    insert_transform_keyframe,
    point_camera_at,
    set_location,
)
from kernel.adapters.blender.visual_style_executor import (
    apply_anime_camera_presentation,
    apply_anime_cel_v1,
    apply_bold_ink_outline,
    apply_warm_key_cool_fill,
    configure_clean_cel_compositor,
    configure_workbench_cel_preview,
    create_layered_2_5d_background,
)
from kernel.visual_style import (
    ANIME_CEL_V1,
)


RIG_NAME = "StudioShotRig"

START_FRAME = 1
FPS = 24

PREVIEW_FPS = 12
PREVIEW_FRAME_STEP = FPS // PREVIEW_FPS


DIRECTOR_TO_STYLE_FRAMING = {
    "wide": "wide_establishing",
    "medium": "medium_hero",
    "close_up": "close_intense",
}


def parse_arguments(
) -> tuple[
    Path,
    Path,
    Path,
    Path | None,
]:
    """Read trusted paths passed after Blender's -- separator."""

    if "--" not in sys.argv:
        raise RuntimeError(
            "Studio AI-shot arguments were not supplied."
        )

    args = sys.argv[
        sys.argv.index("--") + 1 :
    ]

    if len(args) not in {
        3,
        4,
    }:
        raise RuntimeError(
            "Expected blend path, preview path, Animation IR path "
            "and optional Director camera plan path."
        )

    camera_plan_path = (
        Path(args[3]).resolve()
        if len(args) == 4
        else None
    )

    return (
        Path(args[0]).resolve(),
        Path(args[1]).resolve(),
        Path(args[2]).resolve(),
        camera_plan_path,
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


def load_character_production(
    production_path: Path,
) -> CharacterProductionSpec:
    """Load one separately bound trusted character-production contract."""

    try:
        raw_json = production_path.read_text(
            encoding="utf-8"
        )
    except OSError as exc:
        raise RuntimeError(
            "Unable to read character production contract: "
            + str(exc)
        ) from exc

    try:
        return character_production_from_json(
            raw_json
        )
    except CharacterProductionSpecError as exc:
        raise RuntimeError(
            "Invalid character production contract: "
            + str(exc)
        ) from exc


def validate_character_production_binding(
    animation_scene: AnimationScene,
    production_spec: CharacterProductionSpec,
) -> None:
    """Bind production identity to Animation IR without expanding the IR."""

    if len(
        animation_scene.characters
    ) != 1:
        raise RuntimeError(
            "AI shot requires exactly one character "
            "for character-production binding."
        )

    animation_character = (
        animation_scene.characters[0]
    )

    if (
        animation_character.character_id
        != production_spec.character_id
    ):
        raise RuntimeError(
            "Character production ID does not match "
            "Animation IR character ID."
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


def load_director_camera_plan(
    camera_plan_path: Path,
    animation_scene: AnimationScene,
) -> tuple[
    str,
    str,
    str,
]:
    """Load a narrow request-bound Director camera plan."""

    try:
        raw = json.loads(
            camera_plan_path.read_text(
                encoding="utf-8"
            )
        )
    except (
        OSError,
        json.JSONDecodeError,
    ) as exc:
        raise RuntimeError(
            f"Unable to load Director camera plan: {exc}"
        ) from exc

    root = _mapping(
        raw,
        label="Director camera plan",
    )

    _exact_keys(
        root,
        keys={
            "scene_id",
            "duration_seconds",
            "shot",
        },
        label="Director camera plan",
    )

    scene_id = _text(
        root["scene_id"],
        label="Director camera plan scene_id",
    )

    duration_seconds = _number(
        root["duration_seconds"],
        label="Director camera plan duration_seconds",
    )

    if scene_id != animation_scene.scene_id:
        raise RuntimeError(
            "Director camera plan scene ID does not match "
            "Animation IR."
        )

    if duration_seconds != animation_scene.duration_seconds:
        raise RuntimeError(
            "Director camera plan duration does not match "
            "Animation IR."
        )

    shot = _mapping(
        root["shot"],
        label="Director camera plan shot",
    )

    _exact_keys(
        shot,
        keys={
            "framing",
            "camera_intent",
            "pacing",
        },
        label="Director camera plan shot",
    )

    return (
        _text(
            shot["framing"],
            label="Director camera framing",
        ),
        _text(
            shot["camera_intent"],
            label="Director camera intent",
        ),
        _text(
            shot["pacing"],
            label="Director camera pacing",
        ),
    )


def apply_camera_direction(
    *,
    camera_name: str,
    command: CameraDirectionCommand,
) -> None:
    """Apply only a trusted compiled camera command."""

    set_location(
        camera_name,
        command.start_location,
    )

    point_camera_at(
        camera_name,
        command.start_target,
    )

    insert_transform_keyframe(
        camera_name,
        command.start_frame,
        channels=(
            "location",
            "rotation_euler",
        ),
    )

    if command.end_frame > command.start_frame:
        set_location(
            camera_name,
            command.end_location,
        )

        point_camera_at(
            camera_name,
            command.end_target,
        )

        insert_transform_keyframe(
            camera_name,
            command.end_frame,
            channels=(
                "location",
                "rotation_euler",
            ),
        )


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


def style_camera_framing(
    camera_plan: tuple[
        str,
        str,
        str,
    ] | None,
) -> str:
    """Map bounded Director framing into bounded Visual Style framing."""

    if camera_plan is None:
        return "medium_hero"

    framing = camera_plan[0]

    try:
        return DIRECTOR_TO_STYLE_FRAMING[
            framing
        ]
    except KeyError as exc:
        raise RuntimeError(
            "Unsupported Director framing for visual style: "
            + framing
        ) from exc


def retarget_camera_for_character(
    command: CameraDirectionCommand,
    production_spec: CharacterProductionSpec,
) -> CameraDirectionCommand:
    """Retarget bounded camera framing to a production-character focus anchor."""

    if (
        production_spec.production_profile_id
        != "momo_default_v1"
    ):
        return command

    focus_heights = {
        "wide": 1.25,
        "medium": 1.90,
        "close_up": 2.65,
    }

    try:
        focus_height = focus_heights[
            command.framing
        ]
    except KeyError as exc:
        raise RuntimeError(
            "Unsupported production-character framing: "
            + command.framing
        ) from exc

    start_target = (
        command.start_target[0],
        command.start_target[1],
        focus_height,
    )

    end_target = (
        command.end_target[0],
        command.end_target[1],
        focus_height,
    )

    return CameraDirectionCommand(
        framing=command.framing,
        camera_intent=command.camera_intent,
        pacing=command.pacing,
        start_location=command.start_location,
        end_location=command.end_location,
        start_target=start_target,
        end_target=end_target,
        start_frame=command.start_frame,
        end_frame=command.end_frame,
    )


def build_ai_shot(
    animation_scene: AnimationScene,
    *,
    production_spec: CharacterProductionSpec,
    camera_plan: tuple[
        str,
        str,
        str,
    ] | None = None,
) -> tuple[
    int,
    tuple[object, ...],
    CameraDirectionCommand | None,
]:
    """Build the rig and execute trusted character and camera intent."""

    validate_character_production_binding(
        animation_scene,
        production_spec,
    )

    end_frame = timeline_end_frame(
        animation_scene
    )

    configure_timeline(
        start_frame=START_FRAME,
        end_frame=end_frame,
        fps=FPS,
    )

    ground = create_ground()

    camera = create_camera()

    camera_command: (
        CameraDirectionCommand
        | None
    ) = None

    if camera_plan is not None:
        (
            framing,
            camera_intent,
            pacing,
        ) = camera_plan

        camera_command = compile_camera_direction(
            framing=framing,
            camera_intent=camera_intent,
            pacing=pacing,
            timeline_end_frame=end_frame,
        )

        camera_command = retarget_camera_for_character(
            camera_command,
            production_spec,
        )

        apply_camera_direction(
            camera_name=camera.name,
            command=camera_command,
        )

    built_character = build_character(
        production_spec
    )

    rig_name = (
        built_character.armature.name
    )

    # Keep existing generic cel quantization on anatomical meshes only.
    # Hair and outfit retain their character-specific production palette.
    body_parts = (
        built_character.body_parts
    )

    set_location(
        rig_name,
        (
            0.0,
            0.0,
            0.0,
        ),
    )

    commands = execute_animation_scene(
        animation_scene,
        armature_name=rig_name,
        fps=FPS,
    )

    apply_anime_cel_v1(
        body_parts=body_parts,
        ground=ground,
        style=ANIME_CEL_V1,
    )

    apply_warm_key_cool_fill(
        body_parts=body_parts,
        style=ANIME_CEL_V1,
    )

    create_layered_2_5d_background(
        style=ANIME_CEL_V1
    )

    apply_bold_ink_outline(
        style=ANIME_CEL_V1
    )

    configure_clean_cel_compositor(
        style=ANIME_CEL_V1
    )

    apply_anime_camera_presentation(
        camera=camera,
        style=ANIME_CEL_V1,
        framing=style_camera_framing(
            camera_plan
        ),
    )

    return (
        end_frame,
        commands,
        camera_command,
    )


def main() -> None:
    """Create and render an AI-directed Studio engineering shot."""

    (
        blend_path,
        preview_path,
        ir_path,
        camera_plan_path,
    ) = parse_arguments()

    blend_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    animation_scene = load_animation_scene(
        ir_path
    )

    production_spec = load_character_production(
        blend_path.parent
        / CHARACTER_PRODUCTION_FILENAME
    )

    camera_plan = (
        load_director_camera_plan(
            camera_plan_path,
            animation_scene,
        )
        if camera_plan_path is not None
        else None
    )

    clear_scene()

    (
        end_frame,
        commands,
        camera_command,
    ) = build_ai_shot(
        animation_scene,
        production_spec=production_spec,
        camera_plan=camera_plan,
    )

    print(
        "STUDIO_CHARACTER_PRODUCTION_EXECUTED_OK"
    )

    configure_workbench_cel_preview(
        str(preview_path),
        style=ANIME_CEL_V1,
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
    print("STUDIO_VISUAL_STYLE_APPLIED_OK")
    print("STUDIO_VISUAL_STYLE=anime_cel_v1")
    print("STUDIO_RENDER_PROFILE=workbench_cel")
    print("STUDIO_CEL_LEVELS=3")
    print("STUDIO_LINE_TREATMENT=BOLD_INK")
    print("STUDIO_LIGHTING_TREATMENT=WARM_KEY_COOL_FILL")
    print("STUDIO_BACKGROUND_TREATMENT=LAYERED_2_5D")
    print("STUDIO_COMPOSITING=CLEAN_CEL")
    print(
        "STUDIO_STYLE_CAMERA_PRESET="
        + style_camera_framing(
            camera_plan
        )
    )

    if camera_command is not None:
        print(
            "STUDIO_DIRECTOR_CAMERA_EXECUTED_OK"
        )

        print(
            "STUDIO_CAMERA_FRAMING="
            + camera_command.framing
        )

        print(
            "STUDIO_CAMERA_INTENT="
            + camera_command.camera_intent
        )

        print(
            "STUDIO_CAMERA_PACING="
            + camera_command.pacing
        )

        print(
            "STUDIO_CAMERA_FRAMES="
            f"{camera_command.start_frame}:"
            f"{camera_command.end_frame}"
        )

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
