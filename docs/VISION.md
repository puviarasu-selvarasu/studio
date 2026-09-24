# Studio — Vision

## 1. Purpose

Studio is a local-first, zero-cost AI-assisted 2D animation production engine.

Its purpose is to allow a creative director/software engineer to describe educational or
narrative content at a high level and have Studio transform that intent into deterministic,
repeatable animation work executed by Blender.

Studio does not attempt to replace Blender.

Studio acts as the production orchestration layer above Blender.

The core principle is:

> AI decides WHAT should happen. Python decides HOW it happens. Blender executes it.

---

## 2. Products

Studio will eventually support two independent products.

### FunLearn

Educational animated shorts for children.

Target:

- 45–60 seconds
- YouTube Shorts
- English initially
- simple educational topics
- limited 2D animation
- human review before publication

### Anime Studio

Narrative 2D anime-style episodes.

Target:

- approximately 3–10 minutes initially
- YouTube distribution
- screenplay-driven production
- reusable characters
- multi-scene and eventually multi-character stories

The two products share the Studio kernel.

Neither product imports the other.

---

## 3. Core Philosophy

Studio is not an AI video generator.

It is a deterministic animation production system assisted by AI.

The system must prefer:

- deterministic animation
- reusable character rigs
- reusable actions
- structured data
- validated intermediate representations
- local execution
- low resource consumption
- explicit failure handling
- human review

over:

- frame-by-frame AI generation
- opaque AI video models
- cloud rendering
- uncontrolled model output
- large infrastructure
- unnecessary abstraction

---

## 4. Animation Representation

The Animation Intermediate Representation (Animation IR) is the boundary between
creative AI output and Blender execution.

The LLM must never generate Blender Python or Blender commands.

Instead, the LLM produces structured animation intent.

Example:

    {
      "scene_id": "scene_04",
      "duration": 6.0,
      "characters": [
        {
          "id": "momo",
          "actions": [
            {
              "type": "walk",
              "direction": "right",
              "duration": 2.5
            },
            {
              "type": "wave",
              "hand": "right",
              "duration": 1.5
            }
          ]
        }
      ],
      "camera": {
        "shot": "medium",
        "movement": "slow_push"
      }
    }

Python validates this representation before Blender receives it.

---

## 5. Visual Target

The visual target is not photorealism or modern high-frame-rate animation.

The intended style is:

- clean vector-like line work
- flat cel shading
- hard shadow boundaries
- warm retro colors
- strong poses
- expressive but limited character animation
- painted-looking static backgrounds
- camera movement
- restrained post-processing
- film grain
- subtle visual imperfections

The aesthetic target is inspired by the visual language of early television anime,
while remaining an original Studio production style.

Studio does not attempt to reproduce another studio's exact artwork.

---

## 6. Hardware Philosophy

Studio is designed around constrained local hardware.

The initial target machine has:

- Windows 11
- 8 GB RAM
- CPU-first execution
- approximately 2 GB discrete GPU memory
- integrated graphics
- no dedicated modern rendering GPU

Therefore Studio must:

- execute expensive processes sequentially
- render shot-by-shot
- use proxy renders before final renders
- target 720p initially
- use limited animation exposure
- avoid loading entire episodes into memory
- release resources between stages

---

## 7. Human Review

Studio will never automatically publish generated content.

The production pipeline ends at a human review checkpoint.

The human must be able to inspect:

- lesson/story content
- narration
- scene breakdown
- generated visuals
- animation
- final audio/video

before publication.

---

## 8. Success Criteria

Studio succeeds when a developer can provide a high-level creative request and receive
a reproducible animation project without manually animating every frame.

The first meaningful milestone is not a complete animation studio.

The first meaningful milestone is:

> A validated Animation IR can deterministically drive one reusable Blender character
> through a complete shot.

Everything else is built around proving and expanding that capability.