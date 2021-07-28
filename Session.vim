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
badd +34 src/ast_builder.py
badd +153 src/lexer.py
badd +45 src/parser.py
badd +120 src/pico_c_compiler.py
badd +3 term://~/Documents/Studium/pico-c-compiler//119220:/usr/bin/zsh
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//137332:/usr/bin/python
badd +20 .vimspector.json
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//145432:/usr/bin/python
badd +14 term:///home/areo/Documents/Studium/pico-c-compiler//149035:/usr/bin/python
badd +1 test.cpp
badd +61 doc/grammer.txt
badd +1 src/arithmetic_expression.py
badd +1 src/abstract_syntax_tree.py
badd +1 src/grammer.py
badd +1 src/arithmetic_expression_grammer.py
badd +1 src/function_grammer.py
badd +10 Makefile
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
badd +1 src/input.picoc
badd +1 term://~/Documents/Studium/pico-c-compiler//246320:/usr/bin/python
badd +45 term://~/Documents/Studium/pico-c-compiler//248711:/usr/bin/zsh
badd +2 src/globals.py
badd +1 assignment_expression_grammer.py
badd +1 statement_expression_grammer.py
badd +1 src/statement_sequence_grammar.py
badd +13 src/arithmetic_expression_grammar.py
badd +1 src/assignment_grammar.py
badd +23 src/function_grammar.py
badd +1 term://~/Documents/Studium/pico-c-compiler//163116:/usr/bin/python
badd +1 term://~/Documents/Studium/pico-c-compiler//168044:/usr/bin/python
badd +1 term://~/Documents/Studium/pico-c-compiler//177776:/usr/bin/python
badd +34 src/assignment_allocation_grammar.py
badd +0 term://~/Documents/Studium/pico-c-compiler//68352:/usr/bin/python
badd +0 term://~/Documents/Studium/pico-c-compiler//70358:/usr/bin/python
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
let s:l = 98 - ((32 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 98
normal! 07|
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
let s:l = 15 - ((14 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 15
normal! 025|
tabnext
edit src/globals.py
argglobal
if bufexists("src/globals.py") | buffer src/globals.py | else | edit src/globals.py | endif
if &buftype ==# 'terminal'
  silent file src/globals.py
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
let s:l = 2 - ((1 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 2
normal! 011|
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
let s:l = 128 - ((30 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 128
normal! 016|
if exists(':tcd') == 2 | tcd ~/Documents/Studium/pico-c-compiler | endif
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
let s:l = 45 - ((44 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 45
normal! 03|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammar.py
argglobal
1argu
if bufexists("~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammar.py") | buffer ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammar.py | else | edit ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammar.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammar.py
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
let s:l = 80 - ((38 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 80
normal! 023|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/assignment_allocation_grammar.py
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
exe 'vert 1resize ' . ((&columns * 94 + 95) / 190)
exe 'vert 2resize ' . ((&columns * 95 + 95) / 190)
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/src/assignment_allocation_grammar.py") | buffer ~/Documents/Studium/pico-c-compiler/src/assignment_allocation_grammar.py | else | edit ~/Documents/Studium/pico-c-compiler/src/assignment_allocation_grammar.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/assignment_allocation_grammar.py
endif
balt ~/Documents/Studium/pico-c-compiler/src/assignment_grammar.py
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
let s:l = 34 - ((24 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 34
normal! 014|
wincmd w
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/doc/grammer.txt") | buffer ~/Documents/Studium/pico-c-compiler/doc/grammer.txt | else | edit ~/Documents/Studium/pico-c-compiler/doc/grammer.txt | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/doc/grammer.txt
endif
balt ~/Documents/Studium/pico-c-compiler/src/assignment_grammar.py
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
let s:l = 45 - ((44 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 45
normal! 07|
wincmd w
exe 'vert 1resize ' . ((&columns * 94 + 95) / 190)
exe 'vert 2resize ' . ((&columns * 95 + 95) / 190)
if exists(':tcd') == 2 | tcd ~/Documents/Studium/pico-c-compiler | endif
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/statement_sequence_grammar.py
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/src/statement_sequence_grammar.py") | buffer ~/Documents/Studium/pico-c-compiler/src/statement_sequence_grammar.py | else | edit ~/Documents/Studium/pico-c-compiler/src/statement_sequence_grammar.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/statement_sequence_grammar.py
endif
balt ~/Documents/Studium/pico-c-compiler/assignment_expression_grammer.py
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
normal! 0
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/function_grammar.py
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/src/function_grammar.py") | buffer ~/Documents/Studium/pico-c-compiler/src/function_grammar.py | else | edit ~/Documents/Studium/pico-c-compiler/src/function_grammar.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/function_grammar.py
endif
balt ~/Documents/Studium/pico-c-compiler/src/statement_sequence_grammar.py
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
normal! 0
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
let s:l = 24 - ((23 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 24
normal! 023|
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
let s:l = 48 - ((44 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 48
normal! 04|
tabnext
edit ~/Documents/Studium/pico-c-compiler/src/input.picoc
argglobal
1argu
if bufexists("~/Documents/Studium/pico-c-compiler/src/input.picoc") | buffer ~/Documents/Studium/pico-c-compiler/src/input.picoc | else | edit ~/Documents/Studium/pico-c-compiler/src/input.picoc | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/src/input.picoc
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
silent! normal! zE
let &fdl = &fdl
let s:l = 1 - ((0 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 05|
tabnext 7
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
