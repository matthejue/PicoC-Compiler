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
badd +100 src/abstract_syntax_tree.py
badd +1 src/arithmetic_expression_grammar.py
badd +73 src/arithmetic_nodes.py
badd +1 src/assignment_allocation_grammar.py
badd +1 src/assignment_allocation_nodes.py
badd +1 src/ast_builder.py
badd +22 src/code_generator.py
badd +1 src/errors.py
badd +1 src/function_grammar.py
badd +1 src/function_nodes.py
badd +1 src/global_vars.py
badd +1 src/grammar.py
badd +9 src/if_else_grammar.py
badd +26 src/if_else_nodes.py
badd +1 src/lexer.py
badd +1 src/lexer_2.py
badd +1 src/logic_expression_grammar.py
badd +1 src/logic_nodes.py
badd +1 src/loop_grammar.py
badd +1 src/loop_nodes.py
badd +1 src/parser_.py
badd +1 src/pico_c_compiler.py
badd +1 src/statement_grammar.py
badd +1 src/symbol_table.py
badd +1 test/parser_test.py
badd +99 test/code_generator_test.py
badd +1 ~/.config_stow/nvim/.config/nvim/plugin_settings.vim
badd +47 test/testing_helpers.py
badd +1 statement_nodes.py
badd +3 test/execution_test.py
badd +7 test/misc_test.py
badd +6 Makefile
badd +1 input.picoc
badd +1 output.reti
badd +15 .vimspector.json
badd +1 /tmp/crap
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
edit src/arithmetic_nodes.py
argglobal
if bufexists("src/arithmetic_nodes.py") | buffer src/arithmetic_nodes.py | else | edit src/arithmetic_nodes.py | endif
if &buftype ==# 'terminal'
  silent file src/arithmetic_nodes.py
endif
balt input.picoc
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
let s:l = 73 - ((21 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 73
normal! 0
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0&& getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxAoOaFTtI
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
