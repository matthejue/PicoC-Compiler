# SHELL := /bin/bash
TESTNAME_BASE = $(shell basename --suffix=.picoc $(TESTNAME))
FILETYPE ?= reti_states
PAGES ?= 5
.PHONY: all test clean

all: interpret-color

install:
	pip install -r ./requirements.txt
	@sudo -- sh -c '[[ ! -f /usr/local/bin/picoc_compiler ]] && ln -sr ./src/main.py /usr/local/bin/picoc_compiler && echo compiler /usr/local/bin/picoc_compiler was successfully installed || echo compiler /usr/local/bin/picoc_compiler is already installed'
	@[[ ! -d ~/.config/picoc_compiler ]] && mkdir ~/.config/picoc_compiler && echo config folder ~/.config/picoc_compiler created || echo config folder ~/.config/picoc_compiler does already exist
	@[[ ! -f ~/.config/picoc_compiler/history.json ]] && touch ~/.config/picoc_compiler/history.json && echo history file ~/.config/picoc_compiler/history.json created || echo history file ~/.config/picoc_compiler/history.json does already exist
	@[[ ! -f ~/.config/picoc_compiler/settings.conf.json ]] && touch ~/.config/picoc_compiler/settings.conf.json && echo settings file ~/.config/picoc_compiler/settings.conf.json created || echo settings file ~/.config/picoc_compiler/settings.conf.json does already exist
	@[[ ! -f ~/.config/picoc_compiler/interpr_showcase.vim ]] && ln -sr ./interpr_showcase.vim ~/.config/picoc_compiler/interpr_showcase.vim && echo interpreter-showcase-config file ~/.config/picoc_compiler/interpr_showcase.vim created || echo interpreter-showcase-config file ~/.config/picoc_compiler/interpr_showcase.vim does already exist
	@[[ ! -f ~/.config/picoc_compiler/most_used_compile_opts.txt ]] && ln -sr ./most_used_compile_opts.txt ~/.config/picoc_compiler/most_used_compile_opts.txt && echo most-used-compile-options file ~/.config/picoc_compiler/most_used_compile_opts.txt created || echo most-used-compile-options file ~/.config/picoc_compiler/most_used_compile_opts.txt does already exist
	@[[ ! -f ~/.config/picoc_compiler/most_used_interpret_opts.txt ]] && ln -sr ./most_used_interpret_opts.txt ~/.config/picoc_compiler/most_used_interpret_opts.txt && echo most-used-interpret-options file ~/.config/picoc_compiler/most_used_interpret_opts.txt created || echo most-used-interpret-options file ~/.config/picoc_compiler/most_used_interpret_opts.txt does already exist

uninstall:
	pip uninstall -r ./requirements.txt
	@sudo -- sh -c '[[ -f /usr/local/bin/picoc_compiler ]] && rm /usr/local/bin/picoc_compiler && echo compiler /usr/local/bin/picoc_compiler was successfully uninstalled || echo compiler /usr/local/bin/picoc_compiler is already uninstalled'
	@[[ -f ~/.config/picoc_compiler/history.json ]] && rm ~/.config/picoc_compiler/history.json && echo history file ~/.config/picoc_compiler/history.json was deleted || echo history file ~/.config/picoc_compiler/history.json is already deleted
	@[[ -f ~/.config/picoc_compiler/settings.conf.json ]] && rm ~/.config/picoc_compiler/settings.conf.json && echo settings file ~/.config/picoc_compiler/settings.conf.json was deleted || echo settings file ~/.config/picoc_compiler/settings.conf.json is already deleted
	@[[ -f ~/.config/picoc_compiler/interpr_showcase.vim ]] && rm ~/.config/picoc_compiler/interpr_showcase.vim && echo interpter-showcase-config file ~/.config/picoc_compiler/interpr_showcase.vim was deleted || echo interpreter-showcase-config file ~/.config/picoc_compiler/interpr_showcase.vim is already deleted
	@[[ -f ~/.config/picoc_compiler/most_used_compile_opts.txt ]] && rm ~/.config/picoc_compiler/most_used_compile_opts.txt && echo most-used-compile-options file ~/.config/picoc_compiler/most_used_compile_opts.txt was deleted || echo most-used-compile-options file ~/.config/picoc_compiler/most_used_compile_opts.txt is already deleted
	@[[ -f ~/.config/picoc_compiler/most_used_interpret_opts.txt ]] && rm ~/.config/picoc_compiler/most_used_interpret_opts.txt && echo most-used-interpert-options file ~/.config/picoc_compiler/most_used_interpret_opts.txt was deleted || echo most-used-interpret-options file ~/.config/picoc_compiler/most_used_interpret_opts.txt is already deleted
	@[[ -d ~/.config/picoc_compiler ]] && rmdir ~/.config/picoc_compiler && echo config folder ~/.config/picoc_compiler was deleted || echo config folder ~/.config/picoc_compiler is already deleted

compile: _compile _clean-pycache
_compile:
	./src/main.py $$(cat ./most_used_compile_opts.txt) ./run/*.picoc

compile-verbose: _compile-verbose _clean-pycache
_compile-verbose:
	./src/main.py $$(cat ./most_used_compile_opts.txt) -vv ./run/*.picoc

compile-color: _compile-color _clean-pycache
_compile-color:
	./src/main.py $$(cat ./most_used_compile_opts.txt) -c ./run/*.picoc

compile-debug: _compile-debug _clean-pycache
_compile-debug:
	./src/main.py $$(cat ./most_used_compile_opts.txt) -d ./run/*.picoc

interpret: _interpret _clean-pycache
_interpret:
	./src/main.py $$(cat ./most_used_interpret_opts.txt) ./run/*.picoc

interpret-verbose: _interpret-verbose _clean-pycache
_interpret-verbose:
	./src/main.py $$(cat ./most_used_interpret_opts.txt) -vv ./run/*.picoc

interpret-color: _interpret-color _clean-pycache
_interpret-color:
	./src/main.py $$(cat ./most_used_interpret_opts.txt) -c ./run/*.picoc

interpret-debug: _interpret-debug _clean-pycache
_interpret-debug:
	./src/main.py $$(cat ./most_used_interpret_opts.txt) -d ./run/*.picoc

shell: _shell _clean-pychache
_shell:
	./src/main.py

extract:
	./extract_input_and_expected.sh $(TESTNAME_BASE)

test: _test _clean-pycache
test-clean: _test clean
_test:
	# start with 'make test-arg ARG=file_basename'
	# DEBUG=-d for debugging
	-./export_environment_vars_for_makefile.sh;\
	./run_tests.sh $${COLUMNS} $(TESTNAME_BASE) $(VERBOSE) $(DEBUG);

test-show:
ifeq ($(PAGES),8)
	-./export_environment_vars_for_makefile.sh;\
	./run_tests.sh $${COLUMNS} $(TESTNAME_BASE) $(VERBOSE) $(DEBUG);\
	LINE_NUM1=$$(expr $${LINES} + 1 - 1);\
	LINE_NUM2=$$(expr $${LINES} '*' 2 + 1 - 2);\
	LINE_NUM3=$$(expr $${LINES} '*' 3 + 1 - 3);\
	LINE_NUM4=$$(expr $${LINES} '*' 4 + 1 - 4);\
	LINE_NUM5=$$(expr $${LINES} '*' 5 + 1 - 5);\
	LINE_NUM6=$$(expr $${LINES} '*' 6 + 1 - 6);\
	LINE_NUM7=$$(expr $${LINES} '*' 7 + 1 - 7);\
	nvim ./tests/*$(TESTNAME_BASE)*.$(FILETYPE) -u ~/.config/picoc_compiler/interpr_showcase.vim -c "$${LINE_NUM7} | norm zt" -c "$$vs | {LINE_NUM6} | norm zt" -c "vs | $${LINE_NUM5} | norm zt" -c "vs | $${LINE_NUM4} | norm zt" -c "vs | $${LINE_NUM3} | norm zt" -c "vs | $${LINE_NUM2} | norm zt" -c "vs | $${LINE_NUM1} | norm zt" -c "vs | 0 | norm zt" -c "windo se scb!" -c "wincmd h | wincmd h | wincmd h | wincmd h | wincmd h | wincmd h | wincmd h"
else ifeq ($(PAGES),7)
	-./export_environment_vars_for_makefile.sh;\
	./run_tests.sh $${COLUMNS} $(TESTNAME_BASE) $(VERBOSE) $(DEBUG);\
	LINE_NUM1=$$(expr $${LINES} + 1 - 1);\
	LINE_NUM2=$$(expr $${LINES} '*' 2 + 1 - 2);\
	LINE_NUM3=$$(expr $${LINES} '*' 3 + 1 - 3);\
	LINE_NUM4=$$(expr $${LINES} '*' 4 + 1 - 4);\
	LINE_NUM5=$$(expr $${LINES} '*' 5 + 1 - 5);\
	LINE_NUM6=$$(expr $${LINES} '*' 6 + 1 - 6);\
	nvim ./tests/*$(TESTNAME_BASE)*.$(FILETYPE) -u ~/.config/picoc_compiler/interpr_showcase.vim -c "$${LINE_NUM6} | norm zt" -c "vs | $${LINE_NUM5} | norm zt" -c "vs | $${LINE_NUM4} | norm zt" -c "vs | $${LINE_NUM3} | norm zt" -c "vs | $${LINE_NUM2} | norm zt" -c "vs | $${LINE_NUM1} | norm zt" -c "vs | 0 | norm zt" -c "windo se scb!" -c "wincmd h | wincmd h | wincmd h | wincmd h | wincmd h | wincmd h"
else ifeq ($(PAGES),6)
	-./export_environment_vars_for_makefile.sh;\
	./run_tests.sh $${COLUMNS} $(TESTNAME_BASE) $(VERBOSE) $(DEBUG);\
	LINE_NUM1=$$(expr $${LINES} + 1 - 1);\
	LINE_NUM2=$$(expr $${LINES} '*' 2 + 1 - 2);\
	LINE_NUM3=$$(expr $${LINES} '*' 3 + 1 - 3);\
	LINE_NUM4=$$(expr $${LINES} '*' 4 + 1 - 4);\
	LINE_NUM5=$$(expr $${LINES} '*' 5 + 1 - 5);\
	nvim ./tests/*$(TESTNAME_BASE)*.$(FILETYPE) -u ~/.config/picoc_compiler/interpr_showcase.vim -c "$${LINE_NUM5} | norm zt" -c "vs | $${LINE_NUM4} | norm zt" -c "vs | $${LINE_NUM3} | norm zt" -c "vs | $${LINE_NUM2} | norm zt" -c "vs | $${LINE_NUM1} | norm zt" -c "vs | 0 | norm zt" -c "windo se scb!" -c "wincmd h | wincmd h | wincmd h | wincmd h | wincmd h"
else ifeq ($(PAGES),5)
	-./export_environment_vars_for_makefile.sh;\
	./run_tests.sh $${COLUMNS} $(TESTNAME_BASE) $(VERBOSE) $(DEBUG);\
	LINE_NUM1=$$(expr $${LINES} + 1 - 1);\
	LINE_NUM2=$$(expr $${LINES} '*' 2 + 1 - 2);\
	LINE_NUM3=$$(expr $${LINES} '*' 3 + 1 - 3);\
	LINE_NUM4=$$(expr $${LINES} '*' 4 + 1 - 4);\
	nvim ./tests/*$(TESTNAME_BASE)*.$(FILETYPE) -u ~/.config/picoc_compiler/interpr_showcase.vim -c "$${LINE_NUM4} | norm zt" -c "vs | $${LINE_NUM3} | norm zt" -c "vs | $${LINE_NUM2} | norm zt" -c "vs | $${LINE_NUM1} | norm zt" -c "vs | 0 | norm zt" -c "windo se scb!" -c "wincmd h | wincmd h | wincmd h | wincmd h"
else ifeq ($(PAGES),4)
	-./export_environment_vars_for_makefile.sh;\
	./run_tests.sh $${COLUMNS} $(TESTNAME_BASE) $(VERBOSE) $(DEBUG);\
	LINE_NUM1=$$(expr $${LINES} + 1 - 1);\
	LINE_NUM2=$$(expr $${LINES} '*' 2 + 1 - 2);\
	LINE_NUM3=$$(expr $${LINES} '*' 3 + 1 - 3);\
	nvim ./tests/*$(TESTNAME_BASE)*.$(FILETYPE) -u ~/.config/picoc_compiler/interpr_showcase.vim  -c "$${LINE_NUM3} | norm zt" -c "vs | $${LINE_NUM2} | norm zt" -c "vs | $${LINE_NUM1} | norm zt" -c "vs | 0 | norm zt" -c "windo se scb!" -c "wincmd h | wincmd h | wincmd h"
else ifeq ($(PAGES),3)
	-./export_environment_vars_for_makefile.sh;\
	./run_tests.sh $${COLUMNS} $(TESTNAME_BASE) $(VERBOSE) $(DEBUG);\
	LINE_NUM1=$$(expr $${LINES} + 1 - 1);\
	LINE_NUM2=$$(expr $${LINES} '*' 2 + 1 - 2);\
	nvim ./tests/*$(TESTNAME_BASE)*.$(FILETYPE) -u ~/.config/picoc_compiler/interpr_showcase.vim -c "$${LINE_NUM2} | norm zt" -c "vs | $${LINE_NUM1} | norm zt" -c "vs | 0 | norm zt" -c "windo se scb!" -c "wincmd h | wincmd h"
else ifeq ($(PAGES),2)
	-./export_environment_vars_for_makefile.sh;\
	./run_tests.sh $${COLUMNS} $(TESTNAME_BASE) $(VERBOSE) $(DEBUG);\
	LINE_NUM1=$$(expr $${LINES} + 1 - 1);\
	nvim ./tests/*$(TESTNAME_BASE)*.$(FILETYPE) -u ~/.config/picoc_compiler/interpr_showcase.vim -c "$${LINE_NUM1} | norm zt" -c "vs | 0 | norm zt" -c "windo se scb!" -c "wincmd h"
else ifeq ($(PAGES),1)
	-./export_environment_vars_for_makefile.sh;\
	./run_tests.sh $${COLUMNS} $(TESTNAME_BASE) $(VERBOSE) $(DEBUG);\
	nvim ./tests/*$(TESTNAME_BASE)*.$(FILETYPE) -u ~/.config/picoc_compiler/interpr_showcase.vim -c "0 | norm zt"
endif

show:
ifeq ($(PAGES),5)
	-./export_environment_vars_for_makefile.sh;\
	LINE_NUM1=$$(expr $${LINES} + 1 - 1);\
	LINE_NUM2=$$(expr $${LINES} '*' 2 + 1 - 2);\
	LINE_NUM3=$$(expr $${LINES} '*' 3 + 1 - 3);\
	LINE_NUM4=$$(expr $${LINES} '*' 4 + 1 - 4);\
	nvim $(FILEPATH) -u ~/.config/picoc_compiler/interpr_showcase.vim -c "$${LINE_NUM4} | norm zt" -c "vs | $${LINE_NUM3} | norm zt" -c "vs | $${LINE_NUM2} | norm zt" -c "vs | $${LINE_NUM1} | norm zt" -c "vs | 0 | norm zt" -c "windo se scb!" -c "wincmd h | wincmd h | wincmd h | wincmd h"
else ifeq ($(PAGES),4)
	-./export_environment_vars_for_makefile.sh;\
	LINE_NUM1=$$(expr $${LINES} + 1 - 1);\
	LINE_NUM2=$$(expr $${LINES} '*' 2 + 1 - 2);\
	LINE_NUM3=$$(expr $${LINES} '*' 3 + 1 - 3);\
	nvim $(FILEPATH) -u ~/.config/picoc_compiler/interpr_showcase.vim  -c "$${LINE_NUM3} | norm zt" -c "vs | $${LINE_NUM2} | norm zt" -c "vs | $${LINE_NUM1} | norm zt" -c "vs | 0 | norm zt" -c "windo se scb!" -c "wincmd h | wincmd h | wincmd h"
else ifeq ($(PAGES),3)
	-./export_environment_vars_for_makefile.sh;\
	LINE_NUM1=$$(expr $${LINES} + 1 - 1);\
	LINE_NUM2=$$(expr $${LINES} '*' 2 + 1 - 2);\
	nvim .$(FILEPATH) -u ~/.config/picoc_compiler/interpr_showcase.vim -c "$${LINE_NUM2} | norm zt" -c "vs | $${LINE_NUM1} | norm zt" -c "vs | 0 | norm zt" -c "windo se scb!" -c "wincmd h | wincmd h"
else ifeq ($(PAGES),2)
	-./export_environment_vars_for_makefile.sh;\
	LINE_NUM1=$$(expr $${LINES} + 1 - 1);\
	nvim $(FILEPATH) -u ~/.config/picoc_compiler/interpr_showcase.vim -c "$${LINE_NUM1} | norm zt" -c "vs | 0 | norm zt" -c "windo se scb!" -c "wincmd h"
else ifeq ($(PAGES),1)
	-./export_environment_vars_for_makefile.sh;\
	nvim $(FILEPATH) -u ~/.config/picoc_compiler/interpr_showcase.vim -c "0 | norm zt"
endif

convert:  extract
	./convert_to_c.py $(TESTNAME_BASE)

verify: extract convert _verify
verify-clean: extract convert _verify _clean-files
_verify:
	./export_environment_vars_for_makefile.sh; \
	./verify_tests.sh $${COLUMNS} $(TESTNAME_BASE)

help:
	./src/main.py -h -c
	./src/main.py -h > ./doc/help-page.txt
	sed "s/most_used_interpret_opts/$$(cat ./most_used_interpret_opts.txt)/" ./doc/getting_started_raw.md > ./doc/getting_started.md


clean: _clean-pycache _clean-files
_clean-pycache:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

_clean-files:
	find . -type f -wholename "./tests/*.tokens" -delete
	find . -type f -wholename "./tests/*.dt" -delete
	find . -type f -wholename "./tests/*.dt_simple" -delete
	find . -type f -wholename "./tests/*.ast" -delete
	find . -type f -wholename "./tests/*.st_mon" -delete
	find . -type f -wholename "./tests/*.st" -delete
	find . -type f -wholename "./tests/*.picoc_shrink" -delete
	find . -type f -wholename "./tests/*.picoc_blocks" -delete
	find . -type f -wholename "./tests/*.picoc_patch" -delete
	find . -type f -wholename "./tests/*.picoc_mon" -delete
	find . -type f -wholename "./tests/*.reti_blocks" -delete
	find . -type f -wholename "./tests/*.reti_patch" -delete
	find . -type f -wholename "./tests/*.reti" -delete
	find . -type f -wholename "./tests/*.error" -delete
	find . -type f -wholename "./tests/*.c" -delete
	find . -type f -wholename "./tests/*.c_out" -delete
	find . -type f -wholename "./tests/*.reti_tokens" -delete
	find . -type f -wholename "./tests/*.reti_ast" -delete
	find . -type f -wholename "./tests/*.in" -delete
	find . -type f -wholename "./tests/*.out" -delete
	find . -type f -wholename "./tests/*.out_expected" -delete
	find . -type f -wholename "./tests/*.datasegment_size" -delete
	find . -type f -wholename "./tests/*.reti_states" -delete
	find . -type f -wholename "./tests/*.c" -delete
	find . -type f -wholename "./tests/*.c_out" -delete
	find . -type f -wholename "./tests/*.res" -delete

record:
	asciinema rec -i 1 -t $(TESTNAME).cast --overwrite

upload:
	asciinema upload $(TESTNAME).cast

setup_pyinstaller_linux:
	python -m pip install --upgrade pip
	pip install tabulate
	pip install pyinstaller
	pip install staticx
	pip install patchelf-wrapper

setup_pyinstaller_wine:
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 winecfg
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/Python10/python.exe -m pip install --upgrade pip
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/Python10/python.exe -m pip install tabulate
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/Python10/python.exe -m pip install pyinstaller

setup_pyinstaller_windows:
	python -m pip install --upgrade pip
	pip install tabulate
	pip install pyinstaller

create_bin_linux:
	pyinstaller ./src/main.py --onefile --hidden-import=tabulate,cmd2,colorama,bitstring --distpath=./dist
	staticx ./dist/main ./dist/pico_c_compiler_linux
	rm ./dist/main

create_bin_wine:
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/Python10/Scripts/pyinstaller.exe ~/Applications/Windows10/drive_c/users/areo/Documents/Studium/pico_c_compiler/src/main.py  --onefile --hidden-import=tabulate --distpath=~/Documents/Studium/pico_c_compiler/dist
	mv ~/Documents/Studium/pico_c_compiler/dist/pico_c_compiler.exe ~/Documents/Studium/pico_c_compiler/dist/pico_c_compiler_wine.exe

create_bin_windows:
	pyinstaller src\main.py --onefile --hidden-import=tabulate,cmd2,colorama,bitstring --distpath=dist
	staticx ./dist/main.exe ./dist/pico_c_compiler_windows.exe
	# entferne ./dist/main.exe

exec_bin_linux:
	./dist/pico_c_compiler_linux -S

exec_bin_wine:
	WINEPREFIX=~/Applications/Windows10 WINEARCH=win32 wine ~/Applications/Windows10/drive_c/users/areo/Documents/Studium/pico_c_compiler/dist/pico_c_compiler_wine.exe -S

exec_bin_windows:
	# go into dist folder in explorer and ctrl+l and type cmd and hit enter
	pico_c_compiler_windows.exe -S
