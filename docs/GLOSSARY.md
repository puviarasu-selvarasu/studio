# Studio — Glossary

## Action

A supported animation behavior that a character can execute.

Examples:

- idle
- walk
- wave
- talk
- blink

---

## Adapter

An infrastructure implementation of a port.

Examples:

- OllamaAdapter
- PiperAdapter
- BlenderAdapter
- FFmpegAdapter

---

## Animation IR

Animation Intermediate Representation.

The structured, implementation-independent representation of animation intent.

It is the boundary between AI-generated instructions and Blender execution.

---

## Application Layer

The orchestration layer.

It coordinates workflows through ports without depending directly on infrastructure
implementations.

---

## Capability Registry

A machine-readable description of what assets and characters are capable of doing.

The registry prevents the LLM from requesting unsupported behavior.

---

## Composition Root

The location where concrete dependencies are constructed and connected.

For Studio, the initial composition root is `main.py`.

The composition root is allowed to know about concrete adapters.

The rest of the application should depend on abstractions.

---

## Domain

The business/production concepts and rules of Studio.

Domain code should remain independent of external systems.

---

## Exposure

The number of animation frames for which a drawing or pose is held before changing.

Limited exposure is important for the intended retro television-animation aesthetic.

---

## FunLearn

The educational short-form product built on the Studio kernel.

Initial target:

45–60 second educational videos for children.

---

## Grease Pencil

Blender's 2D drawing/animation system.

Studio will eventually use Grease Pencil as part of the Blender execution layer.

---

## Hexagonal Architecture

An architecture in which the core application communicates with external systems through
ports and external systems are implemented through adapters.

Also called Ports and Adapters architecture.

---

## Kernel

The shared reusable production infrastructure used by multiple Studio products.

The kernel should contain only functionality that genuinely belongs to both consumers.

---

## LLM

Large Language Model.

In Studio, the LLM is used for creative/content planning and structured intent generation.

It is not responsible for directly controlling Blender.

---

## Port

An interface/contract describing an external capability required by the application.

Examples:

- LLMPort
- TTSPort
- AnimatorPort
- RendererPort

---

## Proxy Render

A deliberately low-cost render used to verify a scene before performing a final render.

The initial Studio proxy target is:

- Workbench
- 480p
- 8 FPS

---

## Renderer

The subsystem responsible for producing rendered visual output.

Blender is the intended animation/rendering engine.

FFmpeg is the intended video assembly/encoding tool.

---

## Scene

A bounded portion of an episode or short containing:

- characters
- actions
- camera
- background
- duration
- audio/visual requirements

---

## Strangler Fig Migration

A migration strategy where new functionality is built alongside an existing implementation,
then gradually replaces it after the new implementation is proven.

Studio uses this approach when migrating the previous Pillow/FFmpeg pipeline.

---

## Vertical Slice

A small feature that crosses the necessary layers and produces a real end-to-end result.

Example:

    IR
      ->
    Blender
      ->
    rendered shot

A vertical slice is preferred over building an entire layer in isolation.

---

## Visual Rig

A reusable character construction used by Blender to produce multiple poses and actions.

A character is created once and reused rather than regenerated every frame.

---

## Workbench

Blender's lightweight rendering mode.

Studio uses Workbench for inexpensive proxy renders during development.

---

## Deterministic

Given the same valid input, configuration, assets, and software version, the system should
produce the same or substantially reproducible execution result.

---

## Human Review Gate

A mandatory point where a human reviews generated content before publication.

Studio does not automatically publish generated videos.