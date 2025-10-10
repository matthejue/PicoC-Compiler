./src/main.py $(cat ./opts/run_cpl_opts.txt) $2 "$1" || exit 1
reti_emulator $(cat ./opts/run_emu_opts.txt) $3 "${1%.picoc}.reti"
