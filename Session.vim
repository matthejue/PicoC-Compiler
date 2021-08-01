let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/Documents/Studium/pico-c-compiler
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +9 src/abstract_syntax_tree.py
badd +1 src/arithmetic_expression_grammar.py
badd +1 src/assignment_allocation_grammar.py
badd +5 src/ast_builder.py
badd +1 src/errors.py
badd +1 src/function_grammar.py
badd +1 src/globals.py
badd +1 src/input.picoc
badd +201 src/lexer.py
badd +1 src/output.reti
badd +42 src/parser.py
badd +1 src/pico_c_compiler.py
badd +1 src/statement_sequence_grammar.py
badd +21 src/logic_expression_grammar.py
badd +2 src/conditional_grammar.py
argglobal
%argdel
$argadd src/abstract_syntax_tree.py
$argadd src/arithmetic_expression_grammar.py
$argadd src/assignment_allocation_grammar.py
$argadd src/ast_builder.py
$argadd src/errors.py
$argadd src/function_grammar.py
$argadd src/globals.py
$argadd src/input.picoc
$argadd src/lexer.py
$argadd src/output.reti
$argadd src/parser.py
$argadd src/pico_c_compiler.py
$argadd src/statement_sequence_grammar.py
edit src/lexer.py
argglobal
if bufexists("src/lexer.py") | buffer src/lexer.py | else | edit src/lexer.py | endif
if &buftype ==# 'terminal'
  silent file src/lexer.py
endif
balt src/abstract_syntax_tree.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
48
normal! zo
76
normal! zo
76
normal! zo
76
normal! zo
83
normal! zo
185
normal! zo
185
normal! zo
186
normal! zo
196
normal! zo
196
normal! zo
196
normal! zo
205
normal! zo
let s:l = 206 - ((89 * winheight(0) + 23) / 46)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 206
normal! 035|
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0&& getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=A
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
