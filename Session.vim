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
$argadd pico_c_compiler.py
edit assignment_allocation_nodes.py
argglobal
balt symbol_table.py
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
let s:l = 112 - ((29 * winheight(0) + 19) / 39)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 112
normal! 023|
if exists(':tcd') == 2 | tcd ~/Documents/Studium/pico_c_compiler | endif
tabnext 1
badd +235 ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py
badd +115 ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
badd +73 ~/Documents/Studium/pico_c_compiler/src/arithmetic_nodes.py
badd +110 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_nodes.py
badd +73 ~/Documents/Studium/pico_c_compiler/src/error_handler.py
badd +58 ~/Documents/Studium/pico_c_compiler/src/errors.py
badd +7 ~/Documents/Studium/pico_c_compiler/src/global_vars.py
badd +7 ~/Documents/Studium/pico_c_compiler/src/symbol_table.py
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
