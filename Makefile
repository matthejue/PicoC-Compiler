TEST_FILENAMES = $(shell basename -a $(wildcard ./tests/*.picoc))
# suffix=.py would have cut the .py away and implies -a
# TEST_BINARY_PATHS = $(foreach test_binary,$(TEST_FILENAMES),test/$(test_binary))
ARG_BASE = $(shell basename --suffix=.picoc $(ARG))
.PHONY: all test clean

all: read-all-verbose clean

read-all:
	./src/pico_c_compiler.py -c -t -a -S -p -s 100 -e 200 -d 20 -m ./code.picoc

read-all-verbose:
	./src/pico_c_compiler.py -c -t -a -S -p -v -s 100 -e 200 -d 20 -m ./code.picoc

shell-all:
	./src/pico_c_compiler.py -c -t -a -S -p -s 100 -e 200 -d 20 -m

shell-all-verbose:
	./src/pico_c_compiler.py -c -t -a -S -p -v -s 100 -e 200 -d 20 -m

test:
	for testfile in $(TEST_FILENAMES); do \
		echo -e \\n===============================================================================; \
		echo $$testfile; \
		echo ===============================================================================; \
		./src/pico_c_compiler.py -c -t -a -S -p -v -s 100 -e 200 -d 20 -m ./tests/$$testfile; \
	done
# echo $(TEST_BINARY_PATHS)
# for test_binary in $(TEST_BINARY_PATHS); do \
	# ./$$test_binary; \
# done

test-arg:
	# start with 'make test-arg ARG=file_basename'
	./src/pico_c_compiler.py -c -t -a -S -p -v -s 100 -e 200 -d 20 -m ./tests/$(ARG_BASE).picoc

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
