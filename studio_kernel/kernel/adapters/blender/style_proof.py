"""Render Phase 5C Workbench-vs-deterministic-cel proof."""

from __future__ import annotations

import sys
from pathlib import Path

import bpy


PROJECT_ROOT = Path(__file__).resolve().parents[4]
KERNEL_ROOT = PROJECT_ROOT / "studio_kernel"

for bootstrap_path in (
    PROJECT_ROOT,
    KERNEL_ROOT,
):
    value = str(
        bootstrap_path
    )

    if value not in sys.path:
        sys.path.insert(
            0,
            value,
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
    disable_compositing,
    disable_ink_outline,
)

from kernel.visual_style import (
    ANIME_CEL_V1,
)


RIG_NAME = "StudioStyleProofRig"


def parse_arguments(
) -> tuple[
    Path,
    Path,
    Path,
    Path,
    Path,
    Path,
    Path,
    Path,
]:
    """Read trusted Phase 5C output paths."""

    if "--" not in sys.argv:
        raise RuntimeError(
            "Phase 5C output paths were not supplied."
        )

    args = sys.argv[
        sys.argv.index("--") + 1 :
    ]

    if len(args) != 8:
        raise RuntimeError(
            "Expected blend, reference PNG, cel PNG, inked PNG, "
            "lighting PNG, background PNG, composite PNG, "
            "and anime-camera PNG."
        )

    return (
        Path(args[0]).resolve(),
        Path(args[1]).resolve(),
        Path(args[2]).resolve(),
        Path(args[3]).resolve(),
        Path(args[4]).resolve(),
        Path(args[5]).resolve(),
        Path(args[6]).resolve(),
        Path(args[7]).resolve(),
    )


def build_scene(
) -> tuple[
    tuple[bpy.types.Object, ...],
    bpy.types.Object,
]:
    """Build the same primitive scene used by earlier phases."""

    ground = create_ground()

    create_camera()

    rig = create_humanoid_armature(
        RIG_NAME
    )

    body_parts = create_debug_body(
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

    bpy.context.view_layer.update()

    return (
        body_parts,
        ground,
    )


def render_reference(
    path: Path,
) -> None:
    """Render the unchanged Phase-2/3/4 engineering appearance."""

    disable_compositing()

    configure_render(
        path
    )

    bpy.ops.render.render(
        write_still=True
    )


def render_cel_only(
    path: Path,
    *,
    body_parts: tuple[bpy.types.Object, ...],
    ground: bpy.types.Object,
) -> tuple[
    int,
    int,
    int,
]:
    """Render Studio's deterministic three-tone cel treatment."""

    counts = apply_anime_cel_v1(
        body_parts=body_parts,
        ground=ground,
        style=ANIME_CEL_V1,
    )

    configure_workbench_cel_preview(
        str(path),
        style=ANIME_CEL_V1,
    )

    disable_compositing()
    disable_ink_outline()

    bpy.context.view_layer.update()

    bpy.ops.render.render(
        write_still=True
    )

    return counts


def render_inked(
    path: Path,
) -> None:
    """Render the same cel scene with Studio bold-ink silhouettes."""

    disable_compositing()

    apply_bold_ink_outline(
        style=ANIME_CEL_V1
    )

    bpy.context.scene.render.filepath = str(
        path
    )

    bpy.context.view_layer.update()

    bpy.ops.render.render(
        write_still=True
    )


def render_lighting(
    path: Path,
    *,
    body_parts: tuple[bpy.types.Object, ...],
) -> tuple[int, int]:
    """Render cel + ink with warm-key/cool-fill presentation."""

    disable_compositing()

    counts = apply_warm_key_cool_fill(
        body_parts=body_parts,
        style=ANIME_CEL_V1,
    )

    apply_bold_ink_outline(
        style=ANIME_CEL_V1
    )

    bpy.context.scene.render.filepath = str(
        path
    )

    bpy.context.view_layer.update()

    bpy.ops.render.render(
        write_still=True
    )

    return counts


def render_background_depth(
    path: Path,
) -> tuple[bpy.types.Object, ...]:
    """Add the first layered 2.5D environment and render it."""

    disable_compositing()

    objects = create_layered_2_5d_background(
        style=ANIME_CEL_V1
    )

    apply_bold_ink_outline(
        style=ANIME_CEL_V1
    )

    bpy.context.scene.render.filepath = str(
        path
    )

    bpy.context.view_layer.update()

    bpy.ops.render.render(
        write_still=True
    )

    return objects


def render_composited(
    path: Path,
) -> None:
    """Render the final Phase 5G clean-cel composite."""

    configure_clean_cel_compositor(
        style=ANIME_CEL_V1
    )

    apply_bold_ink_outline(
        style=ANIME_CEL_V1
    )

    bpy.context.scene.render.filepath = str(
        path
    )

    bpy.context.view_layer.update()

    bpy.ops.render.render(
        write_still=True
    )


def render_anime_camera(
    path: Path,
) -> dict[str, float]:
    """Render the full style stack with anime cinematic framing."""

    scene = bpy.context.scene

    camera = scene.camera

    if camera is None:
        raise RuntimeError(
            "Scene has no active camera."
        )

    preset = apply_anime_camera_presentation(
        camera=camera,
        style=ANIME_CEL_V1,
        framing="medium_hero",
    )

    configure_clean_cel_compositor(
        style=ANIME_CEL_V1
    )

    apply_bold_ink_outline(
        style=ANIME_CEL_V1
    )

    scene.render.filepath = str(
        path
    )

    bpy.context.view_layer.update()

    bpy.ops.render.render(
        write_still=True
    )

    return preset


def main() -> None:
    """Produce the Phase 5C before/after proof."""

    (
        blend_path,
        reference_path,
        cel_path,
        inked_path,
        lighting_path,
        background_path,
        composite_path,
        camera_path,
    ) = parse_arguments()

    blend_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    clear_scene()

    body_parts, ground = build_scene()

    render_reference(
        reference_path
    )

    (
        shadow_faces,
        base_faces,
        highlight_faces,
    ) = render_cel_only(
        cel_path,
        body_parts=body_parts,
        ground=ground,
    )

    render_inked(
        inked_path
    )

    (
        warm_faces,
        cool_faces,
    ) = render_lighting(
        lighting_path,
        body_parts=body_parts,
    )

    background_objects = render_background_depth(
        background_path
    )

    render_composited(
        composite_path
    )

    camera_preset = render_anime_camera(
        camera_path
    )

    if len(background_objects) != 5:
        raise RuntimeError(
            "Expected exactly five 2.5D background objects."
        )

    if warm_faces <= 0:
        raise RuntimeError(
            "Lighting proof produced no warm-key faces."
        )

    if cool_faces <= 0:
        raise RuntimeError(
            "Lighting proof produced no cool-fill faces."
        )

    if shadow_faces <= 0:
        raise RuntimeError(
            "Cel proof produced no shadow faces."
        )

    if base_faces <= 0:
        raise RuntimeError(
            "Cel proof produced no base faces."
        )

    if highlight_faces <= 0:
        raise RuntimeError(
            "Cel proof produced no highlight faces."
        )

    bpy.ops.wm.save_as_mainfile(
        filepath=str(
            blend_path
        )
    )

    print("STUDIO_PHASE5C_STYLE_PROOF_OK")

    print(
        "STUDIO_RENDER_ENGINE="
        "BLENDER_WORKBENCH"
    )

    print(
        "STUDIO_RENDER_PROFILE="
        "workbench_cel"
    )

    print(
        "STUDIO_VISUAL_STYLE="
        "anime_cel_v1"
    )

    print("STUDIO_CEL_LEVELS=3")

    print(
        "STUDIO_CEL_IMPLEMENTATION="
        "DETERMINISTIC_FACE_QUANTIZATION"
    )

    print(
        f"STUDIO_CEL_SHADOW_FACES="
        f"{shadow_faces}"
    )

    print(
        f"STUDIO_CEL_BASE_FACES="
        f"{base_faces}"
    )

    print(
        f"STUDIO_CEL_HIGHLIGHT_FACES="
        f"{highlight_faces}"
    )

    print(
        "STUDIO_EEVEE_REQUIRED=NO"
    )

    print(
        "STUDIO_GPU_UPGRADE_REQUIRED=NO"
    )

    print(
        "STUDIO_LINE_TREATMENT=BOLD_INK"
    )

    print(
        "STUDIO_LINE_BACKEND="
        "WORKBENCH_OBJECT_OUTLINE"
    )

    print(
        "STUDIO_LINE_WIDTH_TARGET_PX="
        + str(
            ANIME_CEL_V1.line_width_px
        )
    )

    print(
        "STUDIO_LIGHTING_TREATMENT="
        "WARM_KEY_COOL_FILL"
    )

    print(
        f"STUDIO_WARM_KEY_FACES="
        f"{warm_faces}"
    )

    print(
        f"STUDIO_COOL_FILL_FACES="
        f"{cool_faces}"
    )

    print(
        "STUDIO_PALETTE_PRESENTATION="
        "ANIME_CEL_V1"
    )

    print(
        "STUDIO_BACKGROUND_TREATMENT="
        "LAYERED_2_5D"
    )

    print(
        "STUDIO_BACKGROUND_DEPTH_LAYERS="
        + str(
            ANIME_CEL_V1.background_depth_layers
        )
    )

    print(
        "STUDIO_BACKGROUND_OBJECTS="
        + str(
            len(background_objects)
        )
    )

    print(
        "STUDIO_COMPOSITING=CLEAN_CEL"
    )

    print(
        "STUDIO_COMPOSITOR_BACKEND="
        "BLENDER_COMPOSITOR_NODES"
    )

    print(
        "STUDIO_COMPOSITOR_GLOW="
        "DEFERRED_BLENDER_5_2"
    )

    print(
        "STUDIO_COMPOSITOR_GRADE="
        "SATURATION_CONTRAST"
    )

    print(
        "STUDIO_CAMERA_PRESENTATION="
        "ANIME_CINEMATIC"
    )

    print(
        "STUDIO_CAMERA_FRAMING="
        "MEDIUM_HERO"
    )

    print(
        "STUDIO_CAMERA_LENS_MM="
        + str(
            camera_preset["lens_mm"]
        )
    )

    print(
        "STUDIO_CAMERA_SHIFT_X="
        + str(
            camera_preset["shift_x"]
        )
    )

    print(
        "STUDIO_CAMERA_SHIFT_Y="
        + str(
            camera_preset["shift_y"]
        )
    )

    print(
        "STUDIO_REFERENCE_PATH="
        + str(reference_path)
    )

    print(
        "STUDIO_CEL_ONLY_PATH="
        + str(cel_path)
    )

    print(
        "STUDIO_INKED_PATH="
        + str(inked_path)
    )

    print(
        "STUDIO_LIGHTING_PATH="
        + str(lighting_path)
    )

    print(
        "STUDIO_BACKGROUND_PATH="
        + str(background_path)
    )

    print(
        "STUDIO_COMPOSITE_PATH="
        + str(composite_path)
    )

    print(
        "STUDIO_CAMERA_PATH="
        + str(camera_path)
    )

    print(
        "STUDIO_BLEND_PATH="
        + str(blend_path)
    )


if __name__ == "__main__":
    main()
