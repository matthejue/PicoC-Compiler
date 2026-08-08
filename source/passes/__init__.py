from source.passes.common import PassStateMixin
from source.passes.linking.reti_patch_pass import RetiPatchPass
from source.passes.linking.reti_pass import RetiPass
from source.passes.compilation.picoc_anf_pass import PicocAnfPass
from source.passes.compilation.picoc_blocks_pass import PicocBlocksPass
from source.passes.compilation.picoc_shrink_pass import PicocShrinkPass
from source.passes.compilation.picoc_symbol_pass import PicocSymbolPass
from source.passes.compilation.picoc_typing_pass import PicocTypingPass
from source.passes.compilation.reti_blocks_pass import RetiBlocksPass


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
