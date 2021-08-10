TEST_BINARIES = $(wildcard ./test/*_test.py)
.PHONY: all run test clean

all: run-shell-ast clean

run-read-ast:
	./src/pico_c_compiler.py -a -p ./src/input.picoc ./src/output.reti

run-read-ast-verbose:
	./src/pico_c_compiler.py -a -p -v ./src/input.picoc ./src/output.reti

run-read-tokens:
	./src/pico_c_compiler.py -t -p -v ./src/input.picoc ./src/output.reti

run-shell-ast:
	./src/pico_c_compiler.py -a

run-shell-ast-verbose:
	./src/pico_c_compiler.py -a -v

run-shell-tokens:
	./src/pico_c_compiler.py -t -v

test: $(TEST_BINARIES)
	$^

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
