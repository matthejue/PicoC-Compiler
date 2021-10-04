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
badd +610 src/abstract_syntax_tree.py
badd +100 src/arithmetic_expression_grammar.py
badd +37 src/assignment_allocation_grammar.py
badd +5 src/ast_builder.py
badd +1 src/errors.py
badd +1 src/function_grammar.py
badd +3 src/globals.py
badd +1 src/grammar.py
badd +14 src/if_else_grammar.py
badd +3 src/lexer.py
badd +25 src/logic_expression_grammar.py
badd +1 src/loop_grammar.py
badd +1 src/parser_.py
badd +104 src/pico_c_compiler.py
badd +3 src/statement_sequence_grammar.py
badd +307 test/grammar_test.py
badd +1 input.picoc
badd +1 test/gcd.picoc
badd +12 src/code_generator.py
badd +117 src/symbol_table.py
badd +1 output.reti
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
edit src/abstract_syntax_tree.py
argglobal
balt src/arithmetic_expression_grammar.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
542
normal! zo
546
normal! zo
559
normal! zo
565
normal! zo
570
normal! zo
575
normal! zo
576
normal! zo
589
normal! zo
596
normal! zo
604
normal! zo
607
normal! zo
613
normal! zo
618
normal! zo
let s:l = 610 - ((17 * winheight(0) + 17) / 35)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 610
normal! 034|
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
