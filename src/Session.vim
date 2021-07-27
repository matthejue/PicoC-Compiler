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
badd +19 ~/Documents/Studium/pico-c-compiler/src/errors.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/ast_builder.py
badd +18 ~/Documents/Studium/pico-c-compiler/src/lexer.py
badd +68 ~/Documents/Studium/pico-c-compiler/src/parser.py
badd +136 ~/Documents/Studium/pico-c-compiler/src/pico_c_compiler.py
badd +3 term://~/Documents/Studium/pico-c-compiler//119220:/usr/bin/zsh
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//137332:/usr/bin/python
badd +1 ~/Documents/Studium/pico-c-compiler/.vimspector.json
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//145432:/usr/bin/python
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//149035:/usr/bin/python
badd +1 ~/Documents/Studium/pico-c-compiler/test.cpp
badd +1 ~/Documents/Studium/pico-c-compiler/doc/grammer.txt
badd +1 ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression.py
badd +48 ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/grammar.py
badd +38 ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py
badd +21 ~/Documents/Studium/pico-c-compiler/src/function_grammer.py
badd +7 ~/Documents/Studium/pico-c-compiler/Makefile
badd +1 term://~/Documents/Studium/pico-c-compiler//353172:/usr/bin/python
badd +7 term://~/Documents/Studium/pico-c-compiler//353362:/usr/bin/python
badd +5 term://~/Documents/Studium/pico-c-compiler//357695:/usr/bin/python
badd +14 term://~/Documents/Studium/pico-c-compiler//391793:/usr/bin/python
badd +3 term://~/Documents/Studium/pico-c-compiler//429467:/usr/bin/python
badd +13 term://~/Documents/Studium/pico-c-compiler//429880:/usr/bin/python
badd +3 term://~/Documents/Studium/pico-c-compiler//436259:/usr/bin/python
badd +1 term://~/Documents/Studium/pico-c-compiler//437955:/usr/bin/python
badd +14 term://~/Documents/Studium/pico-c-compiler//439231:/usr/bin/python
badd +14 term://~/Documents/Studium/pico-c-compiler//453191:/usr/bin/python
badd +14 term://~/Documents/Studium/pico-c-compiler//459114:/usr/bin/python
badd +14 term://~/Documents/Studium/pico-c-compiler//470832:/usr/bin/python
badd +0 ~/Documents/Studium/pico-c-compiler/globals.py
badd +0 term://~/Documents/Studium/pico-c-compiler//209025:/usr/bin/python
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
tabnew
tabnew
tabrewind
edit ~/Documents/Studium/pico-c-compiler/src/pico_c_compiler.py
argglobal
5argu
balt ~/Documents/Studium/pico-c-compiler/src/parser.py
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
let s:l = 108 - ((5 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 108
normal! 09|
tabnext
edit ~/Documents/Studium/pico-c-compiler/globals.py
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/globals.py") | buffer ~/Documents/Studium/pico-c-compiler/globals.py | else | edit ~/Documents/Studium/pico-c-compiler/globals.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/globals.py
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
let s:l = 1 - ((0 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 025|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/errors.py
argglobal
1argu
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
let s:l = 18 - ((17 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 18
normal! 034|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/lexer.py
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/src/lexer.py") | buffer ~/Documents/Studium/pico-c-compiler/src/lexer.py | else | edit ~/Documents/Studium/pico-c-compiler/src/lexer.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/lexer.py
endif
balt ~/Documents/Studium/pico-c-compiler/src/errors.py
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
let s:l = 18 - ((11 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 18
normal! 030|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/parser.py
argglobal
4argu
balt ~/Documents/Studium/pico-c-compiler/src/lexer.py
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
let s:l = 69 - ((41 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 69
normal! 011|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py
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
1argu
if bufexists("~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py") | buffer ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py | else | edit ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py
endif
balt ~/Documents/Studium/pico-c-compiler/src/parser.py
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
let s:l = 22 - ((0 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 22
normal! 012|
wincmd w
argglobal
1argu
if bufexists("~/Documents/Studium/pico-c-compiler/doc/grammer.txt") | buffer ~/Documents/Studium/pico-c-compiler/doc/grammer.txt | else | edit ~/Documents/Studium/pico-c-compiler/doc/grammer.txt | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/doc/grammer.txt
endif
balt ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression.py
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
let s:l = 1 - ((0 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 09|
wincmd w
exe 'vert 1resize ' . ((&columns * 92 + 95) / 190)
exe 'vert 2resize ' . ((&columns * 97 + 95) / 190)
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/function_grammer.py
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/src/function_grammer.py") | buffer ~/Documents/Studium/pico-c-compiler/src/function_grammer.py | else | edit ~/Documents/Studium/pico-c-compiler/src/function_grammer.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/function_grammer.py
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
let s:l = 21 - ((20 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 21
normal! 04|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/ast_builder.py
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/src/ast_builder.py") | buffer ~/Documents/Studium/pico-c-compiler/src/ast_builder.py | else | edit ~/Documents/Studium/pico-c-compiler/src/ast_builder.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/ast_builder.py
endif
balt ~/Documents/Studium/pico-c-compiler/src/function_grammer.py
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
let s:l = 18 - ((17 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 18
normal! 08|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe '2resize ' . ((&lines * 27 + 24) / 49)
exe 'vert 2resize ' . ((&columns * 114 + 95) / 190)
exe '3resize ' . ((&lines * 25 + 24) / 49)
exe 'vert 3resize ' . ((&columns * 112 + 95) / 190)
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
let s:l = 48 - ((20 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 48
normal! 0
wincmd w
argglobal
5argu
enew
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
wincmd w
argglobal
5argu
if bufexists("term://~/Documents/Studium/pico-c-compiler//138720:/usr/bin/zsh") | buffer term://~/Documents/Studium/pico-c-compiler//138720:/usr/bin/zsh | else | edit term://~/Documents/Studium/pico-c-compiler//138720:/usr/bin/zsh | endif
if &buftype ==# 'terminal'
  silent file term://~/Documents/Studium/pico-c-compiler//138720:/usr/bin/zsh
endif
balt ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 107 - ((24 * winheight(0) + 12) / 25)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 107
normal! 08|
wincmd w
3wincmd w
exe '2resize ' . ((&lines * 27 + 24) / 49)
exe 'vert 2resize ' . ((&columns * 114 + 95) / 190)
exe '3resize ' . ((&lines * 25 + 24) / 49)
exe 'vert 3resize ' . ((&columns * 112 + 95) / 190)
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py
let s:save_splitbelow = &splitbelow
let s:save_splitright = &splitright
set splitbelow splitright
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd _ | wincmd |
split
wincmd _ | wincmd |
split
2wincmd k
wincmd w
wincmd w
wincmd w
wincmd _ | wincmd |
split
wincmd _ | wincmd |
split
2wincmd k
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
exe '1resize ' . ((&lines * 15 + 24) / 49)
exe 'vert 1resize ' . ((&columns * 91 + 95) / 190)
exe '2resize ' . ((&lines * 13 + 24) / 49)
exe 'vert 2resize ' . ((&columns * 91 + 95) / 190)
exe '3resize ' . ((&lines * 15 + 24) / 49)
exe 'vert 3resize ' . ((&columns * 91 + 95) / 190)
exe '4resize ' . ((&lines * 19 + 24) / 49)
exe 'vert 4resize ' . ((&columns * 98 + 95) / 190)
exe '5resize ' . ((&lines * 14 + 24) / 49)
exe 'vert 5resize ' . ((&columns * 98 + 95) / 190)
exe '6resize ' . ((&lines * 10 + 24) / 49)
exe 'vert 6resize ' . ((&columns * 98 + 95) / 190)
argglobal
enew
file ~/Documents/Studium/pico-c-compiler/vimspector.Variables
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
wincmd w
argglobal
enew
file ~/Documents/Studium/pico-c-compiler/vimspector.Watches
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
wincmd w
argglobal
enew
file ~/Documents/Studium/pico-c-compiler/vimspector.StackTrace
balt ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
wincmd w
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py") | buffer ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py | else | edit ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py
endif
balt ~/Documents/Studium/pico-c-compiler/src/function_grammer.py
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
let s:l = 22 - ((0 * winheight(0) + 9) / 19)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 22
normal! 0
wincmd w
argglobal
if bufexists("term://~/Documents/Studium/pico-c-compiler//209025:/usr/bin/python") | buffer term://~/Documents/Studium/pico-c-compiler//209025:/usr/bin/python | else | edit term://~/Documents/Studium/pico-c-compiler//209025:/usr/bin/python | endif
if &buftype ==# 'terminal'
  silent file term://~/Documents/Studium/pico-c-compiler//209025:/usr/bin/python
endif
balt ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 14 - ((13 * winheight(0) + 7) / 14)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 14
normal! 0
wincmd w
argglobal
enew
file ~/Documents/Studium/pico-c-compiler/vimspector.Console
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
wincmd w
exe '1resize ' . ((&lines * 15 + 24) / 49)
exe 'vert 1resize ' . ((&columns * 91 + 95) / 190)
exe '2resize ' . ((&lines * 13 + 24) / 49)
exe 'vert 2resize ' . ((&columns * 91 + 95) / 190)
exe '3resize ' . ((&lines * 15 + 24) / 49)
exe 'vert 3resize ' . ((&columns * 91 + 95) / 190)
exe '4resize ' . ((&lines * 19 + 24) / 49)
exe 'vert 4resize ' . ((&columns * 98 + 95) / 190)
exe '5resize ' . ((&lines * 14 + 24) / 49)
exe 'vert 5resize ' . ((&columns * 98 + 95) / 190)
exe '6resize ' . ((&lines * 10 + 24) / 49)
exe 'vert 6resize ' . ((&columns * 98 + 95) / 190)
tabnext 9
set stal=1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0&& getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=A
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
