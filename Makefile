.PHONY: test run clean run_send_keypresses

TEST_PATTERN ?= $(shell cat ./opts/test_pattern.txt)
RUN_PATH ?= $(shell cat ./opts/run_path.txt)
DEBUG_PATH ?= $(shell cat ./opts/debug_path.txt)
EXTRA_CPL_ARGS ?=
EXTRA_EMU_ARGS ?=

full-install: install-dependencies install-global

SHELL := /bin/bash
install-dependencies:
	python -m venv .virtualenv && source .virtualenv/bin/activate && pip install -r requirements.txt && sed -i "s|#!.*|#!$(realpath .)/.virtualenv/bin/python|" ./src/main.py && chmod 500 ./src/main.py

install-global:
	@sudo bash -c "if [ -L /usr/local/bin/picoc_compiler ]; then rm -f /usr/local/bin/picoc_compiler; fi && sudo ln -s $(realpath .)/run.py /usr/local/bin/picoc_compiler"

clean: _clean-pycache _clean-files
_clean-pycache:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

_clean-files:
	find . -type f -wholename "./sys_tests/*.tokens" -delete
	find . -type f -wholename "./sys_tests/*.rtokens" -delete
	find . -type f -wholename "./sys_tests/*.ps" -delete
	find . -type f -wholename "./sys_tests/*.dt" -delete
	find . -type f -wholename "./sys_tests/*.rdt" -delete
	find . -type f -wholename "./sys_tests/*.dt_simple" -delete
	find . -type f -wholename "./sys_tests/*.ast" -delete
	find . -type f -wholename "./sys_tests/*.rast" -delete
	find . -type f -wholename "./sys_tests/*.st" -delete
	find . -type f -wholename "./sys_tests/*.picoc_shrink" -delete
	find . -type f -wholename "./sys_tests/*.picoc_blocks" -delete
	find . -type f -wholename "./sys_tests/*.picoc_symbol" -delete
	find . -type f -wholename "./sys_tests/*.picoc_typing" -delete
	find . -type f -wholename "./sys_tests/*.picoc_anf" -delete
	find . -type f -wholename "./sys_tests/*.reti_blocks" -delete
	find . -type f -wholename "./sys_tests/*.reti_patch" -delete
	find . -type f -wholename "./sys_tests/*.reti" -delete
	find . -type f -wholename "./sys_tests/*.error" -delete
	find . -type f -wholename "./sys_tests/*.c" -delete
	find . -type f -wholename "./sys_tests/*.c_output" -delete
	find . -type f -wholename "./sys_tests/*.reti_tokens" -delete
	find . -type f -wholename "./sys_tests/*.reti_ast" -delete
	find . -type f -wholename "./sys_tests/*.input" -delete
	find . -type f -wholename "./sys_tests/*.output" -delete
	find . -type f -wholename "./sys_tests/*.expected_output" -delete
	find . -type f -wholename "./sys_tests/*.datasegment_size" -delete
	find . -type f -wholename "./sys_tests/*.debuginfo" -delete
	find . -type f -wholename "./sys_tests/*.sections" -delete
	find . -type f -wholename "./sys_tests/*.reti_states" -delete
	find . -type f -wholename "./sys_tests/*.eprom" -delete
	find . -type f -wholename "./sys_tests/*.c" -delete
	find . -type f -wholename "./sys_tests/*.res" -delete
	find ./vendor/tree-sitter-reti/src -type f \( -name "grammar.json" -o -name "node-types.json" -o -name "parser.c" \) -delete
	find ./vendor/tree-sitter-reti/src -type d -name "tree_sitter" -exec rm -rf {} +

test: _test _clean-pycache
test-clean: _test clean
_test:
	# start with 'make test-arg ARG=file_basename'
	# DEBUG=-d for debugging
	./export_environment_vars_for_makefile.sh;\
	./run_sys_tests.sh $${COLUMNS} "$(TEST_PATTERN)" "$(EXTRA_CPL_ARGS)" "$(EXTRA_EMU_ARGS)"

run:
	./run.sh "$(RUN_PATH)" "$(EXTRA_CPL_ARGS)" "$(EXTRA_EMU_ARGS)"

debug:
	./debug.sh "$(DEBUG_PATH)" "$(EXTRA_CPL_ARGS)" "$(EXTRA_EMU_ARGS)"

setup_pyinstaller_linux:
	python -m pip install --upgrade pip
	pip install tabulate
	pip install pyinstaller
	pip install staticx
	pip install patchelf-wrapper

create_bin_linux:
	pyinstaller ./src/main.py --onefile --hidden-import=tabulate,bitstring --distpath=./dist
	staticx ./dist/main ./dist/pico_c_compiler_linux
	rm ./dist/main

exec_bin_linux:
	./dist/pico_c_compiler_linux -S

run_send_keypresses:
	@set -e; \
	run_path="$(RUN_PATH)"; \
	if [[ "$$run_path" == *.picoc ]]; then \
		compiled_path="$${run_path%.picoc}.reti"; \
		./run.py $$(cat ./opts/run_cpl_opts.txt) $(EXTRA_CPL_ARGS) "$$run_path" -o "$$compiled_path"; \
		run_path="$$compiled_path"; \
	fi; \
	./send_keypresses.py --input ./opts/input.txt reti_emulator $$(cat ./opts/run_emu_opts.txt) $(EXTRA_EMU_ARGS) "$$run_path"
