let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/Documents/Studium/pico_c_compiler/src
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
argglobal
%argdel
$argadd ~/Documents/Studium/pico_c_compiler/.misc/test.cpp
edit ~/Documents/Studium/pico_c_compiler/__Tagbar__.1
argglobal
balt ~/Documents/Studium/pico_c_compiler/NERD_tree_8
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal nofen
silent! normal! zE
let &fdl = &fdl
let s:l = 2 - ((1 * winheight(0) + 19) / 39)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 2
normal! 0
if exists(':tcd') == 2 | tcd ~/Documents/Studium/pico_c_compiler | endif
tabnext 1
badd +13 ~/Documents/Studium/pico_c_compiler/src/grammar.py
badd +0 ~/Documents/Studium/pico_c_compiler/.misc/test.cpp
badd +2 ~/Documents/Studium/pico_c_compiler/__Tagbar__.1
badd +0 ~/Documents/Studium/pico_c_compiler/file_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/NERD_tree_8
badd +1 ~/Documents/Studium/pico_c_compiler/assignment_allocation_grammar.py
badd +6 ~/Documents/Studium/pico_c_compiler/src/dummy_nodes.py
badd +1 ~/Documents/Studium/pico_c_compiler/file_nodes.py
badd +153 ~/Documents/Studium/pico_c_compiler/src/parser_.py
badd +7 ~/Documents/Studium/pico_c_compiler/src/statement_grammar.py
badd +45 ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
badd +128 ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
badd +22 ~/Documents/Studium/pico_c_compiler/src/arithmetic_nodes.py
badd +43 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_grammar.py
badd +4 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_nodes.py
badd +64 ~/Documents/Studium/pico_c_compiler/src/ast_builder.py
badd +105 ~/Documents/Studium/pico_c_compiler/src/code_generator.py
badd +7 ~/Documents/Studium/pico_c_compiler/src/function_grammar.py
badd +58 ~/Documents/Studium/pico_c_compiler/src/if_else_grammar.py
badd +121 ~/Documents/Studium/pico_c_compiler/src/if_else_nodes.py
badd +34 ~/Documents/Studium/pico_c_compiler/src/logic_expression_grammar.py
badd +199 ~/Documents/Studium/pico_c_compiler/src/logic_nodes.py
badd +9 ~/Documents/Studium/pico_c_compiler/src/loop_grammar.py
badd +121 ~/Documents/Studium/pico_c_compiler/src/loop_nodes.py
badd +191 ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py
badd +112 ~/Documents/Studium/pico_c_compiler/src/symbol_table.py
badd +45 ~/Documents/Studium/pico_c_compiler/.misc/lexer_2
badd +5 ~/Documents/Studium/pico_c_compiler/src/file_nodes.py
badd +804 ~/Documents/Studium/pico_c_compiler/tags
badd +1 ~/Documents/Studium/pico_c_compiler/.misc/python_match_args_example.py
badd +46 ~/Documents/Studium/pico_c_compiler/src/function_nodes.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/global_vars.py
badd +127 ~/Documents/Studium/pico_c_compiler/src/lexer.py
badd +2 ~/Documents/Studium/pico_c_compiler/test/code_generator_test.py
badd +1 ~/Documents/Studium/pico_c_compiler/test/error_message_test.py
badd +1 ~/Documents/Studium/pico_c_compiler/test/execution_test.py
badd +1 ~/Documents/Studium/pico_c_compiler/test/lexer_test.py
badd +4 ~/Documents/Studium/pico_c_compiler/test/parser_test.py
badd +13 ~/Documents/Studium/pico_c_compiler/test/testing_helpers.py
badd +39 ~/Documents/Studium/pico_c_compiler/README.md
badd +1 ~/Documents/Studium/pico_c_compiler/.misc/pico_c_compiler
badd +232 ~/.SpaceVim.d/init.toml
badd +20 /tmp/tmp.YF6D7eD13D
badd +8 ~/Documents/Studium/pico_c_compiler/input.picoc
badd +11 ~/Documents/Studium/pico_c_compiler/src/file_grammar.py
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0 && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxcsAoOaFTt
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
set hlsearch
nohlsearch
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
