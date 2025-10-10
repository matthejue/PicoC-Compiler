./src/main.py $(cat ./opts/debug_cpl_opts.txt) $2 "$1" || exit 1
gdb --tui -n -x ./.gdbinit --args reti_emulator $(cat ./opts/debug_emu_opts.txt) $3 "${1%.picoc}.reti"
