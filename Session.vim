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
badd +3 src/abstract_syntax_tree.py
badd +7 src/arithmetic_expression_grammar.py
badd +1 src/assignment_allocation_grammar.py
badd +1 src/ast_builder.py
badd +1 src/conditional_grammar.py
badd +1 src/errors.py
badd +1 src/function_grammar.py
badd +1 src/globals.py
badd +1 src/grammar.py
badd +1 src/grammar_2.py
badd +1 src/input.picoc
badd +1 src/lexer.py
badd +1 src/logic_expression_grammar.py
badd +1 src/output.reti
badd +1 src/parser.py
badd +1 src/pico_c_compiler.py
badd +1 src/statement_sequence_grammar.py
badd +23 test/grammar_test.py
argglobal
%argdel
$argadd src/abstract_syntax_tree.py
$argadd src/arithmetic_expression_grammar.py
$argadd src/assignment_allocation_grammar.py
$argadd src/ast_builder.py
$argadd src/conditional_grammar.py
$argadd src/errors.py
$argadd src/function_grammar.py
$argadd src/globals.py
$argadd src/grammar.py
$argadd src/grammar_2.py
$argadd src/input.picoc
$argadd src/lexer.py
$argadd src/logic_expression_grammar.py
$argadd src/output.reti
$argadd src/parser.py
$argadd src/pico_c_compiler.py
$argadd src/statement_sequence_grammar.py
edit src/arithmetic_expression_grammar.py
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe '2resize ' . ((&lines * 17 + 23) / 47)
exe 'vert 2resize ' . ((&columns * 1 + 47) / 94)
argglobal
if bufexists("src/arithmetic_expression_grammar.py") | buffer src/arithmetic_expression_grammar.py | else | edit src/arithmetic_expression_grammar.py | endif
if &buftype ==# 'terminal'
  silent file src/arithmetic_expression_grammar.py
endif
balt test/grammar_test.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
8
normal! zo
15
normal! zo
15
normal! zo
15
normal! zo
24
normal! zo
24
normal! zo
24
normal! zo
30
normal! zo
36
normal! zo
45
normal! zo
45
normal! zo
45
normal! zo
56
normal! zo
65
normal! zo
65
normal! zo
65
normal! zo
87
normal! zo
87
normal! zo
87
normal! zo
98
normal! zo
98
normal! zo
98
normal! zo
104
normal! zo
108
normal! zo
let s:l = 7 - ((6 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 7
normal! 08|
wincmd w
argglobal
enew
balt src/arithmetic_expression_grammar.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
wincmd w
exe '2resize ' . ((&lines * 17 + 23) / 47)
exe 'vert 2resize ' . ((&columns * 1 + 47) / 94)
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
