TEST_BINARY_BASENAMES = $(shell basename -a $(wildcard ./test/*_test.py))
# suffix=.py would have cut the .py away and implies -a
TEST_BINARY_PATHS = $(foreach test_binary,$(TEST_BINARY_BASENAMES),test/$(test_binary))
.PHONY: all run test clean

all: run-read-compile clean

run-read-compile:
	./src/pico_c_compiler.py -p -s 100 -e 200 -m -S ./input.picoc ./output.reti

run-read-compile-comments:
	./src/pico_c_compiler.py -p -v -s 100 -e 200 -m -S ./input.picoc ./output.reti

run-read-compile-arg:
	./src/pico_c_compiler.py -p -s 100 -e 200 -m -S ./test/$(ARG) ./output.reti

run-shell-compile:
	./src/pico_c_compiler.py -p -s 100 -e 200 -m -S

run-shell-compile-comments:
	./src/pico_c_compiler.py -p -v -s 100 -e 200 -m -S

run-read-ast:
	./src/pico_c_compiler.py -a -p -m ./input.picoc ./output.reti

run-read-ast-verbose:
	./src/pico_c_compiler.py -a -p -v -m ./input.picoc ./output.reti

run-read-tokens:
	./src/pico_c_compiler.py -t -p -v -m ./input.picoc ./output.reti

run-shell-ast:
	./src/pico_c_compiler.py -a -m

run-shell-ast-verbose:
	./src/pico_c_compiler.py -a -v -m

run-shell-tokens:
	./src/pico_c_compiler.py -t -v -m

run-help:
	./src/pico_c_compiler.py -h

test:
	# for test_binary in $(TEST_BINARY_BASENAMES); do \
	# 	python -m $$test_binary; \
	# done
	echo $(TEST_BINARY_PATHS)
	for test_binary in $(TEST_BINARY_PATHS); do \
		./$$test_binary; \
	done

create_bin_linux:
	pyinstaller ./src/pico_c_compiler.py --onefile --hidden-import=tabulate --distpath=./dist

create_bin_win:
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/Python10/Scripts/pyinstaller.exe ~/Applications/Windows10/drive_c/users/areo/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py  --onefile --hidden-import=tabulate --distpath=~/Documents/Studium/pico_c_compiler/dist

exec_bin_linux:
	./dist/pico_c_compiler -S

exec_bin_win:
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/users/areo/Documents/Studium/pico_c_compiler/dist/pico_c_compiler.exe -S

help:
	./src/pico_c_compiler.py -h

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
