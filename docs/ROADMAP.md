# Studio - Roadmap

## 1. Roadmap Principle

Studio is developed through small, testable vertical slices.

The roadmap follows one rule:

> Never add autonomous AI behavior before the deterministic capability it
> depends on has been proven.

The development direction is:

    deterministic execution
        ->
    deterministic animation
        ->
    AI Animator
        ->
    AI Director
        ->
    reusable production systems
        ->
    longer productions

The roadmap is capability-driven rather than deadline-driven.

A phase is complete only when its verification boundary passes.

---

## 2. Completed Foundation

### Phase 0 - Repository Foundation

Status: COMPLETE

Established:

- Python project
- repository structure
- virtual environment
- test infrastructure
- modular kernel foundation
- Ports and Adapters direction

---

### Phase 1.1 - Animation IR

Status: COMPLETE

Established:

- AnimationAction
- CharacterAnimation
- AnimationScene
- structural validation
- automated tests

Animation IR became the initial deterministic execution representation.

---

### Phase 1.2 - Content Domain

Status: COMPLETE / LEGACY

Established:

- ContentScene
- Lesson
- content validation

This functionality belongs to the previous educational-product direction.

It remains temporarily for migration safety but is not part of new animation
development.

---

### Phase 1.3 - Lesson JSON Boundary

Status: COMPLETE / LEGACY

Established structured Lesson JSON parsing and validation.

This remains covered by tests but is no longer an active development path.

---

### Phase 1.4 - Local LLM Adapter

Status: COMPLETE

Established:

- LLMPort
- OllamaAdapter
- controlled adapter failures
- local model integration boundary

The adapter remains part of the new Studio architecture.

---

### Phase 1.5 - Lesson Generator

Status: COMPLETE / LEGACY

Established the previous Lesson-generation application flow.

It remains temporarily but must not be extended.

---

### Phase 1.6 - Capability Registry

Status: COMPLETE

Established:

- CharacterCapability
- CapabilityRegistry
- capability loading
- capability validation
- controlled unsupported-action failure

This is a core foundation for the animation system.

---

## 3. Phase 2.0 - Architectural Pivot

Status: IN PROGRESS

Purpose:

Transition Studio from the previous FunLearn-first direction into one focused
AI-assisted animation production system.

### Phase 2.0A - Baseline Verification

Status: COMPLETE

Verified:

- Python 3.11.9 virtual environment
- pytest
- complete regression suite
- clean repository baseline

### Phase 2.0B - Architecture Inspection

Status: COMPLETE

Reviewed:

- README
- vision
- architecture
- roadmap
- decisions
- glossary
- project entry point
- Python configuration
- kernel structure

### Phase 2.0C - README Pivot

Status: COMPLETE

README now describes:

- focused Studio product
- Director / Animator architecture
- Animation IR trust boundary
- deterministic Blender execution
- 2D / 2.5D / hybrid visual direction
- limited-animation philosophy
- legacy Lesson/Content boundary

### Phase 2.0D - Architecture Documentation Pivot

Status: IN PROGRESS

Update:

- VISION.md
- ARCHITECTURE.md
- ROADMAP.md
- DECISIONS.md
- GLOSSARY.md

No production functionality is added during this checkpoint.

### Phase 2.0E - Pivot Verification

Planned verification:

- complete pytest regression
- documentation diff inspection
- git diff --check
- explicit staged-file inspection
- clean documentation commit

### Phase 2.0F - Legacy Isolation Review

Review legacy:

- Lesson
- ContentScene
- LessonGenerator
- lesson JSON
- FunLearn-specific packages

Do not delete them during the architecture-documentation checkpoint.

Any removal must occur separately with regression verification.

---

## 4. Phase 2.1 - Minimal Desktop UI

Goal:

Create the smallest useful Studio desktop shell.

Likely technology:

- PySide6
- Qt

Initial UI:

- main window
- scene/story text input
- Direct button
- Animate button
- status area
- preview placeholder

Rules:

- UI calls Application services
- UI does not directly control Blender
- UI contains no production business logic
- UI remains intentionally minimal

Success criterion:

> Studio launches as a desktop application with a thin working UI boundary.

This phase does not require AI animation.

---

## 5. Phase 2.2 - Blender Bridge Proof

Goal:

Prove Python can deterministically control the installed Blender runtime.

Initial operations:

- locate Blender executable
- launch Blender headlessly
- execute a trusted Studio-owned Blender script
- create or load a simple scene
- create an object
- manipulate a transform
- configure a camera
- render a test frame
- return a controlled success/failure result

No LLM output is involved.

Success criterion:

> Studio launches Blender through a controlled adapter and produces a known
> deterministic render.

This is the first real Studio-to-Blender integration milestone.

---

## 6. Phase 2.3 - Animation Toolkit Level 0

Goal:

Build deterministic Blender control primitives.

Initial toolkit capabilities may include:

- place_object
- move_object
- rotate_object
- set_camera
- move_camera
- insert_keyframe
- render_shot

Requirements:

- explicit inputs
- deterministic behavior
- controlled failures
- no arbitrary code execution
- integration tests where practical

Success criterion:

> A hardcoded Studio plan produces a short animated object/camera shot through
> reusable deterministic tools.

---

## 7. Phase 2.4 - First Controllable Character

Goal:

Move from generic objects to one reusable rigged character.

Scope:

- one approved test character
- known rig structure
- character loading
- deterministic placement
- deterministic pose control
- deterministic animation
- camera framing
- proxy rendering

Do not attempt a full character-generation system yet.

Success criterion:

> Studio loads one reusable rigged character and animates it without manual
> keyframing during execution.

---

## 8. Phase 2.5 - Animation Toolkit Level 1

Goal:

Implement a small useful character animation vocabulary.

Initial target capabilities:

- idle
- walk
- turn
- look_at
- blink
- basic talk
- basic expressions

Introduce limited-animation primitives where useful.

Potential production strategies:

- HOLD
- KEY_POSE
- REACTION
- DIALOGUE
- CAMERA_OVER_STILL
- LOOP
- WALK_CYCLE
- PARALLAX

The Capability Registry must reflect only functionality that genuinely exists.

Success criterion:

> The test character performs multiple validated reusable actions through the
> deterministic toolkit.

---

## 9. Phase 2.6 - Deterministic 5-10 Second Scene

Goal:

Combine existing deterministic capabilities into a coherent short scene.

The scene should demonstrate several of:

- character placement
- held pose
- movement
- expression
- gaze
- camera
- action transition
- limited-animation strategy
- proxy render

No AI planning is required.

Success criterion:

> A hardcoded plan creates a coherent 5-10 second Blender animation without
> manual keyframing during execution.

This is the key prerequisite for introducing the Animator Agent.

---

## 10. Phase 3 - AI Animator

Goal:

Use the local LLM to convert high-level animation direction into structured
performance intent.

Initial flow:

    Human / Hardcoded Director Direction
        ->
    Animator Agent
        ->
    Animation Plan
        ->
    Animation IR
        ->
    Structural Validation
        ->
    Capability Validation
        ->
    Deterministic Toolkit
        ->
    Blender

The Animator must not generate Python.

The Animator must not generate raw Blender commands.

Unsupported actions fail before execution.

Success criterion:

> Natural-language animation direction is converted into valid executable
> animation using only registered capabilities.

---

## 11. Phase 4 - AI Director

Goal:

Introduce structured cinematic planning.

Initial Director responsibilities:

- shot intent
- duration
- character involvement
- emotional intent
- staging
- composition
- camera intent
- high-level action
- visual mode
- animation strategy
- motion budget

Flow:

    Story / Scene Intent
        ->
    Director Agent
        ->
    Director Plan
        ->
    Animator Agent
        ->
    Animation Plan
        ->
    Animation IR
        ->
    Blender

Success criterion:

> The Director produces a structured shot plan that the Animator can transform
> into executable animation.

---

## 12. Phase 5 - First AI-Produced 5-15 Second Scene

Goal:

Prove the complete creative-to-render pipeline.

Target flow:

    Creator
        ->
    Director
        ->
    Animator
        ->
    Validation
        ->
    Toolkit
        ->
    Blender
        ->
    Proxy Render
        ->
    Human Review

Success criterion:

> Studio produces a coherent 5-15 second scene from high-level creative input
> using local AI planning and deterministic execution.

This is the first major product proof.

---

## 13. Phase 6 - Character Identity Foundation

Goal:

Separate persistent character identity from individual visual variants.

Introduce only the minimum concepts required for:

- CharacterIdentity
- CharacterVariant
- rig reference
- capability reference
- visual asset reference

Success criterion:

> One character identity can safely reference more than one approved appearance
> variant without losing its production identity.

---

## 14. Phase 7 - Character Production Pipeline

Goal:

Make reusable character preparation more systematic.

Potential capabilities:

- character asset registration
- rig validation
- pose library
- expression library
- animation clip library
- costume variants
- hairstyle variants
- asset preview
- character metadata

Real-person-inspired characters may be explored only after the reusable
identity pipeline is stable.

Success criterion:

> Reusable characters can be prepared, validated, selected, and animated across
> multiple scenes.

---

## 15. Phase 8 - World and Prop Foundation

Goal:

Create reusable production environments.

Potential concepts:

- World
- Location
- environment asset
- props
- spawn points
- camera anchors
- lighting presets

Support may progressively include:

- 2D backgrounds
- layered 2D
- 2.5D environments
- stylized 3D
- hybrid environments

Success criterion:

> A reusable location can be loaded and used by multiple shots without being
> rebuilt manually.

---

## 16. Phase 9 - Voice Actor Agent

Goal:

Add structured dialogue performance.

Initial flow:

    Dialogue
        ->
    Voice Actor Agent
        ->
    Voice Performance Plan
        ->
    TTSPort
        ->
    Local TTS
        ->
    Audio

Initial implementation may use Piper.

Requirements:

- persistent character voice profiles
- controlled local generation
- timing metadata
- replaceable TTS adapter

Success criterion:

> Multiple characters can produce distinguishable persistent dialogue voices
> through one coordinated voice-production workflow.

---

## 17. Phase 10 - Acting, Dialogue and Lip Sync

Goal:

Connect voice timing with character performance.

Potential capabilities:

- dialogue timing
- mouth cues
- basic lip sync
- blink scheduling
- gaze
- head movement
- facial expressions
- breathing
- micro-idles
- dialogue camera strategies

Target milestone:

> Produce a coherent 30-60 second dialogue or acting scene.

---

## 18. Phase 11 - Multilingual Voice

Goal:

Support alternate dialogue tracks after single-language performance works.

Potential capabilities:

- translated dialogue track
- language-specific voice profile
- timing adaptation
- subtitle track
- alternate audio assembly

Do not couple the animation architecture to one TTS engine.

---

## 19. Phase 12 - Music Director

Goal:

Add structured music and ambience planning.

Initial focus:

- cue planning
- ambience
- reusable music
- procedural/MIDI possibilities
- dialogue-aware placement
- FFmpeg mixing

High-quality local generative music is optional and replaceable.

Success criterion:

> Studio can plan and assemble intentional music/ambience cues around an
> animated scene.

---

## 20. Phase 13 - Review / Critic Loop

Goal:

Introduce structured review only after animation and rendering are reliable.

Potential loop:

    render proxy
        ->
    inspect
        ->
    identify issue
        ->
    propose structured correction
        ->
    validate
        ->
    rerender

Initial review may remain human-driven.

Machine-assisted review must never bypass deterministic validation.

---

## 21. Phase 14 - Multi-Scene Production

Goal:

Move from isolated scenes to connected narrative production.

Introduce as required:

- Project
- Episode
- Sequence
- Scene
- Shot
- production manifests
- persisted status
- recovery
- caching
- continuity state

Success criterion:

> Multiple scenes can be produced, recovered, and assembled without requiring
> the complete production in memory.

---

## 22. Phase 15 - UI Maturation

Goal:

Turn the minimal desktop shell into a practical production interface.

Potential areas:

- project browser
- scene editor
- shot list
- character browser
- world browser
- production status
- render queue
- preview
- voice controls
- export
- error reporting

The UI remains an adapter over Application services.

---

## 23. Phase 16 - Production Hardening

Focus:

- recovery
- logging
- caching
- deterministic asset references
- project portability
- render retry
- production manifests
- error reporting
- configuration
- performance profiling
- regression testing

The goal is reliability rather than new creative features.

---

## 24. Phase 17 - Advanced Animation Capabilities

Potential additions:

- richer acting
- object interaction
- procedural gaze
- procedural head movement
- secondary motion
- advanced facial animation
- action composition
- root motion
- two-character interactions
- combat primitives
- group choreography
- advanced camera choreography
- effects

Capabilities are added only when deterministic implementations exist.

---

## 25. Phase 18 - Approximately 10-Minute Production

Goal:

Prove that the architecture scales beyond short demonstrations.

Requirements will likely include:

- reusable characters
- reusable locations
- continuity
- shot recovery
- proxy workflow
- voice
- music
- production manifests
- sequential resource scheduling
- reliable final assembly

Success criterion:

> Studio can complete and recover a coherent approximately 10-minute production
> using shot-based execution.

---

## 26. Phase 19 - Full Episode Production

Long-term target:

Produce original episode-length narrative animation through reusable,
recoverable production workflows.

This phase depends on evidence from shorter productions.

The architecture must not assume that full automation equals zero human review.

The intended model is:

    human creative ownership
        +
    AI planning
        +
    deterministic animation tools
        +
    reusable assets
        +
    shot-based rendering
        +
    structured review

---

## 27. Deferred Until Proven Necessary

Do not introduce these merely because they sound scalable:

- microservices
- Docker-based distributed architecture
- Kubernetes
- cloud render farms
- paid AI APIs as core dependencies
- event buses
- distributed queues
- complex databases
- multi-user collaboration infrastructure
- frame-by-frame generative video
- giant local language models

They may be reconsidered only when a measured requirement justifies them.

---

## 28. Immediate Path

The immediate engineering path after the architecture pivot is:

    Phase 2.1
    Minimal Desktop UI
        |
        v
    Phase 2.2
    Blender Bridge
        |
        v
    Phase 2.3
    Animation Toolkit Level 0
        |
        v
    Phase 2.4
    First Controllable Character
        |
        v
    Phase 2.5
    Animation Toolkit Level 1
        |
        v
    Phase 2.6
    Deterministic 5-10 Second Scene
        |
        v
    Phase 3
    AI Animator
        |
        v
    Phase 4
    AI Director
        |
        v
    Phase 5
    First AI-Produced 5-15 Second Scene

Do not skip the deterministic milestones to reach the AI stages faster.

Those deterministic milestones are what make the AI stages safe, testable, and
useful.