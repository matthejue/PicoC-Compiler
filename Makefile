.PHONY: test test-clean test_not_passed run clean run_send_keypresses grammars ci-build package android-package

PYTHON ?= python3
ANDROID_API ?= 24
ANDROID_ARCH ?= aarch64
ANDROID_PYTHON_ARCHIVE ?= binary/downloads/python-3.14.6-aarch64-linux-android.tar.gz
ANDROID_TREE_SITTER_ARCHIVE ?= binary/downloads/tree-sitter-0.25.2.tar.gz
ANDROID_ARCHIVE ?= binary/picoc-compiler-android-arm64.tar.gz

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

grammars:
	$(PYTHON) ./scripts/build_tree_sitter.py

ci-build: grammars
	$(PYTHON) -m compileall -q ./source
	$(PYTHON) ./scripts/smoke_test.py

package: ci-build
	$(PYTHON) -m PyInstaller --clean --noconfirm --distpath=./binary --workpath=./binary/build ./source/main.spec

android-package:
	test -d "$(ANDROID_NDK_HOME)"
	test -f "$(ANDROID_PYTHON_ARCHIVE)"
	test -f "$(ANDROID_TREE_SITTER_ARCHIVE)"
	$(PYTHON) ./scripts/package_android.py \
		--ndk "$(ANDROID_NDK_HOME)" \
		--arch "$(ANDROID_ARCH)" \
		--api "$(ANDROID_API)" \
		--python-runtime "$(ANDROID_PYTHON_ARCHIVE)" \
		--tree-sitter-source "$(ANDROID_TREE_SITTER_ARCHIVE)" \
		--output "$(ANDROID_ARCHIVE)"

SHELL := /bin/bash

install-dependencies:
	$(PYTHON) -m venv .virtualenv
	.virtualenv/bin/python -m pip install -r requirements-dev.txt

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
