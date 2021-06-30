TEST_BINARIES = $(basename $(wildcard ./test/*Test.py))
.PHONY: all run test clean

all: run clean

run:
	./src/pico_c_compiler.py -a -p ./src/input.picoc ./src/output.reti

test:
	S^

clean:
	find . -type f -name "*Test.py" -delete
	find . -type d -name "__pycache" -delete
