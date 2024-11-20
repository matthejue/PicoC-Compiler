TESTNAME_BASE = $(shell basename --suffix=.picoc $(TESTNAME))
.PHONY: clean

full-install: install-dependencies install

install-dependencies:
	python -m venv .virtualenv && source .virtualenv/bin/activate && pip install -r requirements.txt

install:
	@sudo bash -c "([[ ! -f /usr/local/bin/picoc_compiler ]] || rm /usr/local/bin/picoc_compiler) && sed -i \"s|#!.*|#!$(realpath .)/.virtualenv/bin/python|\" ./src/main.py && chmod 755 ./src/main.py && sudo ln -s $(realpath .)/src/main.py /usr/local/bin/picoc_compiler"

clean: _clean-pycache _clean-files
_clean-pycache:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

_clean-files:
	find . -type f -wholename "./sys_tests/*.tokens" -delete
	find . -type f -wholename "./sys_tests/*.rtokens" -delete
	find . -type f -wholename "./sys_tests/*.dt" -delete
	find . -type f -wholename "./sys_tests/*.rdt" -delete
	find . -type f -wholename "./sys_tests/*.dt_simple" -delete
	find . -type f -wholename "./sys_tests/*.ast" -delete
	find . -type f -wholename "./sys_tests/*.rast" -delete
	find . -type f -wholename "./sys_tests/*.st_mon" -delete
	find . -type f -wholename "./sys_tests/*.st" -delete
	find . -type f -wholename "./sys_tests/*.picoc_shrink" -delete
	find . -type f -wholename "./sys_tests/*.picoc_blocks" -delete
	find . -type f -wholename "./sys_tests/*.picoc_patch" -delete
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
	# find . -type f -wholename "./sys_tests/*.out" -delete
	find . -type f -wholename "./sys_tests/*.expected_output" -delete
	find . -type f -wholename "./sys_tests/*.datasegment_size" -delete
	find . -type f -wholename "./sys_tests/*.reti_states" -delete
	find . -type f -wholename "./sys_tests/*.eprom" -delete
	find . -type f -wholename "./sys_tests/*.c" -delete
	find . -type f -wholename "./sys_tests/*.res" -delete

test: _test _clean-pycache
test-clean: _test clean
_test:
	# start with 'make test-arg ARG=file_basename'
	# DEBUG=-d for debugging
	./export_environment_vars_for_makefile.sh;\
	./run_sys_tests.sh $${COLUMNS} $(TESTNAME_BASE) $(EXTRA_ARGS)

setup_pyinstaller_linux:
	python -m pip install --upgrade pip
	pip install tabulate
	pip install pyinstaller
	pip install staticx
	pip install patchelf-wrapper

create_bin_linux:
	pyinstaller ./src/main.py --onefile --hidden-import=tabulate,cmd2,colorama,bitstring --distpath=./dist
	staticx ./dist/main ./dist/pico_c_compiler_linux
	rm ./dist/main

exec_bin_linux:
	./dist/pico_c_compiler_linux -S
