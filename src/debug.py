"""
Debug helpers to toggle on-demand breakpoints and post-mortem hooks.

Use `activate_debug()` wherever you want to enable manual breakpoints, then
call `debug()` at the desired location; it will drop into pudb (or pdb as a
fallback) only when the flag is active.

Call `install_post_mortem_hook()` to have unhandled exceptions drop into pdb.
"""

import sys
import pdb
from src import global_vars

_debug_enabled = False


def activate_debug():
    """Enable debug breakpoints."""
    global _debug_enabled
    _debug_enabled = True


def deactivate_debug():
    """Disable debug breakpoints."""
    global _debug_enabled
    _debug_enabled = False


def debug():
    """Trigger pudb/pdb if debug mode was activated."""
    if not (_debug_enabled and global_vars.args.debug):
        return
    pudb.set_trace()


def debug_excepthook(exc_type, value, tb):
    try:
        import pudb  # type: ignore

        pudb.post_mortem(tb)
    except ImportError:
        pdb.post_mortem(tb)
