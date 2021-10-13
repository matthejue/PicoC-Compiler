TEST_BINARY_BASENAMES = $(shell basename -a $(wildcard ./test/*_test.py))
# suffix=.py would have cut the .py away and implies -a
TEST_BINARY_PATHS = $(foreach test_binary,$(TEST_BINARY_BASENAMES),test/$(test_binary))
.PHONY: all run test clean

all: run-shell-compile clean

run-read-compile:
	./src/pico_c_compiler.py -p -s 100 -e 200 -m ./input.picoc ./output.reti

run-read-compile-comments:
	./src/pico_c_compiler.py -p -v -s 100 -e 200 -m ./input.picoc ./output.reti

run-read-compile-arg:
	./src/pico_c_compiler.py -p -s 100 -e 200 -m ./test/$(ARG) ./output.reti

run-shell-compile:
	./src/pico_c_compiler.py -p -s 100 -e 200 -m

run-shell-compile-comments:
	./src/pico_c_compiler.py -p -v -s 100 -e 200 -m

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

test:
	# for test_binary in $(TEST_BINARY_BASENAMES); do \
	# 	python -m $$test_binary; \
	# done
	echo $(TEST_BINARY_PATHS)
	for test_binary in $(TEST_BINARY_PATHS); do \
		./$$test_binary; \
	done

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
