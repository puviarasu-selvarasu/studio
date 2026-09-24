# Studio — Architecture

## 1. Architectural Style

Studio uses a modular monolith with Hexagonal Architecture
(Ports and Adapters).

The architecture has three logical layers:

1. Domain
2. Application
3. Infrastructure

The shared reusable production contracts and adapters live inside `studio_kernel`.

Applications such as FunLearn and Anime Studio depend inward on the kernel.

---

## 2. Dependency Direction

Dependencies point inward.

    Infrastructure
          |
          v
      Application
          |
          v
        Domain

The Domain must never depend on Infrastructure.

The Application layer must depend on ports/contracts rather than concrete external
systems.

Infrastructure implements those ports.

---

## 3. Domain

The Domain contains pure production concepts.

Examples that will eventually exist:

- Lesson
- Scene
- Character
- Action
- Animation IR
- Camera instruction
- Capability
- Production state

Domain code must not import:

- Blender
- Ollama
- Piper
- FFmpeg
- requests
- filesystem-specific infrastructure
- operating-system integration

The domain should be deterministic and testable without external services.

---

## 4. Application

The Application layer coordinates production workflows.

It answers questions such as:

- What stage should execute next?
- Which port should be called?
- What data should move between stages?
- When should validation occur?
- What should happen when a stage fails?

Application services receive dependencies through ports.

They do not construct concrete infrastructure adapters.

---

## 5. Infrastructure

Infrastructure contains external-system implementations.

Examples:

- Ollama adapter
- Piper adapter
- Blender adapter
- FFmpeg adapter
- repository/file adapter
- background image adapter

Infrastructure is the only place where external-system-specific code belongs.

---

## 6. Ports

Ports define contracts between the application and infrastructure.

Initial ports:

- `LLMPort`
- `TTSPort`
- `AnimatorPort`
- `RendererPort`

A repository port will be added when persistent production data requires it.

Ports are Python Protocols.

The application should be able to operate against a fake/test implementation without
knowing whether the real implementation is Ollama, Piper, Blender, or another system.

---

## 7. Animation IR Boundary

Animation IR is the critical architectural boundary.

The flow is:

    Creative Input
          |
          v
        LLM
          |
          v
    Structured Output
          |
          v
    Schema Validation
          |
          v
 Capability Validation
          |
          v
    Animation IR
          |
          v
    Blender Adapter
          |
          v
       Blender

The LLM never generates Blender commands.

---

## 8. Capability Registry

Characters expose explicit capabilities.

Example conceptual capability set:

    momo:
      - idle
      - walk
      - wave
      - talk
      - blink

If an LLM requests an unsupported action, validation fails.

The system must not silently invent an implementation.

The validator should report the available capabilities so the generation layer can
correct its request.

---

## 9. Deterministic Animation

Animation execution is deterministic.

The LLM specifies intent.

Python determines:

- timing
- keyframes
- interpolation
- action composition
- frame ranges
- supported transitions

Blender executes the resulting instructions.

AI-generated frame-by-frame animation is explicitly outside the architecture.

---

## 10. Rendering Strategy

Rendering is shot-based.

A complete episode must never be rendered entirely in memory.

The intended flow is:

    Scene
      |
      v
    Animation
      |
      v
    Blender Frames
      |
      v
    Scene Video
      |
      v
    Release resources
      |
      v
    Next Scene

Final assembly is performed by FFmpeg.

---

## 11. Resource Constraint

The initial execution policy is sequential.

The system must not intentionally execute:

- Ollama
- Blender
- FFmpeg

simultaneously.

This is a hardware constraint rather than a theoretical architectural requirement.

The scheduler/application layer must therefore make execution order explicit.

---

## 12. Failure Boundaries

External adapters translate infrastructure failures into application-understandable
exceptions.

Examples:

- LLM unavailable
- TTS failure
- Blender process failure
- FFmpeg unavailable
- invalid generated data
- unsupported animation capability

Raw subprocess errors must not leak directly to users.

---

## 13. Human Review Gate

The final pipeline contains a mandatory human review checkpoint.

No publishing adapter is part of the initial architecture.

The initial system produces a reviewable local artifact.

---

## 14. Kernel Boundary

The kernel contains reusable contracts and implementations required by more than one
application.

During early development, the kernel remains deliberately small.

FunLearn is developed first because it provides the shortest path to proving the
production pipeline.

Once Anime Studio becomes the second real consumer, shared code is extracted and
stabilized.

---

## 15. Testing

Testing is divided into:

### Unit Tests

Test:

- domain behavior
- validation
- transformations
- application orchestration using fakes

No Blender/Ollama/Piper process is required.

### Integration Tests

Test:

- Ollama adapter
- Piper adapter
- Blender adapter
- FFmpeg adapter

against real local installations where practical.

External-process tests are not part of the fast unit-test suite.

---

## 16. Current Phase Boundary

Phase 0 contains:

- project structure
- documentation
- ports
- composition root
- test foundation

Phase 0 does not contain:

- Blender integration
- Animation IR implementation
- LLM integration
- TTS integration
- rendering
- animation
- AI image generation

Those belong to later phases.