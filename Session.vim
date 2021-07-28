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
badd +1 src/abstract_syntax_tree.py
badd +1 src/arithmetic_expression_grammar.py
badd +1 src/assignment_allocation_grammar.py
badd +1 src/ast_builder.py
badd +1 src/errors.py
badd +1 src/function_grammar.py
badd +1 src/globals.py
badd +1 src/input.picoc
badd +1 src/lexer.py
badd +1 src/output.reti
badd +1 src/parser.py
badd +1 src/pico_c_compiler.py
badd +1 src/statement_sequence_grammar.py
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
edit src/ast_builder.py
argglobal
if bufexists("src/ast_builder.py") | buffer src/ast_builder.py | else | edit src/ast_builder.py | endif
if &buftype ==# 'terminal'
  silent file src/ast_builder.py
endif
balt src/errors.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 1 - ((0 * winheight(0) + 23) / 46)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 0
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0&& getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=AI
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
