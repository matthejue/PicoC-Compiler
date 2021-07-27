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
badd +25 ~/Documents/Studium/pico-c-compiler/src/ast_builder.py
badd +74 ~/Documents/Studium/pico-c-compiler/src/lexer.py
badd +2 ~/Documents/Studium/pico-c-compiler/src/parser.py
badd +5 ~/Documents/Studium/pico-c-compiler/src/pico_c_compiler.py
badd +3 term://~/Documents/Studium/pico-c-compiler//119220:/usr/bin/zsh
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//137332:/usr/bin/python
badd +20 ~/Documents/Studium/pico-c-compiler/.vimspector.json
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//145432:/usr/bin/python
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//149035:/usr/bin/python
badd +1 ~/Documents/Studium/pico-c-compiler/test.cpp
badd +54 ~/Documents/Studium/pico-c-compiler/doc/grammer.txt
badd +1 ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/grammer.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py
badd +20 ~/Documents/Studium/pico-c-compiler/src/function_grammer.py
badd +10 ~/Documents/Studium/pico-c-compiler/Makefile
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
badd +13 term://~/Documents/Studium/pico-c-compiler//238302:/usr/bin/python
badd +3 term://~/Documents/Studium/pico-c-compiler//243064:/usr/bin/python
badd +1 term://~/Documents/Studium/pico-c-compiler//243786:/usr/bin/python
badd +1 ~/Documents/Studium/pico-c-compiler/src/input.picoc
badd +1 term://~/Documents/Studium/pico-c-compiler//246320:/usr/bin/python
badd +45 term://~/Documents/Studium/pico-c-compiler//248711:/usr/bin/zsh
badd +0 ~/Documents/Studium/pico-c-compiler/src/globals.py
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
let s:l = 149 - ((44 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 149
normal! 019|
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
let s:l = 20 - ((19 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 20
normal! 041|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/globals.py
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/src/globals.py") | buffer ~/Documents/Studium/pico-c-compiler/src/globals.py | else | edit ~/Documents/Studium/pico-c-compiler/src/globals.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/globals.py
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
let s:l = 1 - ((0 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 09|
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
let s:l = 169 - ((44 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 169
normal! 047|
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
let s:l = 8 - ((7 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 8
normal! 010|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammer.py
argglobal
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
let s:l = 94 - ((27 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 94
normal! 0
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
let s:l = 1 - ((0 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 07|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/ast_builder.py
argglobal
1argu
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
let s:l = 19 - ((18 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 19
normal! 04|
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
let s:l = 58 - ((30 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 58
normal! 020|
tabnext 4
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
