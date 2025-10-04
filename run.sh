./src/main.py $(cat ./run/run_cpl_opts.txt) $2 "$1";
reti_emulator $(cat ./run/run_emu_opts.txt) $3 "${1%.picoc}.reti";
