# Studio - Architecture

## 1. Architectural Style

Studio uses a modular monolith with Hexagonal Architecture
(Ports and Adapters).

The architecture is intentionally designed for:

- one primary developer
- local-first execution
- constrained hardware
- deterministic animation
- replaceable external tools
- incremental vertical-slice development

The three logical layers are:

1. Domain
2. Application
3. Infrastructure

Dependencies point inward.

    Infrastructure
         |
         v
     Application
         |
         v
       Domain

Domain code must never depend on Blender, Ollama, Piper, FFmpeg, the desktop
UI, or operating-system-specific infrastructure.

---

## 2. Core Production Rule

The central architectural rule is:

> AI decides WHAT. Python decides HOW. Blender executes.

AI is used for structured planning and creative decision making.

AI-generated output must never be treated as executable code.

Python owns deterministic execution.

Blender owns scene manipulation, animation, and rendering.

---

## 3. Production Flow

The long-term production flow is:

    Creator
       |
       v
    Desktop UI
       |
       v
    Application Layer
       |
       v
    Director Agent
       |
       v
    Director Plan
       |
       v
    Animator Agent
       |
       v
    Animation Plan
       |
       v
    Animation IR
       |
       v
    Structural Validation
       |
       v
    Capability Validation
       |
       v
    Animation Toolkit
       |
       v
    Blender Adapter
       |
       v
    Blender
       |
       v
    Proxy / Final Render
       |
       v
    Audio Production
       |
       v
    FFmpeg Assembly
       |
       v
    Human Review

Not every stage exists yet.

Architecture describes the intended dependency boundaries, not permission to
implement every stage immediately.

---

## 4. Domain Layer

The Domain contains pure production concepts and rules.

Current domain concepts include:

- AnimationScene
- CharacterAnimation
- AnimationAction
- CapabilityRegistry
- CharacterCapability

Future domain concepts may include:

- DirectorPlan
- ShotPlan
- AnimationPlan
- CharacterIdentity
- CharacterVariant
- RigProfile
- World
- Location
- ProductionManifest
- VoiceIdentity
- MusicCue

These concepts should be introduced only when their corresponding vertical
slice requires them.

Domain code must not import:

- Blender
- bpy
- Ollama
- requests
- Piper
- FFmpeg
- PySide6
- subprocess-specific infrastructure
- operating-system integration

Domain behavior should remain testable using normal Python and pytest.

---

## 5. Application Layer

The Application layer coordinates use cases.

It decides:

- which production stage executes next
- which port is required
- when validation occurs
- how domain objects move between stages
- how failures are translated
- when resources should be released
- when a production stage may continue

Application services depend on ports and domain concepts.

They must not construct infrastructure adapters internally.

Conceptual future services may include:

- DirectorService
- AnimatorService
- AnimationExecutionService
- RenderShotService
- VoicePerformanceService
- ProductionAssemblyService

Names are illustrative.

Do not create these abstractions until a real use case requires them.

---

## 6. Infrastructure Layer

Infrastructure contains integrations with external systems.

Examples include:

- OllamaAdapter
- BlenderAdapter
- PiperAdapter
- FFmpegAdapter
- filesystem repositories
- process launchers

Infrastructure may depend on external libraries and operating-system behavior.

Infrastructure translates external failures into controlled application-level
failures.

Raw implementation details should not leak into the Domain.

---

## 7. Ports

Ports define contracts required by the application.

Existing ports include:

- LLMPort
- TTSPort
- AnimatorPort
- RendererPort

Ports are represented using Python Protocols where appropriate.

A port exists because the application requires a replaceable external
capability.

Do not create ports merely to satisfy an architectural pattern.

Existing ports may evolve as real animation workflows expose better
boundaries.

---

## 8. Planning Representation Levels

Studio separates creative planning from executable animation.

Three representation levels are expected.

### 8.1 Director Plan

The Director Plan describes cinematic and narrative intent.

It may eventually contain:

- sequence
- scene
- shot
- characters
- location
- emotional intent
- staging
- composition
- camera intent
- high-level action
- visual mode
- animation strategy
- motion budget
- duration

It answers:

> What should the audience see and feel?

The Director Plan is not directly executable by Blender.

### 8.2 Animation Plan

The Animation Plan describes performance.

It may eventually contain:

- actions
- poses
- timing
- gaze
- eye movement
- head movement
- facial expression
- body movement
- transitions
- action composition
- camera animation
- acting choices

It answers:

> How should the characters and camera perform this shot?

The Animation Plan is still higher level than Blender operations.

### 8.3 Animation IR

Animation IR is execution-oriented.

Current Animation IR contains:

- scene identifier
- scene duration
- character identifier
- action
- action start time
- action duration

It answers:

> Which supported animation operations must execute, and when?

Animation IR should remain deliberately smaller than the complete creative
representation.

Do not force screenplay, music, dialogue, world-building, or every cinematic
concept into Animation IR.

---

## 9. Trust Boundary

Animation IR is the critical AI-to-execution trust boundary.

The required flow is:

    AI / Structured Planner
            |
            v
       Structured Data
            |
            v
    Structural Validation
            |
            v
    Capability Validation
            |
            v
       Animation IR
            |
            v
    Animation Toolkit
            |
            v
     Blender Adapter
            |
            v
         Blender

No AI-generated Python is executed.

No AI-generated Blender command is executed directly.

No unsupported capability is silently invented.

Invalid plans fail before Blender execution.

---

## 10. Structural Validation

Structural validation answers questions such as:

- Is the scene identifier valid?
- Is scene duration positive?
- Is the character identifier valid?
- Is the action name valid?
- Is action timing valid?
- Does the action fit within the scene?

Structural validation does not decide whether a specific character knows how to
perform an otherwise valid action.

That belongs to capability validation.

---

## 11. Capability Validation

The Capability Registry defines executable vocabulary.

Example:

    character: momo

    supported actions:
        idle
        blink
        wave
        walk
        talk

If an animation plan requests an unsupported action, execution stops with a
controlled validation failure.

The system must never translate an unknown AI request into arbitrary animation.

The Capability Registry will expand as deterministic animation tools become
real.

Capabilities must follow implementation.

Implementation must not pretend to follow capabilities that do not exist.

---

## 12. Animation Toolkit

The Animation Toolkit is the deterministic layer between validated animation
intent and Blender-specific execution.

The toolkit grows incrementally.

### Level 0 - Blender Control

Examples:

- place_object
- move_object
- rotate_object
- set_camera
- move_camera
- insert_keyframe
- render_shot

### Level 1 - Basic Character Animation

Examples:

- idle
- walk
- turn
- look_at
- blink
- basic talk
- basic expressions

### Level 2 - Basic Acting

Examples:

- sit
- stand
- point
- wave
- pick_up
- put_down
- pose transitions
- emotional poses

### Level 3 - Animation Composition

Examples:

- walk + look
- walk + talk
- pose + expression
- body + facial animation
- action transitions
- root motion

### Level 4 - Procedural Animation

Examples:

- procedural gaze
- procedural head motion
- breathing
- micro-idles
- structured pose generation
- secondary motion

### Level 5 - Review and Revision

Conceptually:

    animate
       ->
    proxy render
       ->
    inspect
       ->
    identify issue
       ->
    revise
       ->
    rerender

This level is postponed until rendering and animation are reliable.

### Level 6 - Advanced Performance

Examples:

- multi-character interaction
- complex acting
- object interaction
- combat primitives
- group choreography
- advanced camera choreography

Each level depends on proven lower-level functionality.

---

## 13. Limited-Animation Strategy

Traditional limited-animation techniques are architectural production tools,
not merely visual decoration.

A shot may use strategies such as:

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

The Director eventually chooses the broad strategy.

The Animator translates that strategy into performance.

The deterministic toolkit executes available capabilities.

This allows Studio to concentrate motion where the audience notices it rather
than treating every frame as equally expensive.

---

## 14. Blender Boundary

Blender is an execution engine.

Blender is responsible for operations such as:

- loading production assets
- object placement
- transforms
- rig manipulation
- keyframes
- cameras
- Grease Pencil
- lighting
- toon/cel materials
- effects
- compositing
- proxy rendering
- final rendering

Creative planning must not be embedded inside Blender scripts.

Blender scripts should receive validated deterministic instructions.

This separation allows Blender execution to be tested and replaced without
changing AI planning contracts.

---

## 15. Visual Modes

Studio should eventually support three shot-level visual modes:

### 2D

Useful for:

- close-ups
- emotional acting
- held poses
- dialogue
- graphic compositions
- impact frames
- overlays

### 2.5D

Useful for:

- parallax
- corridors
- rooms
- streets
- layered environments
- controlled camera movement
- depth without fully realistic 3D presentation

### HYBRID

Useful for:

- perspective-heavy environments
- vehicles
- complex camera moves
- action
- battles
- effects
- shots combining stylized 3D with 2D overlays

A project does not need to choose only one mode.

The Director may eventually select the appropriate mode per shot.

---

## 16. Character Architecture

Character identity and character appearance are separate concepts.

Conceptually:

    CharacterIdentity
         |
         v
    CharacterVariant
         |
         v
      RigProfile
         |
         v
      Visual Asset
         |
         v
     Capabilities

CharacterIdentity represents persistent recognizable identity.

CharacterVariant represents changeable presentation such as:

- costume
- hairstyle
- physique
- age presentation
- accessories
- project-specific styling

The rig and visual implementation may change without changing identity.

This architecture also supports future real-person-inspired characters after
manual asset approval.

---

## 17. World Architecture

World assets are reusable.

Conceptually:

    World
      |
      v
    Location
      |
      +--> Environment
      |
      +--> Props
      |
      +--> Spawn Points
      |
      +--> Camera Anchors
      |
      +--> Lighting Presets

A location may be represented using:

- 2D artwork
- layered 2D
- 2.5D staging
- stylized 3D
- hybrid combinations

World infrastructure should not be implemented before basic character
animation and Blender execution work.

---

## 18. Voice Architecture

Voice is a later production layer.

The conceptual flow is:

    Director dialogue intent
          |
          v
    Voice Actor Agent
          |
          v
    Voice Performance Plan
          |
          v
       TTS Port
          |
          v
    Local TTS Adapter
          |
          v
       Audio File

One Voice Actor Agent may coordinate many character voices.

Voice identity must be persistent.

Example:

    character_a -> voice_profile_a
    character_b -> voice_profile_b
    narrator    -> voice_profile_c

Multilingual dubbing is postponed until single-language dialogue and timing are
reliable.

---

## 19. Music Architecture

Music direction and music generation are separate responsibilities.

Conceptually:

    Director emotional plan
          |
          v
    Music Director Agent
          |
          v
      Music Cue Plan
          |
          +--> reusable music
          +--> ambience
          +--> procedural/MIDI music
          +--> future local generation
          |
          v
       FFmpeg Mix

The Music Director plans intent.

The underlying audio-generation implementation remains replaceable.

High-quality local generative music is not a prerequisite for the core
animation system.

---

## 20. Production Hierarchy

Long-form production uses:

    Project
      |
      v
    Episode
      |
      v
    Sequence
      |
      v
    Scene
      |
      v
    Shot

Rendering and recovery occur at small production boundaries.

A failed shot should be rerenderable independently.

Intermediate results should be persisted to disk.

Production orchestration must eventually track status and dependencies without
requiring the entire episode in memory.

---

## 21. Continuity

Complex long-form stories require explicit state.

The LLM context window must not be the only continuity mechanism.

Future continuity information may include:

Character state:

- location
- alive/dead state where relevant to the story
- injuries
- clothing
- carried items
- relationships
- current objectives

World state:

- location ownership
- weather
- time
- damaged or destroyed structures
- available routes
- persistent environmental changes

Continuity storage is postponed until multi-scene production demonstrates the
need.

---

## 22. Battle and Crowd Architecture

Large groups must be controlled using high-level deterministic primitives.

Potential future primitives include:

- move_group
- formation_move
- battle_charge
- crowd_flee
- archer_volley
- march
- duel
- reusable_combat_exchange
- impact_event

An LLM should plan group intent rather than independently keyframing hundreds
of participants.

Perceived battle complexity should emerge from:

- reusable motion
- deterministic choreography
- camera selection
- editing
- silhouettes
- effects
- impact frames
- sound
- selective hero animation

---

## 23. Rendering Strategy

Rendering is shot-based.

Development uses inexpensive proxy renders before final renders.

Conceptually:

    Animation
       |
       v
    Proxy Render
       |
       v
    Review
       |
       v
    Final Shot Render
       |
       v
    Persist to Disk
       |
       v
    Release Resources

Final assembly is performed later using FFmpeg.

The initial system should favor inexpensive rendering modes suitable for the
available hardware.

---

## 24. Resource Scheduling

The initial execution policy is sequential.

Heavy processes should not intentionally compete for limited memory.

Conceptually:

    Ollama planning
        ->
    release model workload
        ->
    Blender execution/render
        ->
    release Blender workload
        ->
    TTS/audio
        ->
    FFmpeg assembly

This is primarily a hardware policy.

The architecture should remain capable of changing scheduling policy on more
powerful hardware without rewriting domain logic.

---

## 25. Desktop UI Boundary

The final product is not intended to remain command-line-only.

The likely desktop technology is PySide6/Qt for Python.

The UI is a thin adapter over application use cases.

Required dependency direction:

    Desktop UI
        |
        v
    Application
        |
        v
      Domain

The UI must not directly manipulate Blender.

The UI must not contain production business rules.

Initial UI scope should remain minimal:

- story/scene input
- Direct action
- Animate action
- status
- preview placeholder

The UI expands only after underlying application capabilities exist.

---

## 26. Failure Boundaries

Failures must remain explicit and controlled.

Examples include:

- invalid structured AI output
- unsupported capability
- unknown character
- Ollama unavailable
- Blender unavailable
- Blender process failure
- asset missing
- rig mismatch
- render failure
- TTS failure
- FFmpeg failure

Infrastructure adapters translate low-level failures.

Application services provide useful workflow-level failures.

Domain validation failures remain deterministic and testable.

---

## 27. Testing Strategy

### Unit Tests

Unit tests cover:

- domain behavior
- structural validation
- capability validation
- transformations
- application orchestration using fakes

They must not require Blender, Ollama, Piper, or FFmpeg.

### Integration Tests

Integration tests cover real boundaries such as:

- Ollama
- Blender
- Piper
- FFmpeg

External-process tests remain separate from the fast unit-test suite where
practical.

### Vertical-Slice Verification

Every major phase must eventually prove a real runnable path.

Examples:

    hardcoded plan
        ->
    Animation IR
        ->
    Blender
        ->
    rendered shot

and later:

    natural-language direction
        ->
    Animator Agent
        ->
    validated Animation IR
        ->
    Blender
        ->
    rendered shot

---

## 28. Legacy Boundary

The previous educational Lesson/Content pipeline is legacy functionality.

Current legacy areas include concepts such as:

- Lesson
- ContentScene
- LessonGenerator
- lesson JSON parsing
- FunLearn-specific application structure

During the architectural pivot:

- legacy code remains temporarily
- existing tests continue to pass
- new animation features must not depend on legacy concepts
- legacy functionality must not be expanded
- removal happens in a separate controlled checkpoint

This follows a gradual replacement strategy rather than mixing deletion with
new architecture.

---

## 29. Development Order

The development order is intentionally deterministic-first.

First:

    Hardcoded Director Plan
        ->
    Hardcoded Animation Plan
        ->
    deterministic tools

Then:

    Hardcoded Director Plan
        ->
    Local AI Animator
        ->
    deterministic tools

Then:

    Local AI Director
        ->
    Local AI Animator
        ->
    deterministic tools

This isolates failures and prevents autonomous planning from hiding weaknesses
in the execution layer.

---

## 30. Current Architectural Boundary

Already implemented:

- modular kernel
- Ports and Adapters foundation
- Animation IR
- Animation IR structural validation
- LLMPort
- OllamaAdapter
- Capability Registry
- capability loading
- capability validation
- automated unit tests

Not yet implemented:

- desktop UI
- Blender adapter
- deterministic animation toolkit
- rigged character execution
- Animation Plan
- Director Plan
- AI Animator
- AI Director
- character identity system
- world system
- voice production
- music production
- long-form orchestration

The immediate technical priority is the deterministic Blender vertical slice.

No higher-level autonomous system should bypass that milestone.