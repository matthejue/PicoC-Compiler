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
badd +5 src/abstract_syntax_tree.py
badd +1 src/arithmetic_expression_grammar.py
badd +1 src/assignment_allocation_grammar.py
badd +1 src/ast_builder.py
badd +1 src/errors.py
badd +5 src/function_grammar.py
badd +1 src/globals.py
badd +1 src/grammar.py
badd +1 src/if_else_grammar.py
badd +131 src/lexer.py
badd +24 src/logic_expression_grammar.py
badd +1 src/loop_grammar.py
badd +1 src/parser_.py
badd +1 src/pico_c_compiler.py
badd +14 src/statement_sequence_grammar.py
badd +44 test/grammar_test.py
badd +7 input.picoc
badd +11 test/gcd.picoc
argglobal
%argdel
$argadd src/abstract_syntax_tree.py
$argadd src/arithmetic_expression_grammar.py
$argadd src/assignment_allocation_grammar.py
$argadd src/ast_builder.py
$argadd src/errors.py
$argadd src/function_grammar.py
$argadd src/globals.py
$argadd src/grammar.py
$argadd src/if_else_grammar.py
$argadd src/lexer.py
$argadd src/logic_expression_grammar.py
$argadd src/loop_grammar.py
$argadd src/parser_.py
$argadd src/pico_c_compiler.py
$argadd src/statement_sequence_grammar.py
edit test/gcd.picoc
argglobal
if bufexists("test/gcd.picoc") | buffer test/gcd.picoc | else | edit test/gcd.picoc | endif
if &buftype ==# 'terminal'
  silent file test/gcd.picoc
endif
balt src/function_grammar.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 11 - ((10 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 11
normal! 04|
if exists(':tcd') == 2 | tcd ~/Documents/Studium/pico_c_compiler | endif
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0&& getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxIAoOaFTt
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
