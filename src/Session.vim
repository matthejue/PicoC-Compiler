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
badd +1 ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/ast_builder.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/conditional_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/errors.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/function_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/globals.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/grammar.py
badd +27 ~/Documents/Studium/pico_c_compiler/src/lexer.py
badd +37 ~/Documents/Studium/pico_c_compiler/src/logic_expression_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/parser_.py
badd +103 ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py
badd +69 ~/Documents/Studium/pico_c_compiler/src/statement_sequence_grammar.py
badd +201 ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/if_else_grammar.py
badd +40 ~/Documents/Studium/pico_c_compiler/src/loop_grammar.py
argglobal
%argdel
$argadd abstract_syntax_tree.py
$argadd arithmetic_expression_grammar.py
$argadd assignment_allocation_grammar.py
$argadd ast_builder.py
$argadd conditional_grammar.py
$argadd errors.py
$argadd function_grammar.py
$argadd globals.py
$argadd grammar.py
$argadd lexer.py
$argadd logic_expression_grammar.py
$argadd parser_.py
$argadd pico_c_compiler.py
$argadd statement_sequence_grammar.py
edit ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe '2resize ' . ((&lines * 14 + 23) / 47)
exe 'vert 2resize ' . ((&columns * 1 + 95) / 191)
argglobal
if bufexists("~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py") | buffer ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py | else | edit ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py
endif
balt ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
11
normal! zo
11
normal! zo
13
normal! zo
15
normal! zo
17
normal! zo
18
normal! zo
20
normal! zo
21
normal! zo
23
normal! zo
24
normal! zo
26
normal! zo
51
normal! zo
51
normal! zo
51
normal! zo
61
normal! zo
61
normal! zo
61
normal! zo
69
normal! zo
81
normal! zo
81
normal! zo
81
normal! zo
87
normal! zo
97
normal! zo
107
normal! zo
122
normal! zo
let s:l = 103 - ((25 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 103
normal! 07|
wincmd w
argglobal
enew
balt ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
wincmd w
exe '2resize ' . ((&lines * 14 + 23) / 47)
exe 'vert 2resize ' . ((&columns * 1 + 95) / 191)
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0&& getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxIAoOaFTt
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
