./run.py $(cat ./config/run_cpl_opts.txt) $2 "$1" -o "${1%.picoc}.reti" || exit 1
reti_emulator $(cat ./config/run_emu_opts.txt) $3 "${1%.picoc}.reti"
