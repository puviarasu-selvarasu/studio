# Studio

Studio is a local-first AI-assisted animation production system for creating
original 2D, 2.5D, and hybrid anime-style productions with Blender.

The visual direction combines traditional hand-drawn and cel-animation
principles with modern cinematography, compositing, lighting, audio, and
production automation.

Studio is not an AI video generator. It is a deterministic animation
production system assisted by AI.

## Core Principle

> AI decides WHAT. Python decides HOW. Blender executes.

AI components produce structured creative and animation intent.

They never generate or execute arbitrary Blender Python.

Animation intent crosses a validated Animation IR boundary before deterministic
animation tools and Blender are allowed to execute it.

## Production Architecture

The intended production flow is:

    Creator
       |
       v
    Desktop UI
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
    Structural + Capability Validation
       |
       v
    Deterministic Animation Toolkit
       |
       v
    Blender
       |
       v
    2D / 2.5D / Hybrid Render
       |
       v
    Review
       |
       v
    Audio + Final Assembly

Future production roles include a Voice Actor Agent and Music Director Agent.
They will be introduced only after the visual animation pipeline is proven.

## Visual Direction

Studio is designed around an original visual language inspired by traditional
hand-drawn and cel-animation production rather than modern generative video.

The target includes:

- 2D animation
- Blender Grease Pencil where appropriate
- 2.5D staging and environments
- hybrid 2D/3D production
- hand-drawn-style line work
- cel-style shading
- strong key poses
- held poses and limited animation
- animation on reduced exposures where appropriate
- reusable animation cycles
- painted or illustrated-looking backgrounds
- expressive facial and character acting
- selective high-motion hero shots
- modern camera composition
- parallax and controlled depth
- modern lighting and compositing
- modern color treatment
- atmospheric effects
- modern voice, music, sound design, and editing

The goal is not to imitate a specific anime studio or historical production.

The goal is to combine traditional animation production principles with modern
digital tools to create a fresh Studio visual identity.

## Animation Strategy

Studio does not assume that every shot requires continuous full animation.

The Director and Animator will eventually choose production strategies such as:

- held acting
- key poses
- reaction shots
- dialogue animation
- camera-over-still compositions
- background pans
- reusable loops
- walk and run cycles
- parallax shots
- silhouettes
- montage
- impact frames
- action shots
- high-priority hero animation

Animation effort should be allocated according to narrative and visual
importance.

This makes long-form production more practical while preserving deliberate
artistic direction.

## Architecture

Studio uses a modular monolith with Hexagonal Architecture
(Ports and Adapters).

The core is separated into:

1. Domain
2. Application
3. Infrastructure

External systems such as Ollama, Blender, Piper, and FFmpeg are accessed
through explicit ports and adapters.

The domain remains independent of those systems.

## AI Roles

### Director Agent

The Director decides high-level creative intent, including:

- scene and shot breakdown
- staging
- composition
- camera intent
- pacing
- emotional intent
- characters involved
- high-level actions
- visual production strategy
- animation effort or motion budget

### Animator Agent

The Animator converts direction into structured performance intent, including:

- actions
- poses
- timing
- gaze
- head and eye movement
- expressions
- body movement
- transitions
- camera animation
- acting decisions

The Animator works only with capabilities that the deterministic animation
system can execute.

### Voice Actor Agent

Future role.

One agent will coordinate dialogue performance and persistent character voices
through replaceable local TTS technology.

### Music Director Agent

Future role.

The Music Director will plan scoring, ambience, cues, transitions, and
dialogue-aware music placement. Music generation and playback technology remain
replaceable implementation details.

## Animation IR

Animation IR is the trust boundary between AI-generated intent and execution.

Before Blender execution, animation data must pass:

1. structural validation
2. capability validation

Unsupported actions fail explicitly.

The system must never silently invent an executable animation capability.

## Blender

Blender is the execution and rendering engine, not the creative decision maker.

Studio will progressively use Blender for:

- deterministic object control
- rigged character animation
- camera control
- keyframes
- reusable actions
- procedural animation
- Grease Pencil
- 2D/3D composition
- stylized environments
- cel/toon rendering
- lighting
- effects
- compositing
- proxy rendering
- final shot rendering

## Resource Strategy

Studio is designed to work initially on constrained local hardware.

Expensive stages execute sequentially.

The production strategy is:

    plan
      ->
    validate
      ->
    animate
      ->
    proxy render
      ->
    review
      ->
    final render
      ->
    audio
      ->
    assemble

Long productions are divided into recoverable units:

    Project
      ->
    Episode
      ->
    Sequence
      ->
    Scene
      ->
    Shot

Studio must never require an entire episode to remain in memory.

## Current Foundation

Completed foundations include:

- repository and Python environment
- modular kernel
- Ports and Adapters structure
- Animation IR domain models
- Animation IR structural validation
- Ollama LLM adapter
- capability registry
- capability validation
- automated tests

The previous educational Lesson/Content pipeline is legacy functionality.

It remains temporarily for migration safety but must not be extended or used as
the foundation for new animation-system development.

## Current Development Goal

The immediate engineering objective is not a full episode.

The next critical vertical slice is:

    deterministic plan
        ->
    Animation IR
        ->
    validation
        ->
    animation toolkit
        ->
    Blender
        ->
    rendered shot

The first major proof is a short deterministic Blender animation produced
without manual keyframing during execution.

After that foundation is reliable, Studio will introduce the local Animator
Agent and then the local Director Agent.

## Development Rules

- Build vertical slices.
- Keep AI output structured and validated.
- Never execute arbitrary AI-generated code.
- Prefer deterministic reusable animation over frame-by-frame generation.
- Keep expensive processes sequential.
- Render and recover shot-by-shot.
- Use proxy renders before expensive final renders.
- Do not add infrastructure before a demonstrated need.
- Keep legacy functionality isolated while the new pipeline replaces it.
- Tests must pass before a checkpoint is considered complete.
- Human review remains part of the production workflow.

## Development

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```
