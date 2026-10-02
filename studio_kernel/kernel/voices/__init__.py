"""Studio voice-performance domain."""

from kernel.voices.catalog import (
    STUDIO_VOICE_01,
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
    "STUDIO_VOICE_01",
    "VOICE_IDENTITIES",
    "VOICE_PERFORMANCE_SCHEMA_VERSION",
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
