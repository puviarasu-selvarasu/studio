"""Contract tests for the hardware-safe Blender cel executor."""

from pathlib import Path


ROOT = Path(__file__).parents[1]

EXECUTOR = (
    ROOT
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "visual_style_executor.py"
)

PROOF = (
    ROOT
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "style_proof.py"
)


def test_executor_uses_proven_workbench_renderer() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert (
        '"BLENDER_WORKBENCH"'
        in source
    )

    assert "BLENDER_EEVEE" not in source

    assert "resolution_x = 640" in source
    assert "resolution_y = 360" in source


def test_executor_uses_material_color_and_flat_lighting() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert 'shading.light = "FLAT"' in source

    assert (
        'shading.color_type = "MATERIAL"'
        in source
    )

    assert "material.diffuse_color" in source


def test_executor_quantizes_exact_three_tone_faces() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert (
        "def quantize_mesh_cel_tones("
        in source
    )

    assert "SHADOW_THRESHOLD" in source
    assert "HIGHLIGHT_THRESHOLD" in source

    assert (
        "polygon.material_index = index"
        in source
    )

    assert "StudioCelShadow" in source
    assert "StudioCelBase" in source
    assert "StudioCelHighlight" in source


def test_executor_uses_surface_normals_and_fixed_light_direction() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert "CEL_LIGHT_DIRECTION" in source
    assert "polygon.normal" in source
    assert "world_normal.dot(" in source


def test_executor_has_no_ai_or_dynamic_shader_execution() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    lowered = source.lower()

    assert "ollama" not in lowered
    assert "directoragent" not in lowered
    assert "animatoragent" not in lowered

    assert "ShaderNode" not in source

    assert "eval(" not in source
    assert "exec(" not in source


def test_style_proof_requires_all_three_cel_bands() -> None:
    source = PROOF.read_text(
        encoding="utf-8"
    )

    assert (
        "shadow_faces <= 0"
        in source
    )

    assert (
        "base_faces <= 0"
        in source
    )

    assert (
        "highlight_faces <= 0"
        in source
    )

    assert (
        "DETERMINISTIC_FACE_QUANTIZATION"
        in source
    )


def test_phase5g_explicitly_avoids_hardware_upgrade_gate() -> None:
    source = PROOF.read_text(
        encoding="utf-8"
    )

    assert (
        "STUDIO_EEVEE_REQUIRED=NO"
        in source
    )

    assert (
        "STUDIO_GPU_UPGRADE_REQUIRED=NO"
        in source
    )

    assert (
        "STUDIO_LINE_TREATMENT=BOLD_INK"
        in source
    )

    assert (
        "STUDIO_COMPOSITING=CLEAN_CEL"
        in source
    )


def test_executor_supports_bold_ink_object_outline() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert "LineProfile.BOLD_INK" in source

    assert (
        "def apply_bold_ink_outline("
        in source
    )

    assert (
        "shading.show_object_outline = True"
        in source
    )

    assert (
        "shading.object_outline_color"
        in source
    )

    assert (
        "style.palette.ink"
        in source
    )


def test_executor_can_disable_outline_for_before_after_proof() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert (
        "def disable_ink_outline("
        in source
    )

    assert (
        "shading.show_object_outline = False"
        in source
    )


def test_style_proof_renders_cel_and_bold_ink_versions() -> None:
    source = PROOF.read_text(
        encoding="utf-8"
    )

    assert "render_cel_only(" in source
    assert "render_inked(" in source

    assert (
        "STUDIO_LINE_TREATMENT=BOLD_INK"
        in source
    )

    assert (
        "STUDIO_LINE_BACKEND="
        in source
    )

    assert (
        "WORKBENCH_OBJECT_OUTLINE"
        in source
    )

    assert (
        "STUDIO_CEL_ONLY_PATH="
        in source
    )

    assert (
        "STUDIO_INKED_PATH="
        in source
    )


def test_executor_supports_warm_key_cool_fill() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert (
        "LightingProfile.WARM_KEY_COOL_FILL"
        in source
    )

    assert "WARM_KEY_DIRECTION" in source
    assert "COOL_FILL_DIRECTION" in source

    assert (
        "def apply_warm_key_cool_fill("
        in source
    )

    assert "style.palette.warm_key" in source
    assert "style.palette.cool_fill" in source


def test_lighting_preserves_three_value_bands_with_color_variants() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert (
        "tone * 2"
        in source
    )

    assert "StudioCelShadowCool" not in source

    assert (
        'f"StudioCel{label}Cool"'
        in source
    )

    assert (
        'f"StudioCel{label}Warm"'
        in source
    )


def test_style_proof_renders_warm_cool_lighting_version() -> None:
    source = PROOF.read_text(
        encoding="utf-8"
    )

    assert "render_lighting(" in source

    assert (
        "STUDIO_LIGHTING_TREATMENT="
        in source
    )

    assert (
        "WARM_KEY_COOL_FILL"
        in source
    )

    assert (
        "STUDIO_WARM_KEY_FACES="
        in source
    )

    assert (
        "STUDIO_COOL_FILL_FACES="
        in source
    )

    assert (
        "STUDIO_LIGHTING_PATH="
        in source
    )


def test_executor_builds_layered_2_5d_background() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert (
        "BackgroundProfile.LAYERED_2_5D"
        in source
    )

    assert (
        "def create_layered_2_5d_background("
        in source
    )

    assert "StudioBackgroundFar" in source
    assert "StudioBackgroundMidLeft" in source
    assert "StudioBackgroundMidRight" in source
    assert "StudioBackgroundNearLeft" in source
    assert "StudioBackgroundNearRight" in source


def test_background_uses_visual_style_depth_palette() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert "style.palette.background_far" in source
    assert "style.palette.background_mid" in source
    assert "style.palette.background_near" in source

    assert (
        "style.background_depth_layers != 3"
        in source
    )


def test_style_proof_renders_background_depth_version() -> None:
    source = PROOF.read_text(
        encoding="utf-8"
    )

    assert "render_background_depth(" in source

    assert (
        "STUDIO_BACKGROUND_TREATMENT="
        in source
    )

    assert "LAYERED_2_5D" in source

    assert (
        "STUDIO_BACKGROUND_DEPTH_LAYERS="
        in source
    )

    assert (
        "STUDIO_BACKGROUND_PATH="
        in source
    )


def test_executor_builds_clean_cel_compositor() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert (
        "CompositingProfile.CLEAN_CEL"
        in source
    )

    assert (
        "def configure_clean_cel_compositor("
        in source
    )

    assert "CompositorNodeRLayers" in source
    assert "CompositorNodeGlare" not in source
    assert "CompositorNodeHueSat" in source
    assert "CompositorNodeBrightContrast" in source
    assert "NodeGroupOutput" in source

    assert (
        "scene.compositing_node_group = tree"
        in source
    )

    assert (
        'type="CompositorNodeTree"'
        in source
    )

    assert (
        'name="Image"'
        in source
    )

    assert (
        'in_out="OUTPUT"'
        in source
    )

    assert "CompositorNodeComposite" not in source


def test_clean_cel_compositor_uses_stable_grade_nodes() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert "CompositorNodeGlare" not in source
    assert "CompositorNodeHueSat" in source
    assert "CompositorNodeBrightContrast" in source
    assert 'hue_sat.inputs[' in source
    assert '"Saturation"' in source
    assert "1.08" in source
    assert '"Value"' in source
    assert "0.98" in source
    assert '"Contrast"' in source
    assert "6.0" in source


def test_style_proof_renders_clean_cel_composite() -> None:
    source = PROOF.read_text(
        encoding="utf-8"
    )

    assert "render_composited(" in source

    assert (
        "STUDIO_COMPOSITING=CLEAN_CEL"
        in source
    )

    assert (
        "BLENDER_COMPOSITOR_NODES"
        in source
    )

    assert (
        "DEFERRED_BLENDER_5_2"
        in source
    )

    assert (
        "STUDIO_COMPOSITE_PATH="
        in source
    )


def test_executor_has_bounded_anime_camera_presets() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert "CameraPresentationProfile.ANIME_CINEMATIC" in source
    assert "ANIME_CAMERA_PRESETS" in source
    assert '"wide_establishing"' in source
    assert '"medium_hero"' in source
    assert '"close_intense"' in source
    assert "camera.data.lens" in source
    assert "camera.data.shift_x" in source
    assert "camera.data.shift_y" in source


def test_anime_camera_rejects_unknown_framing() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    assert (
        "Unsupported anime camera framing:"
        in source
    )

    assert (
        "preset = ANIME_CAMERA_PRESETS.get("
        in source
    )


def test_style_proof_renders_anime_camera_presentation() -> None:
    source = PROOF.read_text(
        encoding="utf-8"
    )

    assert "render_anime_camera(" in source
    assert 'framing="medium_hero"' in source

    assert (
        "STUDIO_CAMERA_PRESENTATION="
        in source
    )

    assert "ANIME_CINEMATIC" in source
    assert "STUDIO_CAMERA_FRAMING=" in source
    assert "STUDIO_CAMERA_LENS_MM=" in source
    assert "STUDIO_CAMERA_SHIFT_X=" in source
    assert "STUDIO_CAMERA_SHIFT_Y=" in source
    assert "STUDIO_CAMERA_PATH=" in source

def test_visual_fidelity_v2_adds_graphic_form_separation() -> None:
    source = EXECUTOR.read_text(
        encoding="utf-8"
    )

    required = (
        "shading.show_cavity = True",
        "StudioBackgroundBevel",
        'obj.rotation_euler[2] = 0.035',
        'obj.rotation_euler[2] = -0.035',
        "style.palette.ink",
    )

    for token in required:
        assert token in source
