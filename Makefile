TEST_BINARY_BASENAMES = $(shell basename -a $(wildcard ./test/*_test.py))
# suffix=.py would have cut the .py away and implies -a
TEST_BINARY_PATHS = $(foreach test_binary,$(TEST_BINARY_BASENAMES),test/$(test_binary))
.PHONY: all run test clean

all: run-read-all-verbose clean

run-read-all:
	./src/pico_c_compiler.py -c -t -a -S -p -s 100 -e 200 -m ./code.picoc

run-read-all-verbose:
	./src/pico_c_compiler.py -c -t -a -S -p -v -s 100 -e 200 -m ./code.picoc

run-read-all-arg:
	./src/pico_c_compiler.py -c -t -a -S -p -v -s 100 -e 200 -m ./test/$(ARG)

run-shell-all:
	./src/pico_c_compiler.py -c -t -a -S -p -s 100 -e 200 -m

run-shell-all-verbose:
	./src/pico_c_compiler.py -c -t -a -S -p -v -s 100 -e 200 -m

test:
	# for test_binary in $(TEST_BINARY_BASENAMES); do \
	# 	python -m $$test_binary; \
	# done
	echo $(TEST_BINARY_PATHS)
	for test_binary in $(TEST_BINARY_PATHS); do \
		./$$test_binary; \
	done

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
	pyinstaller ./src/pico_c_compiler.py --onefile --hidden-import=tabulate --distpath=./dist
	staticx ./dist/pico_c_compiler ./dist/pico_c_compiler_linux
	rm ./dist/pico_c_compiler

create_bin_wine:
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/Python10/Scripts/pyinstaller.exe ~/Applications/Windows10/drive_c/users/areo/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py  --onefile --hidden-import=tabulate --distpath=~/Documents/Studium/pico_c_compiler/dist
	mv ~/Documents/Studium/pico_c_compiler/dist/pico_c_compiler.exe ~/Documents/Studium/pico_c_compiler/dist/pico_c_compiler_wine.exe

create_bin_windows:
	pyinstaller src\pico_c_compiler.py --onefile --hidden-import=tabulate --distpath=dist
	# rename file to pico_c_compiler_windows.exe

exec_bin_linux:
	./dist/pico_c_compiler_linux -S

exec_bin_wine:
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/users/areo/Documents/Studium/pico_c_compiler/dist/pico_c_compiler_wine.exe -S

exec_bin_windows:
	# go into dist folder in explorer and ctrl+l and type cmd and hit enter
	pico_c_compiler_windows.exe -S

help:
	./src/pico_c_compiler.py -h

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
