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
edit ~/Documents/Studium/pico_c_compiler/__Tagbar__.1
let s:save_splitbelow = &splitbelow
let s:save_splitright = &splitright
set splitbelow splitright
wincmd _ | wincmd |
vsplit
wincmd _ | wincmd |
vsplit
2wincmd h
wincmd w
wincmd w
let &splitbelow = s:save_splitbelow
let &splitright = s:save_splitright
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe 'vert 1resize ' . ((&columns * 30 + 86) / 173)
exe 'vert 2resize ' . ((&columns * 111 + 86) / 173)
exe 'vert 3resize ' . ((&columns * 30 + 86) / 173)
argglobal
balt ~/Documents/Studium/pico_c_compiler/error_handler.py
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
let s:l = 14 - ((13 * winheight(0) + 18) / 37)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 14
normal! 0
wincmd w
argglobal
if bufexists("error_handler.py") | buffer error_handler.py | else | edit error_handler.py | endif
if &buftype ==# 'terminal'
  silent file error_handler.py
endif
balt ~/Documents/Studium/pico_c_compiler/lexer.py
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
let s:l = 179 - ((24 * winheight(0) + 18) / 37)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 179
normal! 022|
wincmd w
argglobal
if bufexists("~/Documents/Studium/pico_c_compiler/NERD_tree_10") | buffer ~/Documents/Studium/pico_c_compiler/NERD_tree_10 | else | edit ~/Documents/Studium/pico_c_compiler/NERD_tree_10 | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico_c_compiler/NERD_tree_10
endif
balt error_handler.py
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
let s:l = 1 - ((0 * winheight(0) + 18) / 37)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 0
wincmd w
2wincmd w
exe 'vert 1resize ' . ((&columns * 30 + 86) / 173)
exe 'vert 2resize ' . ((&columns * 111 + 86) / 173)
exe 'vert 3resize ' . ((&columns * 30 + 86) / 173)
if exists(':tcd') == 2 | tcd ~/Documents/Studium/pico_c_compiler | endif
tabnext 1
badd +179 ~/Documents/Studium/pico_c_compiler/src/error_handler.py
badd +0 ~/Documents/Studium/pico_c_compiler/__Tagbar__.1
badd +0 ~/Documents/Studium/pico_c_compiler/error_handler.py
badd +0 ~/Documents/Studium/pico_c_compiler/lexer.py
badd +0 ~/Documents/Studium/pico_c_compiler/NERD_tree_10
badd +63 ~/Documents/Studium/pico_c_compiler/src/lexer.py
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0 && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxcsAoOaFTt
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
