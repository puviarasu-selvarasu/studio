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