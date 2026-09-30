"""Build Studio's first deterministic hands-off animated shot.

This trusted module executes inside Blender. It composes only Studio-owned
rig, toolkit, and semantic-action APIs. It does not execute dynamic Python
or communicate externally.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy


PROJECT_ROOT = Path(__file__).resolve().parents[4]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from studio_kernel.kernel.adapters.blender.actions import (
    idle,
    step_forward,
    turn_head,
    wave,
)
from studio_kernel.kernel.adapters.blender.humanoid_rig import (
    create_humanoid_armature,
)
from studio_kernel.kernel.adapters.blender.toolkit_level0 import (
    configure_timeline,
    point_camera_at,
    set_location,
)


RIG_NAME = "StudioShotRig"
CAMERA_NAME = "StudioShotCamera"

START_FRAME = 1
END_FRAME = 144
FPS = 24


def parse_arguments() -> tuple[Path, Path]:
    """Read trusted blend and preview paths passed after Blender's separator."""

    if "--" not in sys.argv:
        raise RuntimeError(
            "Studio shot arguments were not supplied."
        )

    args = sys.argv[
        sys.argv.index("--") + 1 :
    ]

    if len(args) != 2:
        raise RuntimeError(
            "Expected exactly two Studio arguments: "
            "blend path and preview path."
        )

    return (
        Path(args[0]).resolve(),
        Path(args[1]).resolve(),
    )


def clear_scene() -> None:
    """Remove factory-startup objects before deterministic construction."""

    bpy.ops.object.select_all(
        action="SELECT"
    )
    bpy.ops.object.delete(
        use_global=False
    )


def create_camera() -> bpy.types.Object:
    """Create the fixed camera for the first deterministic shot."""

    bpy.ops.object.camera_add(
        location=(6.5, -9.0, 4.0)
    )

    camera = bpy.context.active_object
    camera.name = CAMERA_NAME

    point_camera_at(
        CAMERA_NAME,
        (0.0, -0.4, 1.0),
    )

    bpy.context.scene.camera = camera

    return camera


def create_ground() -> bpy.types.Object:
    """Create a lightweight visual ground plane."""

    bpy.ops.mesh.primitive_plane_add(
        size=14.0,
        location=(0.0, 0.0, -1.35),
    )

    ground = bpy.context.active_object
    ground.name = "StudioShotGround"

    return ground


def configure_render(
    preview_path: Path,
) -> None:
    """Configure the hardware-safe engineering preview."""

    scene = bpy.context.scene

    scene.render.engine = "BLENDER_WORKBENCH"

    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100

    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(preview_path)


def build_shot() -> None:
    """Construct and animate Studio's first deterministic shot."""

    configure_timeline(
        start_frame=START_FRAME,
        end_frame=END_FRAME,
        fps=FPS,
    )

    create_ground()
    create_camera()

    create_humanoid_armature(
        RIG_NAME
    )

    set_location(
        RIG_NAME,
        (0.0, 0.0, 0.0),
    )

    idle(
        armature_name=RIG_NAME,
        start_frame=1,
        duration_frames=47,
    )

    turn_head(
        armature_name=RIG_NAME,
        start_frame=49,
        duration_frames=23,
        direction="right",
    )

    wave(
        armature_name=RIG_NAME,
        start_frame=73,
        duration_frames=47,
        side="L",
    )

    step_forward(
        armature_name=RIG_NAME,
        start_frame=121,
        duration_frames=23,
        distance=0.75,
    )


def main() -> None:
    """Build, save, and preview the deterministic animated shot."""

    blend_path, preview_path = parse_arguments()

    blend_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    preview_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    clear_scene()
    build_shot()
    configure_render(preview_path)

    scene = bpy.context.scene
    scene.frame_set(END_FRAME)

    bpy.ops.wm.save_as_mainfile(
        filepath=str(blend_path)
    )

    bpy.ops.render.render(
        write_still=True
    )

    print("STUDIO_DETERMINISTIC_SHOT_OK")
    print(f"STUDIO_BLEND_PATH={blend_path}")
    print(f"STUDIO_PREVIEW_PATH={preview_path}")
    print(f"STUDIO_TIMELINE={START_FRAME}:{END_FRAME}:{FPS}")
    print("STUDIO_DURATION_SECONDS=6")
    print(
        "STUDIO_ACTIONS="
        "idle,turn_head,wave,step_forward"
    )


if __name__ == "__main__":
    main()
