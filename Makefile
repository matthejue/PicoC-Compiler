# SHELL := /bin/bash
ARG_BASE = $(shell basename --suffix=.picoc $(ARG))
.PHONY: all test clean

all: interpret-color

install:
	pip install -r ./requirements.txt
	@sudo -- sh -c '[[ ! -f /usr/local/bin/picoc_compiler ]] && ln -sr ./src/main.py /usr/local/bin/picoc_compiler && echo compiler /usr/local/bin/picoc_compiler was successfully installed || echo compiler /usr/local/bin/picoc_compiler is already installed'
	@[[ ! -d ~/.config/picoc_compiler ]] && mkdir ~/.config/picoc_compiler && echo config folder ~/.config/picoc_compiler created || echo config folder ~/.config/picoc_compiler does already exist
	@[[ ! -f ~/.config/picoc_compiler/history.json ]] && touch ~/.config/picoc_compiler/history.json && echo config file ~/.config/picoc_compiler/history.json created || echo config file ~/.config/picoc_compiler/history.json does already exist
	@[[ ! -f ~/.config/picoc_compiler/settings.conf.json ]] && touch ~/.config/picoc_compiler/settings.conf.json && echo settings file ~/.config/picoc_compiler/settings.conf.json created || echo settings file ~/.config/picoc_compiler/settings.conf.json does already exist
	@[[ ! -f ~/.config/picoc_compiler/most_used_compile_opts.txt ]] && ln -sr ./most_used_compile_opts.txt ~/.config/picoc_compiler/most_used_compile_opts.txt && echo most-usecreated ions file ~/.config/picoc_compiler/most_used_compile_opts.txt created || echo most-used-compile-options file ~/.config/picoc_compiler/most_used_compile_opts.txt does already exist
	@[[ ! -f ~/.config/picoc_compiler/most_used_interpret_opts.txt ]] && ln -sr ./most_used_interpret_opts.txt ~/.config/picoc_compiler/most_used_interpret_opts.txt && echo most-usecreated erpret-options file ~/.config/picoc_compiler/most_used_interpret_opts.txt created || echo most-used-interpret-options file ~/.config/picoc_compiler/most_used_interpret_opts.txt does already exist

uninstall:
	pip uninstall -r ./requirements.txt
	@sudo -- sh -c '[[ -f /usr/local/bin/picoc_compiler ]] && rm /usr/local/bin/picoc_compiler && echo compiler /usr/local/bin/picoc_compiler was successfully uninstalled || echo compiler /usr/local/bin/picoc_compiler is already uninstalled'
	@[[ -f ~/.config/picoc_compiler/history.json ]] && rm ~/.config/picoc_compiler/history.json && echo file ~/.config/picoc_compiler/history.json was deleted || echo config file ~/.config/picoc_compiler/history.json is already deleted
	@[[ -f ~/.config/picoc_compiler/settings.conf.json ]] && rm ~/.config/picoc_compiler/settings.conf.json && echo file ~/.config/picoc_compiler/settings.conf.json was deleted || echo settings file ~/.config/picoc_compiler/settings.conf.json is already deleted
	@[[ -f ~/.config/picoc_compiler/most_used_compile_opts.txt ]] && rm ~/.config/picoc_compiler/most_used_compile_opts.txt && echo file ~/.config/picoc_compiler/most_used_compile_opts.txt was deleted || echo most-used-compile-options file ~/.config/picoc_compiler/most_used_compile_opts.txt is already deleted
	@[[ -f ~/.config/picoc_compiler/most_used_interpret_opts.txt ]] && rm ~/.config/picoc_compiler/most_used_interpret_opts.txt && echo file ~/.config/picoc_compiler/most_used_interpret_opts.txt was deleted || echo most-used-interpret-options file ~/.config/picoc_compiler/most_used_interpret_opts.txt is already deleted
	@[[ -d ~/.config/picoc_compiler ]] && rmdir ~/.config/picoc_compiler && echo config folder ~/.config/picoc_compiler was deleted || echo config folder ~/.config/picoc_compiler is already deleted

compile: _compile _clean-pycache
_compile:
	./src/main.py $$(cat ./most_used_compile_opts.txt) ./run/code.picoc

compile-verbose: _compile-verbose _clean-pycache
_compile-verbose:
	./src/main.py $$(cat ./most_used_compile_opts.txt) -v ./run/code.picoc

compile-color: _compile-color _clean-pycache
_compile-color:
	./src/main.py $$(cat ./most_used_compile_opts.txt) -c ./run/code.picoc

compile-debug: _compile-debug _clean-pycache
_compile-debug:
	./src/main.py $$(cat ./most_used_compile_opts.txt) -d ./run/code.picoc

interpret: _interpret _clean-pycache
_interpret:
	./src/main.py $$(cat ./most_used_interpret_opts.txt) ./run/code.picoc

interpret-verbose: _interpret-verbose _clean-pycache
_interpret-verbose:
	./src/main.py $$(cat ./most_used_interpret_opts.txt) -v ./run/code.picoc

interpret-color: _interpret-color _clean-pycache
_interpret-color:
	./src/main.py $$(cat ./most_used_interpret_opts.txt) -c ./run/code.picoc

interpret-debug: _interpret-debug _clean-pycache
_interpret-debug:
	./src/main.py $$(cat ./most_used_interpret_opts.txt) -d ./run/code.picoc

shell: _shell _clean-pychache
_shell:
	./src/main.py

extract:
	./extract_input_and_expected.sh $(ARG_BASE)

test: _test _clean-pycache
test-clean: _test clean
_test:
	# start with 'make test-arg ARG=file_basename'
	# ARG2=-d for debugging
	-./export_environment_vars_for_makefile.sh; \
	./run_tests.sh $${COLUMNS} $(ARG_BASE) $(ARG2);

convert:  extract
	./convert_to_c.py $(ARG_BASE)

verify: extract convert _verify
verify-clean: extract convert _verify _clean-files
_verify:
	./export_environment_vars_for_makefile.sh; \
	./verify_tests.sh $${COLUMNS} $(ARG_BASE)

help:
	./src/main.py -h -c
	./src/main.py -h > ./doc/help-page.txt
	sed "s/most_used_interpret_opts/$$(cat ./most_used_interpret_opts.txt)/" ./doc/getting_started_raw.md > ./doc/getting_started.md


clean: _clean-pycache _clean-files
_clean-pycache:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

_clean-files:
	find . -type f -wholename "./tests/*.tokens" -delete
	find . -type f -wholename "./tests/*.dt" -delete
	find . -type f -wholename "./tests/*.dt_simple" -delete
	find . -type f -wholename "./tests/*.ast" -delete
	find . -type f -wholename "./tests/*.st_mon" -delete
	find . -type f -wholename "./tests/*.st" -delete
	find . -type f -wholename "./tests/*.picoc_shrink" -delete
	find . -type f -wholename "./tests/*.picoc_blocks" -delete
	find . -type f -wholename "./tests/*.picoc_mon" -delete
	find . -type f -wholename "./tests/*.reti_blocks" -delete
	find . -type f -wholename "./tests/*.reti_patch" -delete
	find . -type f -wholename "./tests/*.reti" -delete
	find . -type f -wholename "./tests/*.error" -delete
	find . -type f -wholename "./tests/*.c" -delete
	find . -type f -wholename "./tests/*.c_out" -delete
	find . -type f -wholename "./tests/*.reti_tokens" -delete
	find . -type f -wholename "./tests/*.reti_ast" -delete
	find . -type f -wholename "./tests/*.in" -delete
	find . -type f -wholename "./tests/*.out" -delete
	find . -type f -wholename "./tests/*.out_expected" -delete
	find . -type f -wholename "./tests/*.reti_states" -delete
	find . -type f -wholename "./tests/*.c" -delete
	find . -type f -wholename "./tests/*.c_out" -delete
	find . -type f -wholename "./tests/*.exec" -delete

setup_pyinstaller_linux:
	python -m pip install --upgrade pip
	pip install tabulate
	pip install pyinstaller
	pip install staticx
	pip install patchelf-wrapper

setup_pyinstaller_wine:
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 winecfg
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/Python10/python.exe -m pip install --upgrade pip
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/Python10/python.exe -m pip install tabulate
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/Python10/python.exe -m pip install pyinstaller

setup_pyinstaller_windows:
	python -m pip install --upgrade pip
	pip install tabulate
	pip install pyinstaller

create_bin_linux:
	pyinstaller ./src/main.py --onefile --hidden-import=tabulate,cmd2,colorama,bitstring --distpath=./dist
	staticx ./dist/main ./dist/pico_c_compiler_linux
	rm ./dist/main

create_bin_wine:
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/Python10/Scripts/pyinstaller.exe ~/Applications/Windows10/drive_c/users/areo/Documents/Studium/pico_c_compiler/src/main.py  --onefile --hidden-import=tabulate --distpath=~/Documents/Studium/pico_c_compiler/dist
	mv ~/Documents/Studium/pico_c_compiler/dist/pico_c_compiler.exe ~/Documents/Studium/pico_c_compiler/dist/pico_c_compiler_wine.exe

create_bin_windows:
	pyinstaller src\main.py --onefile --hidden-import=tabulate,cmd2,colorama,bitstring --distpath=dist
	staticx ./dist/main.exe ./dist/pico_c_compiler_windows.exe
	# entferne ./dist/main.exe

exec_bin_linux:
	./dist/pico_c_compiler_linux -S

exec_bin_wine:
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/users/areo/Documents/Studium/pico_c_compiler/dist/pico_c_compiler_wine.exe -S

exec_bin_windows:
	# go into dist folder in explorer and ctrl+l and type cmd and hit enter
	pico_c_compiler_windows.exe -S
