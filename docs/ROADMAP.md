# Studio — Roadmap

## Guiding Rule

Every phase must produce something runnable.

Do not add breadth before the current vertical slice works.

---

## Phase 0 — Foundation

Target: Week 1

### Work

- repository creation
- Python virtual environment
- package structure
- documentation
- ports
- composition root
- pytest foundation
- Git configuration

### Explicitly excluded

- Blender
- animation
- Ollama calls
- Piper calls
- FFmpeg calls
- AI image generation

### Deliverable

    python main.py --help

works successfully and the test suite passes.

---

## Phase 1 — Content Pipeline Migration

Target: Week 2

### Work

- migrate existing lesson generation concepts
- Ollama adapter
- structured LLM output
- schema validation
- capability registry
- Animation IR schema
- Animation IR validator

### Deliverable

    lesson request
        ->
    structured lesson
        ->
    validated scene representation
        ->
    validated Animation IR

No rendering yet.

---

## Phase 2 — Blender Sanity Test

Target: Week 3

### Work

Create one manual Blender scene containing Momo.

Prove the smallest possible Blender bridge.

Test:

    eyes open
        ->
    eyes closed
        ->
    eyes open

### Deliverable

A Blender background-mode command produces a short blink render.

This phase must succeed before automated Blender animation is attempted.

---

## Phase 3 — Blender Adapter

Target: Weeks 4–5

### Work

- Blender adapter
- IR-to-Blender translation
- rig loading
- action application
- frame rendering
- process/error handling

### Deliverable

A hardcoded Animation IR produces a complete animated Momo shot.

Example:

    walk
      ->
    wave
      ->
    blink

No manual animation during execution.

---

## Phase 4 — Character Library

Target: Weeks 5–6

### Work

Improve Momo.

Initial action set:

- idle
- walk
- wave
- talk
- blink

Define:

- rig conventions
- action conventions
- naming
- anchors
- rest pose
- reusable animation definitions

### Deliverable

Momo can perform all five actions deterministically.

---

## Phase 5 — Integrated FunLearn Pipeline

Target: Week 7

### Work

- background generation
- background caching
- procedural background fallback
- Blender character compositing
- TTS
- FFmpeg
- scene assembly
- final short assembly

### Deliverable

One complete approximately 45-second animated FunLearn short.

---

## Phase 6 — Scene Director

Target: Week 8

### Work

- Ollama scene planning
- constrained prompt templates
- few-shot examples
- deterministic mapping from scene themes to supported actions

The AI describes intent.

Python selects executable animation behavior.

### Deliverable

A topic such as:

    colors

can produce a complete animated short using the supported production vocabulary.

---

## Phase 7 — Kernel Extraction

Target: Week 9

### Work

- stabilize shared kernel
- extract reusable components
- FunLearn depends on kernel
- Anime Studio skeleton created
- style bible created

### Deliverable

Two independent applications use the same kernel.

---

## Phase 8+ — Anime Studio

Target: Months 3–6

Potential work:

- second character
- screenplay parser
- multi-character scenes
- dialogue timing
- shot planning
- longer episodes
- reusable scene templates
- production management

No Phase 8 feature should be started merely because it sounds useful.

It must solve a demonstrated production problem.

---

## Quality Gates

Before moving to the next major phase:

1. Current phase is runnable.
2. Tests pass.
3. Failure behavior is understood.
4. Hardware performance is acceptable.
5. The architecture has not accumulated unnecessary abstraction.
6. The previous phase remains reproducible.

---

## Production Strategy

Initial target:

    1 finished video

not:

    5 videos/week

Production volume will increase only after:

- rendering is stable
- quality is stable
- failures are recoverable
- assets are reusable
- the production workflow is repeatable