"""Create Studio's deterministic Blender bridge proof scene.

This module executes inside Blender, not inside Studio's normal Python runtime.
It accepts only output paths supplied by the trusted Blender adapter.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_arguments() -> tuple[Path, Path]:
    """Read the two trusted output paths passed after Blender's -- separator."""

    if "--" not in sys.argv:
        raise RuntimeError("Studio Blender arguments were not supplied.")

    args = sys.argv[sys.argv.index("--") + 1 :]

    if len(args) != 2:
        raise RuntimeError(
            "Expected exactly two Studio arguments: blend path and render path."
        )

    return Path(args[0]).resolve(), Path(args[1]).resolve()


def clear_scene() -> None:
    """Remove all objects from the current Blender scene."""

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def point_camera_at(camera: bpy.types.Object, target: Vector) -> None:
    """Orient a camera toward a target point."""

    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build_scene() -> None:
    """Build a small deterministic proof scene."""

    scene = bpy.context.scene

    # --------------------------------------------------------
    # Cube
    # --------------------------------------------------------

    bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0))
    cube = bpy.context.active_object
    cube.name = "StudioProofCube"

    # --------------------------------------------------------
    # Ground
    # --------------------------------------------------------

    bpy.ops.mesh.primitive_plane_add(
        size=12.0,
        location=(0.0, 0.0, -1.0),
    )
    ground = bpy.context.active_object
    ground.name = "StudioProofGround"

    # --------------------------------------------------------
    # Camera
    # --------------------------------------------------------

    bpy.ops.object.camera_add(location=(6.0, -6.0, 4.5))
    camera = bpy.context.active_object
    camera.name = "StudioProofCamera"

    point_camera_at(camera, Vector((0.0, 0.0, 0.0)))

    scene.camera = camera

    # --------------------------------------------------------
    # Key light
    # --------------------------------------------------------

    bpy.ops.object.light_add(
        type="AREA",
        location=(4.0, -3.0, 6.0),
    )
    light = bpy.context.active_object
    light.name = "StudioProofKeyLight"
    light.data.energy = 1000.0
    light.data.shape = "DISK"
    light.data.size = 5.0

    # --------------------------------------------------------
    # Fill light
    # --------------------------------------------------------

    bpy.ops.object.light_add(
        type="AREA",
        location=(-4.0, -1.0, 3.0),
    )
    fill = bpy.context.active_object
    fill.name = "StudioProofFillLight"
    fill.data.energy = 500.0
    fill.data.size = 4.0

    # --------------------------------------------------------
    # Render configuration
    # --------------------------------------------------------

    scene.render.engine = "BLENDER_WORKBENCH"

    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100

    scene.render.image_settings.file_format = "PNG"

    scene.render.film_transparent = False


def main() -> None:
    """Create, save, and render the deterministic proof scene."""

    blend_path, render_path = parse_arguments()

    blend_path.parent.mkdir(parents=True, exist_ok=True)
    render_path.parent.mkdir(parents=True, exist_ok=True)

    clear_scene()
    build_scene()

    scene = bpy.context.scene
    scene.render.filepath = str(render_path)

    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.render.render(write_still=True)

    print("STUDIO_BLENDER_PROOF_OK")
    print(f"STUDIO_BLEND_PATH={blend_path}")
    print(f"STUDIO_RENDER_PATH={render_path}")


if __name__ == "__main__":
    main()