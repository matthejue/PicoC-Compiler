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
$argadd assignment_allocation_grammar.py
edit dummy_nodes.py
argglobal
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
let s:l = 10 - ((9 * winheight(0) + 19) / 39)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 10
normal! 0
if exists(':tcd') == 2 | tcd ~/Documents/Studium/pico_c_compiler | endif
tabnext 1
badd +68 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_grammar.py
badd +10 ~/Documents/Studium/pico_c_compiler/src/dummy_nodes.py
badd +22 ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
badd +77 ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
badd +117 ~/Documents/Studium/pico_c_compiler/src/arithmetic_nodes.py
badd +6 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_nodes.py
badd +19 ~/Documents/Studium/pico_c_compiler/src/ast_builder.py
badd +45 ~/Documents/Studium/pico_c_compiler/src/errors.py
badd +197 ~/Documents/Studium/pico_c_compiler/src/lexer.py
badd +58 ~/Documents/Studium/pico_c_compiler/src/parser_.py
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
