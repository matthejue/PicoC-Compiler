.PHONY: test test-clean test_not_passed run clean run_send_keypresses

TEST_PATTERN ?= $(shell cat ./config/test_pattern.txt)
RUN_PATH ?= $(shell cat ./config/run_path.txt)
DEBUG_PATH ?= $(shell cat ./config/debug_path.txt)
EXTRA_CPL_ARGS ?=
EXTRA_EMU_ARGS ?=
TEST_BUILD_MODE ?= staged

VALID_TEST_BUILD_MODES := staged direct
ifeq ($(filter $(TEST_BUILD_MODE),$(VALID_TEST_BUILD_MODES)),)
$(error TEST_BUILD_MODE must be 'staged' or 'direct')
endif
TEST_BUILD_OPTION := $(if $(filter direct,$(TEST_BUILD_MODE)),--direct,)

full-install: install-dependencies install-global

SHELL := /bin/bash

install-dependencies:
	python -m venv .virtualenv && source .virtualenv/bin/activate && pip install -r requirements.txt && sed -i "s|#!.*|#!$(realpath .)/.virtualenv/bin/python|" ./source/main.py && chmod 500 ./source/main.py

install-global:
	@sudo bash -c "if [ -L /usr/local/bin/picoc_compiler ]; then rm -f /usr/local/bin/picoc_compiler; fi && sudo ln -s $(realpath .)/run.py /usr/local/bin/picoc_compiler"

clean: _clean-pycache _clean-files

_clean-pycache:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

_clean-files:
	find . -type f -wholename "./test/*.pre" -delete
	find . -type f -wholename "./test/*.tokens" -delete
	find . -type f -wholename "./test/*.rtokens" -delete
	find . -type f -wholename "./test/*.ps" -delete
	find . -type f -wholename "./test/*.dt" -delete
	find . -type f -wholename "./test/*.rdt" -delete
	find . -type f -wholename "./test/*.dt_simple" -delete
	find . -type f -wholename "./test/*.ast" -delete
	find . -type f -wholename "./test/*.rast" -delete
	find . -type f -wholename "./test/*.st" -delete
	find . -type f -wholename "./test/*.picoc_shrink" -delete
	find . -type f -wholename "./test/*.picoc_blocks" -delete
	find . -type f -wholename "./test/*.picoc_symbol" -delete
	find . -type f -wholename "./test/*.picoc_typing" -delete
	find . -type f -wholename "./test/*.picoc_anf" -delete
	find . -type f -wholename "./test/*.reti_blocks" -delete
	find . -type f -wholename "./test/*.reti_patch" -delete
	find . -type f -wholename "./test/*.reti" -delete
	find . -type f -wholename "./test/*.error" -delete
	find . -type f -wholename "./test/*.c" -delete
	find . -type f -wholename "./test/*.c_output" -delete
	find . -type f -wholename "./test/*.reti_tokens" -delete
	find . -type f -wholename "./test/*.reti_ast" -delete
	find . -type f -wholename "./test/*.input" -delete
	find . -type f -wholename "./test/*.output" -delete
	find . -type f -wholename "./test/*.expected_output" -delete
	find . -type f -wholename "./test/*.datasegment_size" -delete
	find . -type f -wholename "./test/*.debuginfo" -delete
	find . -type f -wholename "./test/*.sections" -delete
	find . -type f -wholename "./test/*.reti_states" -delete
	find . -type f -wholename "./test/*.eprom" -delete
	find . -type f -wholename "./test/*.c" -delete
	find . -type f -wholename "./test/*.res" -delete
	find . -type f -wholename "./.test_dependencies/*.d" -delete
	find . -type d -wholename "./.test_dependencies" -empty -delete
	# find ./vendor/tree-sitter-reti/src -type f \( -name "grammar.json" -o -name "node-types.json" -o -name "parser.c" \) -delete
	# find ./vendor/tree-sitter-reti/src -type d -name "tree_sitter" -exec rm -rf {} +

test: _test _clean-pycache

test-clean: _test clean

test_not_passed: _test_not_passed _clean-pycache

_test:
	# start with 'make test-arg ARG=file_basename'
	# DEBUG=-d for debugging
	./export_environment_vars_for_makefile.sh;\
	TEST_JOBS="$(TEST_JOBS)" ./run_sys_tests.sh $(TEST_BUILD_OPTION) "$${COLUMNS:-120}" "$(TEST_PATTERN)" "$(EXTRA_CPL_ARGS)" "$(EXTRA_EMU_ARGS)"

_test_not_passed:
	# Run the whitespace-separated test paths from ./config/not_passed_tests.txt
	./export_environment_vars_for_makefile.sh;\
	TEST_JOBS="$(TEST_JOBS)" ./run_sys_tests.sh --not-passed $(TEST_BUILD_OPTION) "$${COLUMNS:-120}" "" "$(EXTRA_CPL_ARGS)" "$(EXTRA_EMU_ARGS)"

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
	pyinstaller ./source/main.py --onefile --hidden-import=tabulate,bitstring --distpath=./binary
	staticx ./binary/main ./binary/pico_c_compiler_linux
	rm ./binary/main

exec_bin_linux:
	./binary/pico_c_compiler_linux -S

run_send_keypresses:
	@set -e; \
	run_path="$(RUN_PATH)"; \
	if [[ "$$run_path" == *.picoc ]]; then \
		compiled_path="$${run_path%.picoc}.reti"; \
		./run.py $$(cat ./config/run_cpl_opts.txt) $(EXTRA_CPL_ARGS) "$$run_path" -o "$$compiled_path"; \
		run_path="$$compiled_path"; \
	fi; \
	./send_keypresses.py --input ./config/input.txt reti_emulator $$(cat ./config/run_emu_opts.txt) $(EXTRA_EMU_ARGS) "$$run_path"
