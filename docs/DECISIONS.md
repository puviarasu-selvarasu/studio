# Studio — Architecture Decision Records

This document records important architectural decisions.

---

# ADR-001 — Use a Modular Monolith

## Status

Accepted

## Context

Studio is initially developed and operated by one developer on one Windows machine.

The system has no requirement for independently deployed services.

The hardware is resource constrained.

## Decision

Studio will use a modular monolith.

There will be no microservices, Docker, Kubernetes, or distributed service architecture
during the initial development lifecycle.

## Consequences

### Positive

- simpler development
- simpler debugging
- lower memory usage
- easier local execution
- fewer deployment problems
- clear module boundaries remain possible

### Negative

- process boundaries are not independently scalable
- modules require discipline to maintain separation

---

# ADR-002 — Use Ports and Adapters

## Status

Accepted

## Context

External dependencies such as Ollama, Piper, Blender, and FFmpeg can change independently
of the core production logic.

The core system must remain testable without launching those applications.

## Decision

External systems are accessed through Protocol-based ports.

Adapters implement those ports.

Initial ports:

- LLMPort
- TTSPort
- AnimatorPort
- RendererPort

## Consequences

The application can use fake adapters during testing.

Infrastructure details remain outside the core orchestration logic.

---

# ADR-003 — Animation IR Is the Blender Boundary

## Status

Accepted

## Context

Allowing an LLM to generate Blender Python directly would couple generated content to
Blender implementation details and increase the consequences of model hallucination.

## Decision

The LLM never emits Blender commands.

The LLM emits structured Animation IR.

Python validates the IR against schemas and a capability registry.

The Blender adapter translates valid IR into Blender operations.

## Consequences

### Positive

- safer AI boundary
- deterministic execution
- easier testing
- Blender implementation can change without changing the LLM contract
- unsupported actions can be rejected explicitly

### Negative

- an additional representation must be designed and maintained
- the capability registry must remain synchronized with available actions

---

# ADR-004 — Deterministic Animation Instead of AI Video Generation

## Status

Accepted

## Context

The target hardware cannot support practical local AI video generation at the desired
quality.

AI video generation would also reduce determinism and increase compute/storage requirements.

## Decision

Animation will be generated from deterministic actions, keyframes, interpolation, and
reusable rigs.

AI determines creative intent.

Python determines executable animation.

Blender executes the animation.

## Consequences

### Positive

- reproducible output
- reusable characters
- predictable rendering
- lower hardware requirements
- controllable visual style

### Negative

- animation vocabulary is initially limited
- expressive range depends on the quality of the rig and action library

---

# ADR-005 — Build a Vertical Slice Before Broadening the System

## Status

Accepted

## Context

The largest technical risk is not lesson generation.

The critical unknown is whether structured animation intent can reliably drive Blender
to produce acceptable 2D animation on the available hardware.

Building many features before proving that bridge could result in a large amount of
unusable software.

## Decision

Development proceeds through vertical slices.

The first critical slice is:

    Animation intent
        ->
    validated representation
        ->
    Blender
        ->
    rendered animation

Feature breadth is deferred until this path works.

## Consequences

### Positive

- risks are discovered early
- progress is measurable
- architecture is validated against real execution
- less wasted development

### Negative

Some useful-looking features must deliberately wait until the core pipeline is proven.
---

# ADR-006: Focus Studio on Deterministic AI-Assisted Animation Production

## Status

Accepted

## Context

Studio was originally structured around two product directions:

- an educational animation product
- a broader anime and narrative animation product

The educational path introduced useful foundations including structured content,
local LLM integration, validation, and application boundaries.

However, continuing to develop two product directions would split engineering
effort and allow educational-domain concepts such as Lesson and ContentScene to
shape an animation architecture they were not designed to represent.

The primary product goal is now a general local-first animation production
system capable of progressively supporting original narrative animation.

Studio also requires a stronger separation between:

- cinematic direction
- character performance planning
- executable animation instructions
- Blender execution

The project is developed on constrained local hardware, so the architecture must
favor deterministic reusable animation, shot-based execution, limited-animation
techniques, and sequential expensive workloads.

## Decision

Studio will proceed as one focused AI-assisted animation production system.

The primary production architecture is:

    Creator
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

The governing rule is:

> AI decides WHAT. Python decides HOW. Blender executes.

AI-generated Python or arbitrary Blender commands must not be executed.

Animation IR remains the trust boundary between structured animation intent and
deterministic execution.

Director Plan, Animation Plan, and Animation IR remain separate representation
levels.

The Director owns high-level cinematic intent.

The Animator owns performance intent.

Animation IR contains executable animation intent supported by deterministic
capabilities.

The Capability Registry defines which animation actions the system genuinely
supports.

Studio will progressively support:

- 2D
- 2.5D
- hybrid 2D/3D production
- limited animation
- reusable animation
- selective hero animation
- modern cinematography and compositing

The previous educational Lesson/Content pipeline becomes legacy functionality.

It will:

- remain temporarily for migration safety
- retain its existing tests
- receive no new product development
- not become a dependency of new animation features
- be removed only through a separate controlled checkpoint

Development will proceed deterministic-first:

    Blender bridge
        ->
    deterministic animation toolkit
        ->
    controllable character
        ->
    deterministic short scene
        ->
    AI Animator
        ->
    AI Director
        ->
    reusable production systems
        ->
    longer productions

Voice Actor and Music Director capabilities are future production layers and
are not prerequisites for proving the visual animation pipeline.

## Consequences

### Positive

The project now has one primary product direction.

Animation-specific concepts can evolve without being constrained by the
educational Lesson model.

The Director, Animator, and execution layers have explicit responsibilities.

AI output remains isolated from arbitrary code execution.

Deterministic animation can be tested independently from AI planning.

Blender integration can be developed before autonomous creative behavior.

Limited-animation strategies and motion budgeting can reduce production cost.

The architecture can grow from short shots toward longer productions without
requiring entire episodes to remain in memory.

Existing useful foundations such as the LLM adapter, Animation IR, capability
registry, ports, validation, and tests remain reusable.

### Negative

Some existing educational code becomes temporary legacy code.

Documentation and package structure require gradual cleanup.

The deterministic-first approach delays visually impressive AI demonstrations
until the execution layer is reliable.

Reusable character, world, voice, music, and continuity systems require later
phases.

High-quality long-form animation remains a multi-stage engineering problem and
cannot be treated as a single model-generation task.

## Alternatives Considered

### Continue both FunLearn and narrative animation as equal products

Rejected because it splits development effort and encourages unrelated domain
models to influence the animation kernel.

### Build the AI Director first

Rejected because the Director could produce plans that the execution system
cannot perform.

### Let the LLM generate Blender Python directly

Rejected because it creates an unsafe and difficult-to-test execution boundary.

### Use generative video as the primary renderer

Rejected because it weakens deterministic character identity, asset reuse,
precise animation control, recoverability, and local constrained-hardware
operation.

### Build all production systems before rendering anything

Rejected because it would create architecture without executable evidence.

## Verification

This decision is considered successfully adopted when:

1. new animation functionality does not depend on the legacy Lesson pipeline
2. Blender execution accepts only trusted Studio-owned deterministic code
3. AI animation intent crosses structural and capability validation
4. a deterministic short animation is produced before AI Animator integration
5. AI Animator is proven before AI Director controls the full animation flow
