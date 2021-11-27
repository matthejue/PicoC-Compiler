let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/Documents/Studium/pico_c_compiler
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +18 src/abstract_syntax_tree.py
badd +1 src/arithmetic_expression_grammar.py
badd +47 src/arithmetic_nodes.py
badd +23 src/assignment_allocation_grammar.py
badd +1 src/assignment_allocation_nodes.py
badd +27 src/ast_builder.py
badd +22 src/code_generator.py
badd +43 src/errors.py
badd +44 src/function_grammar.py
badd +1 src/function_nodes.py
badd +1 src/global_vars.py
badd +18 src/grammar.py
badd +9 src/if_else_grammar.py
badd +26 src/if_else_nodes.py
badd +19 src/lexer.py
badd +35 src/lexer_2.py
badd +1 src/logic_expression_grammar.py
badd +1 src/logic_nodes.py
badd +1 src/loop_grammar.py
badd +1 src/loop_nodes.py
badd +56 src/parser_.py
badd +27 src/pico_c_compiler.py
badd +49 src/statement_grammar.py
badd +1 src/symbol_table.py
badd +43 test/parser_test.py
badd +43 test/code_generator_test.py
badd +43 test/testing_helpers.py
badd +1 statement_nodes.py
badd +3 test/execution_test.py
badd +7 test/misc_test.py
badd +6 Makefile
badd +1 input.picoc
badd +1 output.reti
badd +15 .vimspector.json
badd +1 /tmp/crap
badd +3 output.csv
badd +237 test/error_message_test.py
argglobal
%argdel
$argadd src/abstract_syntax_tree.py
$argadd src/arithmetic_expression_grammar.py
$argadd src/arithmetic_nodes.py
$argadd src/assignment_allocation_grammar.py
$argadd src/assignment_allocation_nodes.py
$argadd src/ast_builder.py
$argadd src/code_generator.py
$argadd src/errors.py
$argadd src/function_grammar.py
$argadd src/function_nodes.py
$argadd src/global_vars.py
$argadd src/grammar.py
$argadd src/if_else_grammar.py
$argadd src/if_else_nodes.py
$argadd src/lexer.py
$argadd src/lexer_2.py
$argadd src/logic_expression_grammar.py
$argadd src/logic_nodes.py
$argadd src/loop_grammar.py
$argadd src/loop_nodes.py
$argadd src/parser_.py
$argadd src/pico_c_compiler.py
$argadd src/statement_grammar.py
$argadd statement_nodes.py
$argadd src/symbol_table.py
edit src/statement_grammar.py
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe '2resize ' . ((&lines * 1 + 19) / 39)
exe 'vert 2resize ' . ((&columns * 154 + 79) / 158)
argglobal
if bufexists("src/statement_grammar.py") | buffer src/statement_grammar.py | else | edit src/statement_grammar.py | endif
if &buftype ==# 'terminal'
  silent file src/statement_grammar.py
endif
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
let s:l = 49 - ((18 * winheight(0) + 18) / 37)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 49
normal! 03|
wincmd w
argglobal
enew
balt src/statement_grammar.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
wincmd w
exe '2resize ' . ((&lines * 1 + 19) / 39)
exe 'vert 2resize ' . ((&columns * 154 + 79) / 158)
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0&& getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxAoOaFTtI
let &winminheight = s:save_winminheight
let &winminwidth = s:save_winminwidth
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
