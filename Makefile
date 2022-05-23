ARG_BASE = $(shell basename --suffix=.picoc $(ARG))
.PHONY: all test clean

all: compile-color

install:
	ln -sr ./src/main.py /usr/local/bin/picoc_compiler

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

interpret: _compile _interpret _clean-pycache
_interpret:
	./RETI-Interpreter/src/main.py $$(cat ./most_used_interpret_opts.txt) ./run/code.reti

interpret-verbose: _compile-verbose _interpret-verbose _clean-pycache
_interpret-verbose:
	./RETI-Interpreter/src/main.py $$(cat ./most_used_interpret_opts.txt) -v ./run/code.reti

interpret-color: _compile-color _interpret-color _clean-pycache
_interpret-color:
	./RETI-Interpreter/src/main.py $$(cat ./most_used_interpret_opts.txt) -C ./run/code.reti

shell: _shell _clean-pychache
_shell:
	./src/main.py

extract:
	./extract_input_and_expected.sh

test: _test _clean-pycache
test-clean: _test clean
_test:
	# start with 'make test-arg ARG=file_basename'
	# ARG2=-d for debugging
	./export_environment_vars_for_makefile.sh; \
	./run_tests.sh $${COLUMNS} $(ARG_BASE) $(ARG2);


convert:  extract
	./convert_to_c.py

verify: extract convert _verify
verify-clean: extract convert _verify _clean-files
_verify:
	./verify_tests.sh $${COLUMNS}

help:
	./src/main.py -h -C
	./src/main.py -h > ./doc/help-page.txt

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
	find . -type f -wholename "./tests/*.reti_state" -delete
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
