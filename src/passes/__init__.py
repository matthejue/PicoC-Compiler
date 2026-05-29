from src.passes.common import PassStateMixin
from src.passes.linking.reti_patch_pass import RetiPatchPass
from src.passes.linking.reti_pass import RetiPass
from src.passes.normal_compilation.picoc_anf_pass import PicocAnfPass
from src.passes.normal_compilation.picoc_blocks_pass import PicocBlocksPass
from src.passes.normal_compilation.picoc_shrink_pass import PicocShrinkPass
from src.passes.normal_compilation.picoc_symbol_pass import PicocSymbolPass
from src.passes.normal_compilation.picoc_typing_pass import PicocTypingPass
from src.passes.normal_compilation.reti_blocks_pass import RetiBlocksPass


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
