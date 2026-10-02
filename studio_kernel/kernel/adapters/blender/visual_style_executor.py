"""Hardware-safe deterministic Blender visual-style executor.

Studio computes discrete cel-tone assignment itself and uses Blender
Workbench only as the stable rasterization stage. No Eevee shader runtime,
LLM integration, arbitrary generated shader code, eval, or exec is used.
"""

from __future__ import annotations

import bpy

from mathutils import Vector

from kernel.visual_style import (
    BackgroundProfile,
    CameraPresentationProfile,
    CelProfile,
    ColorRGB,
    CompositingProfile,
    LightingProfile,
    LineProfile,
    RenderProfile,
    VisualStyle,
    VisualStyleError,
)


CEL_LIGHT_DIRECTION = Vector(
    (
        -0.45,
        -0.55,
        0.70,
    )
).normalized()

WARM_KEY_DIRECTION = Vector(
    (
        -0.70,
        -0.30,
        0.55,
    )
).normalized()

COOL_FILL_DIRECTION = Vector(
    (
        0.65,
        0.40,
        0.50,
    )
).normalized()

WARM_MIX = 0.22
COOL_MIX = 0.18

SHADOW_THRESHOLD = -0.10
HIGHLIGHT_THRESHOLD = 0.52


def _rgba(
    color: ColorRGB,
) -> tuple[
    float,
    float,
    float,
    float,
]:
    """Convert one trusted Studio color to Blender RGBA."""

    return (
        *color.as_tuple(),
        1.0,
    )


def create_workbench_material(
    name: str,
    *,
    color: ColorRGB,
) -> bpy.types.Material:
    """Create one Workbench-visible deterministic material."""

    material = bpy.data.materials.new(
        name=name
    )

    material.use_nodes = False

    material.diffuse_color = _rgba(
        color
    )

    return material


def create_three_tone_materials(
    *,
    style: VisualStyle,
) -> tuple[
    bpy.types.Material,
    bpy.types.Material,
    bpy.types.Material,
]:
    """Create the trusted shadow/base/highlight cel palette."""

    if (
        style.cel_profile
        is not CelProfile.THREE_TONE
    ):
        raise VisualStyleError(
            "Three-tone material execution requires "
            "the three_tone cel profile."
        )

    if style.cel_levels != 3:
        raise VisualStyleError(
            "Three-tone execution requires exactly 3 levels."
        )

    return (
        create_workbench_material(
            "StudioCelShadow",
            color=style.palette.character_shadow,
        ),
        create_workbench_material(
            "StudioCelBase",
            color=style.palette.character_base,
        ),
        create_workbench_material(
            "StudioCelHighlight",
            color=style.palette.character_highlight,
        ),
    )


def _tone_index(
    light_dot: float,
) -> int:
    """Quantize a surface/light value into exactly three cel bands."""

    if light_dot < SHADOW_THRESHOLD:
        return 0

    if light_dot >= HIGHLIGHT_THRESHOLD:
        return 2

    return 1


def quantize_mesh_cel_tones(
    obj: bpy.types.Object,
    *,
    materials: tuple[
        bpy.types.Material,
        bpy.types.Material,
        bpy.types.Material,
    ],
) -> tuple[
    int,
    int,
    int,
]:
    """Assign each mesh polygon to one discrete cel-tone material."""

    if obj.type != "MESH":
        raise RuntimeError(
            f"Cel-tone target is not a mesh: {obj.name}"
        )

    mesh = obj.data

    mesh.materials.clear()

    for material in materials:
        mesh.materials.append(
            material
        )

    normal_matrix = (
        obj.matrix_world
        .to_3x3()
    )

    counts = [
        0,
        0,
        0,
    ]

    for polygon in mesh.polygons:
        world_normal = (
            normal_matrix
            @ polygon.normal
        ).normalized()

        light_dot = float(
            world_normal.dot(
                CEL_LIGHT_DIRECTION
            )
        )

        index = _tone_index(
            light_dot
        )

        polygon.material_index = index

        counts[index] += 1

    return (
        counts[0],
        counts[1],
        counts[2],
    )


def assign_flat_material(
    obj: bpy.types.Object,
    *,
    material: bpy.types.Material,
) -> None:
    """Assign one flat material to a mesh."""

    if obj.type != "MESH":
        raise RuntimeError(
            f"Material target is not a mesh: {obj.name}"
        )

    obj.data.materials.clear()

    obj.data.materials.append(
        material
    )

    for polygon in obj.data.polygons:
        polygon.material_index = 0


def configure_workbench_cel_preview(
    preview_path: str,
    *,
    style: VisualStyle,
) -> None:
    """Configure stable Workbench as Studio's cel rasterizer."""

    if (
        style.render_profile
        is not RenderProfile.WORKBENCH_CEL
    ):
        raise VisualStyleError(
            "Visual style does not use "
            "the Workbench cel renderer."
        )

    scene = bpy.context.scene

    scene.render.engine = (
        "BLENDER_WORKBENCH"
    )

    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100

    scene.render.image_settings.file_format = "PNG"

    scene.render.film_transparent = False
    scene.render.filepath = preview_path

    shading = scene.display.shading

    shading.light = "FLAT"
    shading.color_type = "MATERIAL"

    shading.show_shadows = False
    shading.show_cavity = False
    shading.show_specular_highlight = False

    shading.background_type = "VIEWPORT"

    shading.background_color = (
        style.palette.background_far.r,
        style.palette.background_far.g,
        style.palette.background_far.b,
    )


def _mix_color(
    base: ColorRGB,
    tint: ColorRGB,
    amount: float,
) -> ColorRGB:
    """Blend two trusted Studio colors deterministically."""

    inverse = 1.0 - amount

    return ColorRGB(
        (
            base.r * inverse
            + tint.r * amount
        ),
        (
            base.g * inverse
            + tint.g * amount
        ),
        (
            base.b * inverse
            + tint.b * amount
        ),
    )


def create_warm_cool_cel_materials(
    *,
    style: VisualStyle,
) -> tuple[bpy.types.Material, ...]:
    """Create warm/cool variants while retaining three value bands."""

    if (
        style.lighting_profile
        is not LightingProfile.WARM_KEY_COOL_FILL
    ):
        raise VisualStyleError(
            "Lighting execution requires "
            "warm_key_cool_fill."
        )

    base_colors = (
        style.palette.character_shadow,
        style.palette.character_base,
        style.palette.character_highlight,
    )

    labels = (
        "Shadow",
        "Base",
        "Highlight",
    )

    materials: list[
        bpy.types.Material
    ] = []

    for label, base in zip(
        labels,
        base_colors,
        strict=True,
    ):
        cool = _mix_color(
            base,
            style.palette.cool_fill,
            COOL_MIX,
        )

        warm = _mix_color(
            base,
            style.palette.warm_key,
            WARM_MIX,
        )

        materials.append(
            create_workbench_material(
                f"StudioCel{label}Cool",
                color=cool,
            )
        )

        materials.append(
            create_workbench_material(
                f"StudioCel{label}Warm",
                color=warm,
            )
        )

    return tuple(
        materials
    )


def apply_warm_key_cool_fill(
    *,
    body_parts: tuple[bpy.types.Object, ...],
    style: VisualStyle,
) -> tuple[int, int]:
    """Apply deterministic warm-key/cool-fill anime presentation."""

    materials = create_warm_cool_cel_materials(
        style=style
    )

    warm_faces = 0
    cool_faces = 0

    bpy.context.view_layer.update()

    for obj in body_parts:
        if obj.type != "MESH":
            raise RuntimeError(
                f"Lighting target is not a mesh: {obj.name}"
            )

        mesh = obj.data
        mesh.materials.clear()

        for material in materials:
            mesh.materials.append(
                material
            )

        normal_matrix = (
            obj.matrix_world
            .to_3x3()
        )

        for polygon in mesh.polygons:
            world_normal = (
                normal_matrix
                @ polygon.normal
            ).normalized()

            tone = _tone_index(
                float(
                    world_normal.dot(
                        CEL_LIGHT_DIRECTION
                    )
                )
            )

            warm_dot = float(
                world_normal.dot(
                    WARM_KEY_DIRECTION
                )
            )

            cool_dot = float(
                world_normal.dot(
                    COOL_FILL_DIRECTION
                )
            )

            if warm_dot >= cool_dot:
                side = 1
                warm_faces += 1
            else:
                side = 0
                cool_faces += 1

            polygon.material_index = (
                tone * 2
                + side
            )

    return (
        warm_faces,
        cool_faces,
    )


def _create_background_block(
    name: str,
    *,
    location: tuple[
        float,
        float,
        float,
    ],
    scale: tuple[
        float,
        float,
        float,
    ],
    material: bpy.types.Material,
) -> bpy.types.Object:
    """Create one graphic low-cost anime background silhouette."""

    bpy.ops.mesh.primitive_cube_add(
        location=location
    )

    obj = bpy.context.active_object

    if obj is None:
        raise RuntimeError(
            f"Blender did not create background block: {name}"
        )

    obj.name = name

    obj.scale = scale

    bpy.context.view_layer.objects.active = obj

    obj.select_set(
        True
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    obj.select_set(
        False
    )

    # Break the perfect CG rectangle while retaining
    # the existing three-depth low-cost system.
    if "Left" in name:
        obj.rotation_euler[2] = 0.035
    elif "Right" in name:
        obj.rotation_euler[2] = -0.035

    bevel = obj.modifiers.new(
        name="StudioBackgroundBevel",
        type="BEVEL",
    )

    bevel.width = min(
        obj.dimensions
    ) * 0.10

    bevel.segments = 1

    assign_flat_material(
        obj,
        material=material,
    )

    return obj

def create_layered_2_5d_background(
    *,
    style: VisualStyle,
) -> tuple[bpy.types.Object, ...]:
    """Create Studio's first three-depth anime background stage."""

    if (
        style.background_profile
        is not BackgroundProfile.LAYERED_2_5D
    ):
        raise VisualStyleError(
            "Background execution requires "
            "the layered_2_5d profile."
        )

    if style.background_depth_layers != 3:
        raise VisualStyleError(
            "Visual Style V1 background requires exactly 3 layers."
        )

    far_material = create_workbench_material(
        "StudioBackgroundFarMaterial",
        color=style.palette.background_far,
    )

    mid_material = create_workbench_material(
        "StudioBackgroundMidMaterial",
        color=style.palette.background_mid,
    )

    near_material = create_workbench_material(
        "StudioBackgroundNearMaterial",
        color=style.palette.background_near,
    )

    objects = (
        _create_background_block(
            "StudioBackgroundFar",
            location=(
                0.0,
                8.0,
                3.0,
            ),
            scale=(
                8.5,
                0.20,
                3.0,
            ),
            material=far_material,
        ),

        _create_background_block(
            "StudioBackgroundMidLeft",
            location=(
                -3.3,
                5.3,
                2.0,
            ),
            scale=(
                2.4,
                0.25,
                2.0,
            ),
            material=mid_material,
        ),

        _create_background_block(
            "StudioBackgroundMidRight",
            location=(
                3.2,
                5.8,
                1.55,
            ),
            scale=(
                2.0,
                0.25,
                1.55,
            ),
            material=mid_material,
        ),

        _create_background_block(
            "StudioBackgroundNearLeft",
            location=(
                -5.2,
                2.8,
                2.3,
            ),
            scale=(
                1.35,
                0.32,
                2.3,
            ),
            material=near_material,
        ),

        _create_background_block(
            "StudioBackgroundNearRight",
            location=(
                5.0,
                3.0,
                1.9,
            ),
            scale=(
                1.25,
                0.32,
                1.9,
            ),
            material=near_material,
        ),
    )

    return objects


def disable_compositing(
) -> None:
    """Disable Studio post processing for comparison renders."""

    scene = bpy.context.scene

    scene.render.use_compositing = False


def configure_clean_cel_compositor(
    *,
    style: VisualStyle,
) -> None:
    """Configure Studio's restrained clean-cel compositor."""

    if (
        style.compositing_profile
        is not CompositingProfile.CLEAN_CEL
    ):
        raise VisualStyleError(
            "Compositing execution requires "
            "the clean_cel profile."
        )

    scene = bpy.context.scene

    existing = bpy.data.node_groups.get(
        "StudioCleanCelCompositor"
    )

    if existing is not None:
        bpy.data.node_groups.remove(
            existing,
            do_unlink=True,
        )

    tree = bpy.data.node_groups.new(
        name="StudioCleanCelCompositor",
        type="CompositorNodeTree",
    )

    scene.compositing_node_group = tree
    scene.render.use_compositing = True

    if scene.compositing_node_group is not tree:
        raise RuntimeError(
            "Blender compositor node group assignment failed."
        )

    output_socket = tree.interface.new_socket(
        name="Image",
        in_out="OUTPUT",
        socket_type="NodeSocketColor",
    )

    if output_socket is None:
        raise RuntimeError(
            "Blender compositor Image output was not created."
        )

    nodes = tree.nodes
    links = tree.links

    render_layers = nodes.new(
        "CompositorNodeRLayers"
    )

    hue_sat = nodes.new(
        "CompositorNodeHueSat"
    )

    bright_contrast = nodes.new(
        "CompositorNodeBrightContrast"
    )

    group_output = nodes.new(
        "NodeGroupOutput"
    )

    render_layers.name = (
        "StudioRenderLayers"
    )

    hue_sat.name = (
        "StudioCleanCelSaturation"
    )

    bright_contrast.name = (
        "StudioCleanCelContrast"
    )

    group_output.name = (
        "StudioCompositeOutput"
    )

    hue_sat.inputs[
        "Saturation"
    ].default_value = 1.08

    hue_sat.inputs[
        "Value"
    ].default_value = 0.98

    bright_contrast.inputs[
        "Bright"
    ].default_value = 1.0

    bright_contrast.inputs[
        "Contrast"
    ].default_value = 6.0

    links.new(
        render_layers.outputs["Image"],
        hue_sat.inputs["Image"],
    )

    links.new(
        hue_sat.outputs["Image"],
        bright_contrast.inputs["Image"],
    )

    if "Image" not in group_output.inputs:
        raise RuntimeError(
            "Studio compositor group output has no Image socket."
        )

    links.new(
        bright_contrast.outputs["Image"],
        group_output.inputs["Image"],
    )


ANIME_CAMERA_PRESETS = {
    "wide_establishing": {
        "lens_mm": 38.0,
        "shift_x": 0.0,
        "shift_y": 0.0,
    },
    "medium_hero": {
        "lens_mm": 52.0,
        "shift_x": 0.06,
        "shift_y": -0.02,
    },
    "close_intense": {
        "lens_mm": 68.0,
        "shift_x": -0.04,
        "shift_y": 0.025,
    },
}


def apply_anime_camera_presentation(
    *,
    camera: bpy.types.Object,
    style: VisualStyle,
    framing: str,
) -> dict[str, float]:
    """Apply trusted anime-style framing on top of Director camera intent."""

    if (
        style.camera_profile
        is not CameraPresentationProfile.ANIME_CINEMATIC
    ):
        raise VisualStyleError(
            "Camera execution requires "
            "the anime_cinematic profile."
        )

    if camera.type != "CAMERA":
        raise RuntimeError(
            "Anime camera presentation requires a camera object."
        )

    preset = ANIME_CAMERA_PRESETS.get(
        framing
    )

    if preset is None:
        raise VisualStyleError(
            "Unsupported anime camera framing: "
            + framing
        )

    camera.data.lens = preset[
        "lens_mm"
    ]

    camera.data.shift_x = preset[
        "shift_x"
    ]

    camera.data.shift_y = preset[
        "shift_y"
    ]

    return dict(
        preset
    )


def disable_ink_outline(
) -> None:
    """Disable Workbench outlines for cel-only comparison renders."""

    shading = bpy.context.scene.display.shading

    shading.show_object_outline = False


def apply_bold_ink_outline(
    *,
    style: VisualStyle,
) -> None:
    """Apply Studio's hardware-safe anime ink and form separation."""

    if (
        style.line_profile
        is not LineProfile.BOLD_INK
    ):
        raise VisualStyleError(
            "Bold-ink execution requires "
            "the bold_ink line profile."
        )

    shading = bpy.context.scene.display.shading

    shading.show_object_outline = True

    shading.object_outline_color = (
        style.palette.ink.r,
        style.palette.ink.g,
        style.palette.ink.b,
    )

    # Workbench cavity is cheap and gives the cel image
    # extra graphic separation around modeled form changes.
    shading.show_cavity = True

    if hasattr(
        shading,
        "cavity_type",
    ):
        shading.cavity_type = "WORLD"

    if hasattr(
        shading,
        "curvature_ridge_factor",
    ):
        shading.curvature_ridge_factor = 1.35

    if hasattr(
        shading,
        "curvature_valley_factor",
    ):
        shading.curvature_valley_factor = 0.65

    if hasattr(
        shading,
        "cavity_ridge_factor",
    ):
        shading.cavity_ridge_factor = 1.20

    if hasattr(
        shading,
        "cavity_valley_factor",
    ):
        shading.cavity_valley_factor = 0.60

def apply_anime_cel_v1(
    *,
    body_parts: tuple[bpy.types.Object, ...],
    ground: bpy.types.Object,
    style: VisualStyle,
) -> tuple[
    int,
    int,
    int,
]:
    """Apply Studio's first hardware-safe three-tone anime treatment."""

    materials = create_three_tone_materials(
        style=style
    )

    ground_material = create_workbench_material(
        "StudioCelGround",
        color=style.palette.ground,
    )

    total = [
        0,
        0,
        0,
    ]

    bpy.context.view_layer.update()

    for part in body_parts:
        counts = quantize_mesh_cel_tones(
            part,
            materials=materials,
        )

        for index in range(3):
            total[index] += counts[index]

    assign_flat_material(
        ground,
        material=ground_material,
    )

    return (
        total[0],
        total[1],
        total[2],
    )
