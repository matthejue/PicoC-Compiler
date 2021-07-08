let SessionLoad = 1
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/Documents/Studium/pico-c-compiler
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +7 ~/Documents/Studium/pico-c-compiler/src/errors.py
badd +34 ~/Documents/Studium/pico-c-compiler/src/ast_builder.py
badd +91 ~/Documents/Studium/pico-c-compiler/src/lexer.py
badd +50 ~/Documents/Studium/pico-c-compiler/src/parser.py
badd +131 ~/Documents/Studium/pico-c-compiler/src/pico_c_compiler.py
badd +1 term://.//303417:/usr/bin/zsh
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//137332:/usr/bin/python
badd +17 ~/Documents/Studium/pico-c-compiler/.vimspector.json
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//145432:/usr/bin/python
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//149035:/usr/bin/python
badd +1 ~/Documents/Studium/pico-c-compiler/test.cpp
badd +1 ~/Documents/Studium/pico-c-compiler/doc/grammer.txt
badd +9 ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
argglobal
%argdel
$argadd ~/Documents/Studium/pico-c-compiler/src/errors.py
$argadd ~/Documents/Studium/pico-c-compiler/src/ast_builder.py
$argadd ~/Documents/Studium/pico-c-compiler/src/lexer.py
$argadd ~/Documents/Studium/pico-c-compiler/src/parser.py
$argadd ~/Documents/Studium/pico-c-compiler/src/pico_c_compiler.py
set stal=2
edit ~/Documents/Studium/pico-c-compiler/src/pico_c_compiler.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
5argu
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 158 - ((44 * winheight(0) + 23) / 47)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
158
normal! 0
tabedit ~/Documents/Studium/pico-c-compiler/src/errors.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
1argu
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 9 - ((8 * winheight(0) + 23) / 47)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
9
normal! 034|
tabedit ~/Documents/Studium/pico-c-compiler/src/lexer.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/src/lexer.py") | buffer ~/Documents/Studium/pico-c-compiler/src/lexer.py | else | edit ~/Documents/Studium/pico-c-compiler/src/lexer.py | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 23 - ((22 * winheight(0) + 23) / 47)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
23
normal! 018|
tabedit ~/Documents/Studium/pico-c-compiler/src/parser.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
4argu
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 4 - ((3 * winheight(0) + 23) / 47)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
4
normal! 03|
tabedit ~/Documents/Studium/pico-c-compiler/src/ast_builder.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
2argu
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 11 - ((10 * winheight(0) + 23) / 47)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
11
normal! 0
tabedit ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression.py
set splitbelow splitright
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd w
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe 'vert 1resize ' . ((&columns * 94 + 105) / 211)
exe 'vert 2resize ' . ((&columns * 116 + 105) / 211)
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/src/arithmetic_expression.py") | buffer ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression.py | else | edit ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression.py | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 9 - ((8 * winheight(0) + 23) / 47)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
9
normal! 039|
wincmd w
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/doc/grammer.txt") | buffer ~/Documents/Studium/pico-c-compiler/doc/grammer.txt | else | edit ~/Documents/Studium/pico-c-compiler/doc/grammer.txt | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 37 - ((36 * winheight(0) + 23) / 47)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
37
normal! 018|
wincmd w
exe 'vert 1resize ' . ((&columns * 94 + 105) / 211)
exe 'vert 2resize ' . ((&columns * 116 + 105) / 211)
tabedit ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
5argu
if bufexists("~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py") | buffer ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py | else | edit ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 36 - ((35 * winheight(0) + 23) / 47)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
36
normal! 026|
tabnew
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
if bufexists("term://.//303417:/usr/bin/zsh") | buffer term://.//303417:/usr/bin/zsh | else | edit term://.//303417:/usr/bin/zsh | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 47 - ((46 * winheight(0) + 23) / 47)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
47
normal! 0
tabnext 5
set stal=1
if exists('s:wipebuf') && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 winminheight=1 winminwidth=1 shortmess=filnxtToOFc
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
