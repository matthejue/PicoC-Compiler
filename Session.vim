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
badd +19 src/errors.py
badd +16 src/ast_builder.py
badd +12 src/lexer.py
badd +20 src/parser.py
badd +142 src/pico_c_compiler.py
badd +3 term://~/Documents/Studium/pico-c-compiler//119220:/usr/bin/zsh
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//137332:/usr/bin/python
badd +1 .vimspector.json
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//145432:/usr/bin/python
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//149035:/usr/bin/python
badd +1 test.cpp
badd +1 doc/grammer.txt
badd +1 src/arithmetic_expression.py
badd +37 src/abstract_syntax_tree.py
badd +10 src/grammer.py
badd +106 src/arithmetic_expression_grammer.py
badd +21 src/function_grammer.py
badd +7 Makefile
badd +1 term://~/Documents/Studium/pico-c-compiler//353172:/usr/bin/python
badd +7 term://~/Documents/Studium/pico-c-compiler//353362:/usr/bin/python
badd +5 term://~/Documents/Studium/pico-c-compiler//357695:/usr/bin/python
badd +14 term://~/Documents/Studium/pico-c-compiler//391793:/usr/bin/python
badd +3 term://~/Documents/Studium/pico-c-compiler//429467:/usr/bin/python
badd +13 term://~/Documents/Studium/pico-c-compiler//429880:/usr/bin/python
badd +3 term://~/Documents/Studium/pico-c-compiler//436259:/usr/bin/python
badd +0 term://~/Documents/Studium/pico-c-compiler//437955:/usr/bin/python
badd +14 term://~/Documents/Studium/pico-c-compiler//439231:/usr/bin/python
badd +14 term://~/Documents/Studium/pico-c-compiler//453191:/usr/bin/python
badd +14 term://~/Documents/Studium/pico-c-compiler//459114:/usr/bin/python
badd +14 term://~/Documents/Studium/pico-c-compiler//470832:/usr/bin/python
argglobal
%argdel
$argadd src/errors.py
$argadd src/ast_builder.py
$argadd src/lexer.py
$argadd src/parser.py
$argadd src/pico_c_compiler.py
set stal=2
tabnew
tabnew
tabnew
tabnew
tabnew
tabnew
tabnew
tabrewind
edit src/pico_c_compiler.py
argglobal
5argu
balt src/parser.py
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
let s:l = 86 - ((44 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 86
normal! 018|
tabnext
edit src/errors.py
argglobal
1argu
balt src/pico_c_compiler.py
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
let s:l = 19 - ((18 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 19
normal! 020|
tabnext
edit src/lexer.py
argglobal
if bufexists("src/lexer.py") | buffer src/lexer.py | else | edit src/lexer.py | endif
if &buftype ==# 'terminal'
  silent file src/lexer.py
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
let s:l = 6 - ((5 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 6
normal! 09|
tabnext
edit src/parser.py
argglobal
4argu
balt src/lexer.py
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
let s:l = 38 - ((16 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 38
normal! 014|
tabnext
edit src/grammer.py
argglobal
1argu
if bufexists("src/grammer.py") | buffer src/grammer.py | else | edit src/grammer.py | endif
if &buftype ==# 'terminal'
  silent file src/grammer.py
endif
balt src/parser.py
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
let s:l = 10 - ((9 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 10
normal! 017|
tabnext
edit src/arithmetic_expression_grammer.py
let s:save_splitbelow = &splitbelow
let s:save_splitright = &splitright
set splitbelow splitright
wincmd _ | wincmd |
vsplit
1wincmd h
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
exe 'vert 1resize ' . ((&columns * 92 + 95) / 190)
exe 'vert 2resize ' . ((&columns * 97 + 95) / 190)
argglobal
if bufexists("src/arithmetic_expression_grammer.py") | buffer src/arithmetic_expression_grammer.py | else | edit src/arithmetic_expression_grammer.py | endif
if &buftype ==# 'terminal'
  silent file src/arithmetic_expression_grammer.py
endif
balt src/parser.py
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
let s:l = 106 - ((32 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 106
normal! 035|
wincmd w
argglobal
if bufexists("doc/grammer.txt") | buffer doc/grammer.txt | else | edit doc/grammer.txt | endif
if &buftype ==# 'terminal'
  silent file doc/grammer.txt
endif
balt src/arithmetic_expression.py
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
let s:l = 53 - ((4 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 53
normal! 0
wincmd w
exe 'vert 1resize ' . ((&columns * 92 + 95) / 190)
exe 'vert 2resize ' . ((&columns * 97 + 95) / 190)
if exists(':tcd') == 2 | tcd ~/Documents/Studium/pico-c-compiler | endif
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/ast_builder.py
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/src/ast_builder.py") | buffer ~/Documents/Studium/pico-c-compiler/src/ast_builder.py | else | edit ~/Documents/Studium/pico-c-compiler/src/ast_builder.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/ast_builder.py
endif
balt ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py
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
let s:l = 18 - ((14 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 18
normal! 037|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
argglobal
5argu
if bufexists("~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py") | buffer ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py | else | edit ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
endif
balt ~/Documents/Studium/pico-c-compiler/src/pico_c_compiler.py
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
let s:l = 35 - ((28 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 35
normal! 09|
if exists(':tcd') == 2 | tcd ~/Documents/Studium/pico-c-compiler | endif
tabnext 6
set stal=1
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
