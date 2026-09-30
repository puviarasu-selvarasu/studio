# Studio - AI Context

## Purpose

This file is a compact handoff document for AI coding assistants working on
Studio.

Read this before proposing architectural or implementation changes.

For full detail also consult:

- README.md
- docs/VISION.md
- docs/ARCHITECTURE.md
- docs/ROADMAP.md
- docs/DECISIONS.md
- docs/GLOSSARY.md

---

## Product

Studio is a local-first AI-assisted animation production system for original
2D, 2.5D, and hybrid anime-style narrative animation.

It is not primarily a generative-video application.

It combines AI planning with deterministic Python-controlled animation and
Blender execution.

Core rule:

> AI decides WHAT. Python decides HOW. Blender executes.

---

## Architecture

Studio uses a modular monolith with Hexagonal Architecture / Ports and
Adapters.

Logical dependency direction:

    Infrastructure
        ->
    Application
        ->
    Domain

Domain code must remain independent of:

- Blender
- Ollama
- Piper
- FFmpeg
- PySide6
- operating-system infrastructure

---

## Core Production Flow

Target architecture:

    Creator
        ->
    Desktop UI
        ->
    Director
        ->
    Director Plan
        ->
    Animator
        ->
    Animation Plan
        ->
    Animation IR
        ->
    Structural Validation
        ->
    Capability Validation
        ->
    Deterministic Animation Toolkit
        ->
    Blender
        ->
    Render
        ->
    Review
        ->
    Audio / Assembly

Do not collapse Director Plan, Animation Plan, and Animation IR into one giant
schema.

---

## Security / Trust Rule

Never implement:

    LLM
        ->
    arbitrary Python
        ->
    exec
        ->
    Blender

AI-generated Python and arbitrary Blender commands must not be executed.

Animation IR is the AI-to-execution trust boundary.

Unsupported AI-requested actions must fail capability validation.

---

## Director

Director owns high-level cinematic intent.

Examples:

- scene/shot interpretation
- staging
- composition
- camera intent
- pacing
- emotional intent
- high-level action
- visual mode
- animation strategy
- motion budget

Director does not manipulate Blender directly.

---

## Animator

Animator owns performance intent.

Examples:

- action selection
- poses
- timing
- gaze
- head/eye movement
- facial expression
- body movement
- transitions
- acting
- camera animation

Animator may use only deterministic capabilities actually implemented by
Studio.

---

## Deterministic Animation Toolkit

Planned capability progression:

Level 0:
- Blender control
- object placement
- transforms
- camera
- keyframes
- rendering

Level 1:
- idle
- walk
- turn
- look_at
- blink
- basic talk
- basic expressions

Level 2:
- basic acting
- sit/stand
- point/wave
- object interaction
- emotional poses

Level 3:
- action composition
- transitions
- root motion
- combined body/facial actions

Level 4:
- procedural gaze
- head motion
- breathing
- micro-idles
- structured pose generation

Level 5:
- review/revision loop

Level 6:
- advanced interaction
- combat
- group choreography
- advanced camera choreography

Do not advertise a capability before deterministic implementation exists.

---

## Limited Animation

Studio intentionally supports production strategies such as:

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

The goal is minimum motion required to communicate the shot effectively.

---

## Long-Form Hierarchy

    Project
        ->
    Episode
        ->
    Sequence
        ->
    Scene
        ->
    Shot

Rendering should be recoverable at small boundaries.

Never design the system so an entire episode must remain in memory.

---

## Hardware Constraints

Current development machine is constrained.

Assume:

- Windows 11
- 8 GB RAM
- CPU-first workload
- Intel UHD 620
- AMD Radeon R7 M460 approximately 2 GB
- Python 3.11.9
- Blender 5.2 LTS
- Ollama
- llama3.2:3b
- Piper
- FFmpeg

Heavy workloads should initially execute sequentially.

Prefer:

- proxy rendering
- shot-based rendering
- modest development resolution
- cached assets
- reusable animation
- lightweight local models

Do not introduce infrastructure requiring high-end hardware to prove the core
pipeline.

---

## Current Implemented Foundation

Implemented and tested:

- repository foundation
- modular kernel
- Animation IR
- structural Animation IR validation
- LLMPort
- OllamaAdapter
- Capability Registry
- capability loader
- capability validation
- automated pytest coverage

The existing regression suite currently contains 51 tests.

Do not claim tests pass unless terminal output from the developer confirms it.

---

## Legacy Code

The previous FunLearn educational path is legacy.

Legacy concepts include:

- Lesson
- ContentScene
- LessonGenerator
- lesson JSON

Rules:

- preserve temporarily
- keep tests passing
- do not extend
- do not make new animation functionality depend on it
- remove only in a separate verified checkpoint

---

## Immediate Development Order

Current direction:

    architecture pivot
        ->
    minimal PySide6 desktop UI
        ->
    Blender bridge
        ->
    Animation Toolkit Level 0
        ->
    first controllable rigged character
        ->
    Animation Toolkit Level 1
        ->
    deterministic 5-10 second scene
        ->
    local AI Animator
        ->
    local AI Director
        ->
    first AI-produced 5-15 second scene

Do not skip deterministic milestones merely to demonstrate AI sooner.

---

## Future Systems

After the visual animation pipeline is proven:

- Character Identity / Character Variant
- reusable character pipeline
- worlds and locations
- props
- Voice Actor Agent
- persistent voice profiles
- lip sync
- multilingual voice
- Music Director Agent
- review / critic loop
- multi-scene production
- continuity
- advanced animation
- battle/group choreography
- long-form production

Do not implement these prematurely.

---

## Character Rule

Character identity and appearance variants are different concepts.

Conceptually:

    CharacterIdentity
        ->
    CharacterVariant
        ->
    Rig / Visual Asset
        ->
    Capabilities

Do not regenerate persistent character identity independently for every shot.

---

## World Rule

Reusable locations should eventually contain structured references to:

- environment
- props
- spawn points
- camera anchors
- lighting presets

World systems are later than the first working character-animation pipeline.

---

## Voice Rule

One logical Voice Actor Agent may manage multiple persistent character voices.

The agent controls performance intent.

The TTS adapter produces audio.

Do not couple Studio permanently to Piper.

---

## Music Rule

Music direction and music generation are separate concerns.

Music Director plans:

- cue intent
- ambience
- motifs
- timing
- transitions
- dialogue-aware placement

Actual music implementation remains replaceable.

---

## Development Discipline

When modifying Studio:

1. inspect before editing
2. make the smallest coherent change
3. add or update tests when behavior changes
4. run focused tests
5. run full regression before commit
6. inspect git status
7. inspect diff
8. run git diff --check
9. stage explicit files only
10. inspect staged files
11. commit only after verification

Never use `git add .` for checkpoint commits.

Avoid destructive Git operations unless explicitly justified.

Do not claim local success until actual terminal output confirms it.

---

## Engineering Priorities

Prefer:

- working vertical slices
- simple abstractions
- deterministic behavior
- explicit schemas
- explicit failure boundaries
- reusable assets
- testability
- recoverability
- local operation

Avoid:

- premature microservices
- unnecessary Docker
- unnecessary databases
- distributed systems without measured need
- giant schemas
- speculative abstractions
- arbitrary AI code execution
- implementing future agents before deterministic tools exist

---

## Next Technical Milestone

After the architecture-documentation pivot is committed:

> Build the smallest Studio desktop shell, then prove a controlled deterministic
> Studio-to-Blender bridge.

The first major animation proof remains:

> A deterministic Studio plan drives Blender to produce a short animation
> without manual keyframing during execution.