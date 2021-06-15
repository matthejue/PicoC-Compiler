let SessionLoad = 1
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/Documents/Studium/Pico-C_Compiler
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +54 ~/Documents/Studium/Pico-C_Compiler/lexer.py
badd +1 ~/Documents/Studium/Pico-C_Compiler/main.py
badd +58 ~/Documents/Studium/Pico-C_Compiler/parser.py
badd +117 ~/Documents/Studium/Pico-C_Compiler/pico_c_compiler.py
badd +1 ~/Documents/Studium/Pico-C_Compiler/tokentypes.py
badd +28 ~/Documents/Studium/Pico-C_Compiler/tok.py
badd +10 ~/Documents/Studium/Pico-C_Compiler/grammer.txt
badd +1 ~/Documents/Studium/Pico-C_Compiler/input.picoc
badd +1 ~/Documents/Studium/Pico-C_Compiler/output.reti
badd +1 ~/Documents/Studium/Pico-C_Compiler/_arithmetic_expressions.py
badd +19 term://.//186271:/usr/bin/zsh
badd +21 term://.//2308:/usr/bin/zsh
badd +1 ~/Documents/Studium/Pico-C_Compiler/error_evaluation.py
badd +95 term://.//30731:/usr/bin/zsh
badd +10 term:///home/areo/Documents/Studium/Pico-C_Compiler//43105:/usr/bin/python
badd +2 ~/Documents/Studium/Pico-C_Compiler/.vimspector.json
badd +1 term:///home/areo/Documents/Studium/Pico-C_Compiler//43958:/usr/bin/python
badd +1 ~/Documents/Studium/Pico-C_Compiler/errors.py
badd +1 term:///home/areo/Documents/Studium/Pico-C_Compiler//62413:/usr/bin/python
badd +1 term:///home/areo/Documents/Studium/Pico-C_Compiler//75487:/usr/bin/python
badd +1 term:///home/areo/Documents/Studium/Pico-C_Compiler//81431:/usr/bin/python
badd +43 term://.//213880:/usr/bin/zsh
badd +1 term:///home/areo/Documents/Studium/Pico-C_Compiler//110707:/usr/bin/python
badd +3 term://.//121154:/usr/bin/zsh
badd +1 ~/Documents/Studium/Pico-C_Compiler/test_parser.py
badd +16 ~/Documents/Studium/Pico-C_Compiler/test_errors.py
argglobal
%argdel
$argadd lexer.py
$argadd main.py
$argadd parser.py
$argadd pico_c_compiler.py
$argadd tokentypes.py
$argadd tok.py
set stal=2
edit ~/Documents/Studium/Pico-C_Compiler/pico_c_compiler.py
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
let s:l = 8 - ((7 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
8
normal! 057|
tabedit ~/Documents/Studium/Pico-C_Compiler/errors.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
if bufexists("~/Documents/Studium/Pico-C_Compiler/errors.py") | buffer ~/Documents/Studium/Pico-C_Compiler/errors.py | else | edit ~/Documents/Studium/Pico-C_Compiler/errors.py | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 1 - ((0 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
1
normal! 022|
tabedit ~/Documents/Studium/Pico-C_Compiler/lexer.py
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
let s:l = 47 - ((44 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
47
normal! 012|
tabedit ~/Documents/Studium/Pico-C_Compiler/parser.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
3argu
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 41 - ((7 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
41
normal! 012|
tabedit ~/Documents/Studium/Pico-C_Compiler/_arithmetic_expressions.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
if bufexists("~/Documents/Studium/Pico-C_Compiler/_arithmetic_expressions.py") | buffer ~/Documents/Studium/Pico-C_Compiler/_arithmetic_expressions.py | else | edit ~/Documents/Studium/Pico-C_Compiler/_arithmetic_expressions.py | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 73 - ((44 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
73
normal! 014|
tabedit ~/Documents/Studium/Pico-C_Compiler/tok.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
6argu
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 37 - ((35 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
37
normal! 022|
tabedit ~/Documents/Studium/Pico-C_Compiler/tokentypes.py
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
let s:l = 3 - ((2 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
3
normal! 0
tabedit ~/Documents/Studium/Pico-C_Compiler/grammer.txt
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
if bufexists("~/Documents/Studium/Pico-C_Compiler/grammer.txt") | buffer ~/Documents/Studium/Pico-C_Compiler/grammer.txt | else | edit ~/Documents/Studium/Pico-C_Compiler/grammer.txt | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 19 - ((18 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
19
normal! 018|
tabedit ~/Documents/Studium/Pico-C_Compiler/input.picoc
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
if bufexists("~/Documents/Studium/Pico-C_Compiler/input.picoc") | buffer ~/Documents/Studium/Pico-C_Compiler/input.picoc | else | edit ~/Documents/Studium/Pico-C_Compiler/input.picoc | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 1 - ((0 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
1
normal! 01|
tabedit ~/Documents/Studium/Pico-C_Compiler/output.reti
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
if bufexists("~/Documents/Studium/Pico-C_Compiler/output.reti") | buffer ~/Documents/Studium/Pico-C_Compiler/output.reti | else | edit ~/Documents/Studium/Pico-C_Compiler/output.reti | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 1 - ((0 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
1
normal! 0
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
if bufexists("term://.//213880:/usr/bin/zsh") | buffer term://.//213880:/usr/bin/zsh | else | edit term://.//213880:/usr/bin/zsh | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 45 - ((44 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
45
normal! 0
tabedit ~/Documents/Studium/Pico-C_Compiler/test_parser.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
if bufexists("~/Documents/Studium/Pico-C_Compiler/test_parser.py") | buffer ~/Documents/Studium/Pico-C_Compiler/test_parser.py | else | edit ~/Documents/Studium/Pico-C_Compiler/test_parser.py | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 11 - ((10 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
11
normal! 02|
tabnext 5
set stal=1
if exists('s:wipebuf') && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 winminheight=1 winminwidth=1 shortmess=filnxtToOF
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
