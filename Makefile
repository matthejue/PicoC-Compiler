TEST_BINARIES = $(wildcard ./test/*_test.py)
.PHONY: all run test clean

all: run-shell clean

run-compile:
	./src/pico_c_compiler.py -a -p ./src/input.picoc ./src/output.reti

run-shell:
	./src/pico_c_compiler.py -t

test: $(TEST_BINARIES)
	S^

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
