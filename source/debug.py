"""
Debug helpers to toggle on-demand breakpoints and post-mortem hooks.

Use `activate_debug()` wherever you want to enable manual breakpoints, then
call `debug()` at the desired location; it will drop into pudb (or pdb as a
fallback) only when the flag is active.

Call `install_post_mortem_hook()` to have unhandled exceptions drop into pdb.
"""

import pdb

try:
    import pudb
except ImportError:
    pudb = None

from source import global_vars

_debug_enabled = False
_debug_triggered = False


def activate_debug():
    """Enable debug breakpoints."""
    global _debug_enabled, _debug_triggered
    _debug_enabled = True
    _debug_triggered = False


def deactivate_debug():
    """Disable debug breakpoints."""
    global _debug_enabled, _debug_triggered
    _debug_enabled = False
    _debug_triggered = False


def debug():
    """Trigger pudb/pdb if debug mode was activated."""
    global _debug_triggered
    if not (_debug_enabled and global_vars.args.debug) or _debug_triggered:
        return
    _debug_triggered = True
    if pudb is None:
        pdb.set_trace()
    else:
        pudb.set_trace()


def debug_excepthook(_exc_type, _value, tb):
    if pudb is None:
        pdb.post_mortem(tb)
    else:
        pudb.post_mortem(tb)
