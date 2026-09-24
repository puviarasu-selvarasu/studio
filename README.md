# Studio

Studio is a local-first, zero-cost AI-assisted 2D animation production engine.

It orchestrates structured creative intent, deterministic animation logic, Blender,
text-to-speech, background generation, and FFmpeg into a reproducible production
pipeline.

## Products

Studio will eventually support two independent products:

- FunLearn — educational children's shorts
- Anime Studio — narrative anime-style episodes

Both products share the Studio kernel.

Neither product imports the other.

## Architecture

Studio uses a modular monolith with Ports and Adapters.

Core principle:

> AI decides WHAT. Python decides HOW. Blender executes.

The AI never generates Blender commands directly.

AI-generated animation intent is represented through Animation IR and validated against
a capability registry before Blender execution.

## Current Status

Phase 0 — Foundation

Completed:

- repository structure
- Python environment
- kernel package
- ports
- documentation
- composition root
- initial tests

Current test status:

    4 passed

## Development

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1