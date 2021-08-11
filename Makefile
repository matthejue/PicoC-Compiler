TEST_BINARIES = $(shell basename --suffix=.py $(wildcard ./test/*_test.py))
TEST_BINARY_BASENAMES = $(foreach test_binary,$(TEST_BINARIES),test.$(test_binary))
.PHONY: all run test clean

all: run-shell-ast clean

run-read-ast:
	./pico_c_compiler.py -a -p ./input.picoc ./output.reti

run-read-ast-verbose:
	./pico_c_compiler.py -a -p -v ./input.picoc ./output.reti

run-read-tokens:
	./pico_c_compiler.py -t -p -v ./input.picoc ./output.reti

run-shell-ast:
	./pico_c_compiler.py -a

run-shell-ast-verbose:
	./pico_c_compiler.py -a -v

run-shell-tokens:
	./pico_c_compiler.py -t -v

test:
	for test_binary in $(TEST_BINARY_BASENAMES); do \
		python -m $$test_binary; \
	done

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
