# Studio - Vision

## 1. Purpose

Studio is a local-first AI-assisted animation production system.

Its purpose is to allow a storyteller/software engineer to describe an original
story, scene, or performance at a high level and progressively transform that
creative intent into deterministic, reusable animation executed by Blender.

Studio does not replace Blender.

Studio provides the creative planning, production orchestration, validation,
automation, and reusable animation systems above Blender.

The core principle is:

> AI decides WHAT. Python decides HOW. Blender executes.

The creator remains responsible for storytelling, creative supervision, review,
and final approval.

---

## 2. Product Direction

Studio is being developed as one integrated animation production application.

The primary target is original narrative animation supporting:

- short scenes
- dialogue
- emotional acting
- multiple characters
- reusable characters
- reusable environments
- action
- travel
- political and dramatic scenes
- battles and large-scale events
- multi-scene stories
- episodes
- eventually long-form narrative productions

The system must grow toward long-form production through small proven vertical
slices rather than attempting full episode generation immediately.

The previous FunLearn educational-short concept is legacy functionality.

Existing Lesson and Content code remains temporarily for migration safety but
must not drive new architecture or feature development.

---

## 3. Visual Direction

Studio targets an original visual language combining traditional animation
production principles with modern digital presentation.

The system should support three production modes:

- 2D
- 2.5D
- HYBRID

A production may use different modes for different shots.

### Traditional influences

Studio should make deliberate use of:

- hand-drawn visual language
- strong silhouettes
- strong key poses
- held drawings and held poses
- limited animation
- animation on reduced exposures where appropriate
- expressive facial acting
- reusable cycles
- cel-style shading
- painted or illustrated-looking backgrounds
- impact frames
- selective motion
- deliberate composition
- economical television-animation techniques

### Modern presentation

Traditional animation principles are combined with:

- clean digital output
- modern cinematography
- controlled camera movement
- parallax
- depth
- modern color management
- lighting
- compositing
- atmospheric effects
- sound design
- voice
- music
- editing
- high-quality final assembly

The target is not to reproduce the exact style of any existing anime, artist,
studio, or historical production.

Studio must develop its own reusable visual identity.

---

## 4. Production Philosophy

Studio is not a frame-by-frame generative video system.

It is a deterministic animation production system assisted by AI.

The system prefers:

- reusable character identities
- reusable rigs
- reusable animation clips
- procedural animation
- structured plans
- explicit capabilities
- validated intermediate representations
- deterministic execution
- shot-based rendering
- asset reuse
- recoverable production stages
- human review

over:

- arbitrary AI-generated Blender code
- uncontrolled model output
- regenerating characters every frame
- opaque video generation
- unnecessary cloud dependencies
- rendering entire episodes as one job
- unnecessary infrastructure

---

## 5. AI Production Roles

Studio separates creative responsibilities into specialized logical roles.

These roles do not require separate language models.

The same local model may initially perform several roles through different
prompts, schemas, tools, and application services.

### Director Agent

The Director determines what should happen.

Responsibilities will progressively include:

- screenplay/story interpretation
- sequence planning
- scene planning
- shot breakdown
- staging
- composition
- camera intent
- pacing
- emotional intent
- characters involved
- high-level action
- visual mode
- animation strategy
- narrative importance
- motion budget

The Director does not directly manipulate Blender.

### Animator Agent

The Animator determines how the performance should move.

Responsibilities will progressively include:

- action selection
- poses
- timing
- gaze
- eye movement
- head movement
- body movement
- facial expression
- action transitions
- acting
- reusable animation composition
- procedural animation intent
- camera animation

The Animator may request only capabilities available to the production system.

### Voice Actor Agent

The Voice Actor Agent is a later production role.

One logical agent will manage:

- dialogue performance
- character voice identity
- emotion
- pauses
- delivery
- multiple characters
- eventually multiple languages

The agent decides performance intent.

A replaceable local TTS engine generates audio.

### Music Director Agent

The Music Director Agent is a later production role.

It will plan:

- scoring intent
- ambience
- recurring themes
- character motifs
- location motifs
- cues
- transitions
- tension and release
- dialogue-aware music placement
- volume intent

Music planning and music generation remain separate concerns.

---

## 6. Animation Strategy and Motion Budget

Not every shot deserves or requires the same amount of animation.

Studio should eventually select the least expensive visual technique that
communicates the story beat effectively.

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

Higher-level production strategies may include:

- HELD_ACTING
- REUSABLE_ACTION
- CAMERA_OVER_ENVIRONMENT
- HERO_ANIMATION

The Director eventually assigns animation effort according to:

- narrative importance
- emotional importance
- required movement
- shot duration
- visual mode
- available capabilities
- production cost

This motion-budget philosophy is essential for practical long-form animation.

---

## 7. Animation Representation

Animation IR is the trust boundary between AI-generated animation intent and
execution.

The AI must never generate arbitrary Blender Python for execution.

The intended flow is:

    Creative Intent
        ->
    Director Plan
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

Animation IR remains deliberately execution-oriented.

Higher-level cinematic and acting concepts belong in Director and Animation
plans rather than forcing every concept into the low-level IR.

---

## 8. Character Philosophy

A character is a reusable production identity.

Character identity must remain separate from character appearance variants.

Conceptually:

    CharacterIdentity
        ->
    CharacterVariant
        ->
    Rig / Visual Asset
        ->
    Capabilities

A persistent identity may later appear with different:

- clothing
- hairstyles
- ages
- physiques
- accessories
- settings
- project-specific visual treatments

Real-person-inspired characters may eventually use the same architecture.

A real person must not be regenerated independently for every scene or frame.

Initial asset preparation and approval may remain partially manual.

---

## 9. World Philosophy

Worlds and locations are reusable production assets.

Conceptually:

    World
        ->
    Location
        ->
    Environment
        ->
    Props
        ->
    Spawn Points
        ->
    Camera Anchors
        ->
    Lighting Presets

A school, city, castle, battlefield, house, or street should be reusable across
shots rather than rebuilt from scratch every time.

2D backgrounds, 3D environments, and hybrid environments may coexist.

---

## 10. Long-Form Production

Long-form animation is decomposed as:

    Project
        ->
    Episode
        ->
    Sequence
        ->
    Scene
        ->
    Shot

The system renders recoverable units.

A failed shot must not invalidate already completed shots.

Intermediate artifacts are stored on disk and may be cached.

FFmpeg eventually assembles:

    shots
        ->
    scenes
        ->
    sequences
        ->
    episode

An entire episode must never need to remain in memory.

---

## 11. Battle and Crowd Philosophy

Large battles must not require an LLM to individually animate every participant.

The long-term architecture should support higher-level deterministic
choreography primitives such as:

- group movement
- formation movement
- crowd fleeing
- march cycles
- charge actions
- ranged volleys
- reusable combat exchanges
- two-character duels
- impact events
- smoke and effects
- reaction shots
- commander shots

Large-scale action should combine:

- reusable cycles
- deterministic choreography
- selective hero animation
- camera language
- editing
- silhouettes
- effects
- impact frames
- sound

This allows perceived scale without requiring continuous unique animation for
every character.

---

## 12. Hardware Philosophy

Studio begins on constrained local hardware.

Therefore the system must:

- remain local-first
- keep models replaceable
- execute expensive stages sequentially
- use lightweight local LLMs
- prefer deterministic animation over generative video
- render shot-by-shot
- use inexpensive proxy renders
- release resources between stages
- cache reusable results
- target modest resolutions during development
- avoid loading entire productions into memory

A hardware upgrade may improve speed and quality later, but the architecture
must not require one to prove the core system.

---

## 13. Human Role

Studio is designed to reduce repetitive animation work, not remove creative
ownership.

The human remains:

- storyteller
- software engineer
- creative supervisor
- asset approver
- continuity reviewer
- final quality reviewer

The user should not need to manually keyframe every routine scene.

Manual intervention remains acceptable for:

- initial asset creation
- unusual character interactions
- complex choreography
- exceptional acting
- continuity corrections
- final artistic refinement

---

## 14. Development Strategy

Development proceeds from deterministic foundations toward AI orchestration.

The order is:

    deterministic tools
        ->
    deterministic character animation
        ->
    deterministic multi-action scene
        ->
    AI Animator
        ->
    AI Director
        ->
    short AI-directed production
        ->
    reusable characters and worlds
        ->
    voice
        ->
    music
        ->
    longer productions

Autonomous AI behavior must never be introduced before the underlying
deterministic capability exists.

---

## 15. Success Criteria

The first major success is:

> A deterministic animation plan drives Blender to produce a short animated
> shot without manual keyframing during execution.

The next major success is:

> A local Animator Agent converts natural-language direction into validated
> executable animation.

The next major success is:

> A local Director Agent and Animator Agent together produce a coherent
> 5-15 second scene.

Later milestones expand toward:

- 30-60 second scenes
- multi-character scenes
- reusable worlds
- voice
- music
- 3-5 minute productions
- approximately 10-minute sequences
- multi-scene episodes
- long-form original stories

Each milestone must be earned by a reliable previous milestone.