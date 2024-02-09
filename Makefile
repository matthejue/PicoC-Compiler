.PHONY: clean

install:
	@sudo bash -c "([[ -f /usr/local/bin/picoc_compiler ]] || rm /usr/local/bin/picoc_compiler) && sed -i \"s|#!.*|#!$(realpath .)/.virtualenv/bin/python|\" ./src/main.py && chmod 755 ./src/main.py && sudo ln -s $(realpath .)/src/main.py /usr/local/bin/picoc_compiler"

clean: _clean-pycache _clean-files
_clean-pycache:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

_clean-files:
	find . -type f -wholename "./tests/*.tokens" -delete
	find . -type f -wholename "./tests/*.rtokens" -delete
	find . -type f -wholename "./tests/*.dt" -delete
	find . -type f -wholename "./tests/*.rdt" -delete
	find . -type f -wholename "./tests/*.dt_simple" -delete
	find . -type f -wholename "./tests/*.ast" -delete
	find . -type f -wholename "./tests/*.rast" -delete
	find . -type f -wholename "./tests/*.st_mon" -delete
	find . -type f -wholename "./tests/*.st" -delete
	find . -type f -wholename "./tests/*.picoc_shrink" -delete
	find . -type f -wholename "./tests/*.picoc_blocks" -delete
	find . -type f -wholename "./tests/*.picoc_patch" -delete
	find . -type f -wholename "./tests/*.picoc_anf" -delete
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
	find . -type f -wholename "./tests/*.eprom" -delete
	find . -type f -wholename "./tests/*.c" -delete
	find . -type f -wholename "./tests/*.c_out" -delete
	find . -type f -wholename "./tests/*.res" -delete

record:
	asciinema rec -i 1 -t $(TESTNAME) --overwrite

upload:
	asciinema upload $(TESTNAME).cast

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
