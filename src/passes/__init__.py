from src.passes.common import PassStateMixin
from src.passes.normal_compilation import (
    PicocShrinkPass,
    PicocBlocksPass,
    PicocSymbolPass,
    PicocTypingPass,
    PicocAnfPass,
    RetiBlocksPass,
)
from src.passes.linking import RetiPatchPass, RetiPass


class Passes(
    PassStateMixin,
    PicocShrinkPass,
    PicocBlocksPass,
    PicocSymbolPass,
    PicocTypingPass,
    PicocAnfPass,
    RetiBlocksPass,
    RetiPatchPass,
    RetiPass,
):
    pass
