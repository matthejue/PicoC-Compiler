let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/Documents/Studium/pico_c_compiler/test
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +5 ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
badd +10 ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
badd +3 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_grammar.py
badd +7 ~/Documents/Studium/pico_c_compiler/src/ast_builder.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/conditional_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/errors.py
badd +3 ~/Documents/Studium/pico_c_compiler/src/function_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/globals.py
badd +9 ~/Documents/Studium/pico_c_compiler/src/grammar.py
badd +5 ~/Documents/Studium/pico_c_compiler/src/lexer.py
badd +15 ~/Documents/Studium/pico_c_compiler/src/logic_expression_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/parser.py
badd +33 ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
badd +5 ~/Documents/Studium/pico_c_compiler/.vimspector.json
badd +11 ~/Documents/Studium/pico_c_compiler/Makefile
badd +1 ~/Documents/Studium/pico_c_compiler/pico_c_compiler.py
badd +1 ~/Documents/Studium/pico_c_compiler/input.picoc
argglobal
%argdel
$argadd ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
$argadd ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/ast_builder.py
$argadd ~/Documents/Studium/pico_c_compiler/src/conditional_grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/errors.py
$argadd ~/Documents/Studium/pico_c_compiler/src/function_grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/globals.py
$argadd ~/Documents/Studium/pico_c_compiler/src/grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/grammar_2.py
$argadd ~/Documents/Studium/pico_c_compiler/src/input.picoc
$argadd ~/Documents/Studium/pico_c_compiler/src/lexer.py
$argadd ~/Documents/Studium/pico_c_compiler/src/logic_expression_grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/output.reti
$argadd ~/Documents/Studium/pico_c_compiler/src/parser.py
$argadd ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py
$argadd ~/Documents/Studium/pico_c_compiler/src/statement_sequence_grammar.py
edit ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
argglobal
if bufexists("~/Documents/Studium/pico_c_compiler/test/grammar_test.py") | buffer ~/Documents/Studium/pico_c_compiler/test/grammar_test.py | else | edit ~/Documents/Studium/pico_c_compiler/test/grammar_test.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
endif
balt ~/Documents/Studium/pico_c_compiler/src/lexer.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
35
normal! zo
36
normal! zo
37
normal! zo
41
normal! zo
42
normal! zo
let s:l = 33 - ((26 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 33
normal! 030|
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
