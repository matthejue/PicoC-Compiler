./run.py $(cat ./config/debug_cpl_opts.txt) $2 "$1" || exit 1
gdb --tui -n -x ./.gdbinit --args reti_emulator $(cat ./config/debug_emu_opts.txt) $3 "${1%.picoc}.reti"
