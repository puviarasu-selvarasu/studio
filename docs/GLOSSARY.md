# Studio - Glossary

## Studio

The local-first AI-assisted animation production system.

Studio combines AI planning with deterministic Python-controlled animation and
Blender execution.

---

## Director

The logical AI production role responsible for deciding what should happen in
a scene or shot.

Responsibilities may include:

- staging
- composition
- camera intent
- pacing
- emotional intent
- high-level action
- visual mode
- animation strategy
- motion budget

The Director does not directly control Blender.

---

## Director Plan

A structured representation of cinematic and narrative intent.

It sits between creative input and the Animator.

Conceptually:

    Creative Intent
        ->
    Director Plan
        ->
    Animator

It is higher-level than Animation Plan and Animation IR.

---

## Animator

The logical AI production role responsible for deciding how characters and
camera should perform the Director's intent.

Responsibilities may include:

- action selection
- poses
- timing
- gaze
- head movement
- eye movement
- body movement
- facial expression
- transitions
- acting
- camera animation

The Animator may request only supported production capabilities.

---

## Animation Plan

A structured representation of character and camera performance.

It sits between Director Plan and Animation IR.

Conceptually:

    Director Plan
        ->
    Animation Plan
        ->
    Animation IR

Animation Plan describes performance rather than raw Blender operations.

---

## Animation IR

Animation Intermediate Representation.

The execution-oriented structured representation between animation planning
and deterministic execution.

Current concepts include:

- scene identifier
- scene duration
- character
- action
- action start time
- action duration

Animation IR is intentionally smaller than the complete creative model.

---

## Trust Boundary

The boundary where AI-generated structured intent becomes eligible for
deterministic execution.

Studio's critical trust boundary is:

    Animation IR
        ->
    Structural Validation
        ->
    Capability Validation
        ->
    Deterministic Toolkit

AI-generated Python must never cross this boundary.

---

## Structural Validation

Validation of the internal correctness of structured animation data.

Examples include:

- required identifiers
- positive duration
- valid action timing
- actions fitting inside scene duration

Structural validation does not determine whether a character actually supports
an action.

---

## Capability Registry

The authoritative registry describing which deterministic actions are supported
by a character or production asset.

The registry prevents AI planning from inventing unsupported executable
behavior.

---

## Capability Validation

Validation that requested actions exist in the Capability Registry.

An unsupported action causes a controlled failure before Blender execution.

---

## Animation Toolkit

The deterministic Python-controlled animation layer.

It translates validated animation intent into trusted Blender operations.

The toolkit grows progressively from low-level Blender control to reusable
character acting and advanced choreography.

---

## Blender Adapter

Infrastructure responsible for controlled interaction with Blender.

It may:

- launch Blender
- pass trusted Studio-owned scripts/data
- collect results
- translate process failures

It must not accept arbitrary AI-generated Python.

---

## Limited Animation

A production approach that intentionally concentrates movement on the elements
needed to communicate a shot.

Studio treats limited animation as a first-class production strategy rather
than a quality defect.

Examples include:

- held poses
- key poses
- reusable cycles
- reaction shots
- camera movement over still artwork
- selective facial movement
- impact frames

---

## Animation Strategy

The broad production technique selected for a shot.

Potential strategies include:

- HOLD
- KEY_POSE
- REACTION
- DIALOGUE
- CAMERA_OVER_STILL
- PAN_BACKGROUND
- LOOP
- WALK_CYCLE
- RUN_CYCLE
- PARALLAX
- SILHOUETTE
- MONTAGE
- IMPACT_FRAME
- ACTION
- HERO_ACTION

---

## Motion Budget

The amount of animation effort intentionally allocated to a shot.

Motion budget may depend on:

- narrative importance
- emotional importance
- shot duration
- required movement
- visual mode
- available capabilities
- production cost

---

## Hero Animation

Animation receiving greater motion/detail investment because the shot is
especially important visually, emotionally, or narratively.

Hero animation is selective rather than the default for every shot.

---

## 2D Mode

A production mode emphasizing flat or illustrated presentation.

Potential uses include:

- close-ups
- dialogue
- emotional acting
- held poses
- graphic compositions
- impact frames

---

## 2.5D Mode

A production mode combining layered 2D presentation with depth and controlled
camera movement.

Potential uses include:

- parallax
- rooms
- streets
- corridors
- layered environments

---

## Hybrid Mode

A production mode combining stylized 2D and 3D elements.

Potential uses include:

- complex perspective
- vehicles
- battles
- action
- complex camera movement
- effects

---

## Character Identity

The persistent production identity of a character.

Identity should remain stable even when visual presentation changes.

---

## Character Variant

A particular approved presentation of a Character Identity.

Variants may change:

- costume
- hairstyle
- physique
- age presentation
- accessories
- project-specific styling

---

## Rig Profile

Metadata describing the known animation structure and controls of a rigged
character asset.

---

## World

A reusable production-level environment context containing one or more
Locations.

---

## Location

A reusable place within a World.

A Location may reference:

- environment assets
- props
- spawn points
- camera anchors
- lighting presets

---

## Shot

The smallest primary cinematic production unit.

Studio should render and recover work at shot-level boundaries where practical.

---

## Scene

A narrative unit containing one or more related shots.

---

## Sequence

A collection of related scenes forming a larger narrative movement.

---

## Episode

A long-form production containing sequences.

---

## Project

The highest-level Studio production container.

Conceptually:

    Project
        ->
    Episode
        ->
    Sequence
        ->
    Scene
        ->
    Shot

---

## Proxy Render

A low-cost render used for inspection before expensive final rendering.

Proxy rendering is especially important on constrained hardware.

---

## Voice Actor Agent

A future logical production role responsible for dialogue-performance intent.

The Voice Actor Agent manages performance decisions.

The TTS engine generates the actual waveform.

---

## Voice Profile

Persistent configuration representing the intended voice identity of a
character.

---

## Music Director Agent

A future logical production role responsible for music and ambience intent.

It plans cues rather than being permanently coupled to one music-generation
engine.

---

## Vertical Slice

A small end-to-end production path proving that architecture works in reality.

Example:

    hardcoded plan
        ->
    Animation IR
        ->
    validation
        ->
    toolkit
        ->
    Blender
        ->
    rendered shot

Studio prioritizes vertical slices over broad unproven feature development.

---

## Deterministic Execution

Execution where validated inputs map to controlled known operations rather than
arbitrary model-generated code.

Deterministic execution is the foundation beneath Studio's AI layers.

---

## Local-First

Studio is designed so its core production workflow can operate using local
software and local compute without requiring paid cloud APIs.

Replaceable cloud integrations may be considered later, but they are not core
dependencies.

---

## Legacy Lesson Pipeline

The previous educational-content path containing concepts such as:

- Lesson
- ContentScene
- LessonGenerator
- lesson JSON

It remains temporarily for migration safety.

New animation functionality must not depend on it.