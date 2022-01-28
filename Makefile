# TEST_FILENAMES = $(shell basename -a $(wildcard ./tests/*.picoc))
ARG_BASE = $(shell basename --suffix=.picoc $(ARG))
.PHONY: all test clean

all: read-all-verbose

read-all: _read_all clean
_read-all:
	./src/main.py -c -t -a -s -p -b 100 -e 200 -d 20 -S 2 ./run/code.picoc

read-all-verbose: _read-all-verbose clean
_read-all-verbose:
	./src/main.py -c -t -a -s -p -v -b 100 -e 200 -d 20 -S 2 ./run/code.picoc

shell: _shell clean
_shell:
	./src/main.py

# shell-all: _shell-all clean
# _shell-all:
#   ./src/main.py -c -t -a -s -p -b 100 -e 200 -d 20 -S 2

# shell-all-verbose: _shell-all-verbose clean
# _shell-all-verbose:
#   ./src/main.py -c -t -a -s -p -v -b 100 -e 200 -d 20 -S 2

test: _test clean
_test:
	./run_tests.sh

test-arg: _test-arg clean
_test-arg:
	# start with 'make test-arg ARG=file_basename'
	./run_tests.sh $(ARG_BASE)

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
	pyinstaller ./src/main.py --onefile --hidden-import=tabulate --distpath=./dist
	staticx ./dist/pico_c_compiler ./dist/pico_c_compiler_linux
	rm ./dist/pico_c_compiler

create_bin_wine:
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/Python10/Scripts/pyinstaller.exe ~/Applications/Windows10/drive_c/users/areo/Documents/Studium/pico_c_compiler/src/main.py  --onefile --hidden-import=tabulate --distpath=~/Documents/Studium/pico_c_compiler/dist
	mv ~/Documents/Studium/pico_c_compiler/dist/pico_c_compiler.exe ~/Documents/Studium/pico_c_compiler/dist/pico_c_compiler_wine.exe

create_bin_windows:
	pyinstaller src\main.py --onefile --hidden-import=tabulate --distpath=dist
	# rename file to pico_c_compiler_windows.exe

exec_bin_linux:
	./dist/pico_c_compiler_linux -S

exec_bin_wine:
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/users/areo/Documents/Studium/pico_c_compiler/dist/pico_c_compiler_wine.exe -S

exec_bin_windows:
	# go into dist folder in explorer and ctrl+l and type cmd and hit enter
	pico_c_compiler_windows.exe -S

help:
	./src/main.py -h
	./src/main.py -h > ./doc/help-page.txt

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
