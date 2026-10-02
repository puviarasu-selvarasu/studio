"""Studio voice-performance domain."""

from kernel.voices.casting import (
    CharacterVoiceAssignment,
    VoiceCast,
    VoiceCastError,
)
from kernel.voices.catalog import (
    STUDIO_VOICE_01,
    STUDIO_VOICE_02,
    VOICE_IDENTITIES,
    get_voice_identity,
)
from kernel.voices.models import (
    VoiceDomainError,
    VoiceEmotion,
    VoiceEnergy,
    VoiceIdentity,
    VoicePace,
    VoicePerformancePlan,
)
from kernel.voices.serialization import (
    VOICE_PERFORMANCE_SCHEMA_VERSION,
    VoicePerformanceParseError,
    voice_performance_plan_from_data,
    voice_performance_plan_from_json,
    voice_performance_plan_to_data,
    voice_performance_plan_to_json,
)


__all__ = [
    "CharacterVoiceAssignment",
    "STUDIO_VOICE_01",
    "STUDIO_VOICE_02",
    "VOICE_IDENTITIES",
    "VOICE_PERFORMANCE_SCHEMA_VERSION",
    "VoiceCast",
    "VoiceCastError",
    "VoiceDomainError",
    "VoiceEmotion",
    "VoiceEnergy",
    "VoiceIdentity",
    "VoicePace",
    "VoicePerformanceParseError",
    "VoicePerformancePlan",
    "get_voice_identity",
    "voice_performance_plan_from_data",
    "voice_performance_plan_from_json",
    "voice_performance_plan_to_data",
    "voice_performance_plan_to_json",
]
