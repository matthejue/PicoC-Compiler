ARG_BASE = $(shell basename --suffix=.picoc $(ARG))
.PHONY: all test clean

all: read-color

install:
	ln -sr ./src/main.py /usr/local/bin/picoc_compiler

read: _read _clean-pycache
_read:
	./src/main.py -ctdambs -p -D 20 -S 2 -M ./run/code.picoc

read-verbose: _read-verbose _clean-pycache
_read-verbose:
	./src/main.py -ctdambs -p -D 20 -S 2 -M -v ./run/code.picoc

read-color: _read-color _clean-pycache
_read-color:
	./src/main.py -ctdambs -p -D 20 -S 2 -M -v -C ./run/code.picoc

read-debug: _read-debug _clean-pycache
_read-debug:
	./src/main.py -ctdambs -p -D 20 -S 2 -M -v -g ./run/code.picoc

shell: _shell _clean-pychache
_shell:
	./src/main.py

extract:
	./extract_input_and_expected.sh

test: _test _clean-pycache
test-clean: _test clean
_test:
	# start with 'make test-arg ARG=file_basename'
	# ARG2=-g for debugging
	./export_environment_vars_for_makefile.sh; \
	./run_tests.sh $${COLUMNS} $(ARG_BASE) $(ARG2);

verify: extract _verify
verify-clean: extract _verify _clean-files
_verify:
	./export_environment_vars_for_makefile.sh; \
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
	find . -type f -wholename "./tests/*.ast" -delete
	find . -type f -wholename "./tests/*.csv" -delete
	find . -type f -wholename "./tests/*.picoc_mon" -delete
	find . -type f -wholename "./tests/*.picoc_blocks" -delete
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
