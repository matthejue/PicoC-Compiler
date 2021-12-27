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
edit lexer.py
argglobal
balt lexer_2.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal nofen
silent! normal! zE
let &fdl = &fdl
let s:l = 12 - ((11 * winheight(0) + 19) / 38)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 12
normal! 027|
if exists(':tcd') == 2 | tcd ~/Documents/Studium/pico_c_compiler | endif
tabnext 1
badd +69 ~/Documents/Studium/pico_c_compiler/src/parser_.py
badd +28 ~/Documents/Studium/pico_c_compiler/src/ast_builder.py
badd +31 ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
badd +18 ~/Documents/Studium/pico_c_compiler/src/arithmetic_nodes.py
badd +12 ~/Documents/Studium/pico_c_compiler/src/lexer.py
badd +11 ~/Documents/Studium/pico_c_compiler/src/lexer_2.py
badd +136 ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
badd +3 ~/Documents/Studium/pico_c_compiler/src/if_else_nodes.py
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
