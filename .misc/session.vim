let SessionLoad = 1
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/Documents/Studium/pico-c-compiler
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +71 ~/Documents/Studium/pico-c-compiler/_arithmetic_expressions.py
badd +1 ~/Documents/Studium/pico-c-compiler/errors.py
badd +45 ~/Documents/Studium/pico-c-compiler/lexer.py
badd +68 ~/Documents/Studium/pico-c-compiler/parser.py
badd +139 ~/Documents/Studium/pico-c-compiler/pico_c_compiler.py
badd +5 ~/Documents/Studium/pico-c-compiler/test_errors.py
badd +5 ~/Documents/Studium/pico-c-compiler/test_parser.py
badd +27 ~/Documents/Studium/pico-c-compiler/tokentypes.py
badd +2 ~/Documents/Studium/pico-c-compiler/tok.py
badd +1 ~/Documents/Studium/pico-c-compiler/input.picoc
badd +1 ~/Documents/Studium/pico-c-compiler/output.reti
badd +18 ~/Documents/Studium/pico-c-compiler/grammer.txt
badd +21 term://.//245689:/usr/bin/zsh
badd +19 ~/Documents/Studium/pico-c-compiler/_allocation_assignment_expressions.py
badd +1 ~/Documents/Studium/pico-c-compiler/symbol_table.py
badd +1 ~/Documents/Studium/pico-c-compiler/globals.py
badd +17 ~/Documents/Studium/pico-c-compiler/_statement_sequences.py
badd +299 term://.//394429:/usr/bin/zsh
badd +1 term:///home/areo/Documents/Studium/pico-c-compiler//260500:/usr/bin/python
badd +1 term:///home/areo/Documents/Studium/pico-c-compiler//271076:/usr/bin/python
argglobal
%argdel
$argadd _arithmetic_expressions.py
$argadd errors.py
$argadd lexer.py
$argadd parser.py
$argadd pico_c_compiler.py
$argadd test_errors.py
$argadd test_parser.py
$argadd tokentypes.py
$argadd tok.py
$argadd input.picoc
$argadd output.reti
$argadd grammer.txt
set stal=2
edit ~/Documents/Studium/pico-c-compiler/pico_c_compiler.py
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
let s:l = 14 - ((13 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
14
normal! 020|
tabedit ~/Documents/Studium/pico-c-compiler/errors.py
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
let s:l = 37 - ((36 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
37
normal! 09|
tabedit ~/Documents/Studium/pico-c-compiler/symbol_table.py
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
if bufexists("~/Documents/Studium/pico-c-compiler/symbol_table.py") | buffer ~/Documents/Studium/pico-c-compiler/symbol_table.py | else | edit ~/Documents/Studium/pico-c-compiler/symbol_table.py | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 46 - ((44 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
46
normal! 012|
tabedit ~/Documents/Studium/pico-c-compiler/globals.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/globals.py") | buffer ~/Documents/Studium/pico-c-compiler/globals.py | else | edit ~/Documents/Studium/pico-c-compiler/globals.py | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 4 - ((3 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
4
normal! 074|
tabedit ~/Documents/Studium/pico-c-compiler/lexer.py
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
let s:l = 70 - ((37 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
70
normal! 047|
tabedit ~/Documents/Studium/pico-c-compiler/parser.py
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
let s:l = 27 - ((26 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
27
normal! 06|
tabedit ~/Documents/Studium/pico-c-compiler/_statement_sequences.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/_statement_sequences.py") | buffer ~/Documents/Studium/pico-c-compiler/_statement_sequences.py | else | edit ~/Documents/Studium/pico-c-compiler/_statement_sequences.py | endif
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
normal! 047|
tabedit ~/Documents/Studium/pico-c-compiler/_allocation_assignment_expressions.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/_allocation_assignment_expressions.py") | buffer ~/Documents/Studium/pico-c-compiler/_allocation_assignment_expressions.py | else | edit ~/Documents/Studium/pico-c-compiler/_allocation_assignment_expressions.py | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 21 - ((20 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
21
normal! 020|
tabedit ~/Documents/Studium/pico-c-compiler/_arithmetic_expressions.py
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
let s:l = 16 - ((15 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
16
normal! 017|
tabedit ~/Documents/Studium/pico-c-compiler/tok.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
9argu
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 14 - ((13 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
14
normal! 033|
tabedit ~/Documents/Studium/pico-c-compiler/tokentypes.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
8argu
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 21 - ((20 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
21
normal! 0
tabedit ~/Documents/Studium/pico-c-compiler/input.picoc
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
10argu
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
normal! 012|
tabedit ~/Documents/Studium/pico-c-compiler/output.reti
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
11argu
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
normal! 077|
tabedit ~/Documents/Studium/pico-c-compiler/grammer.txt
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
12argu
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 12 - ((11 * winheight(0) + 22) / 45)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
12
normal! 042|
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
11argu
if bufexists("term://.//394429:/usr/bin/zsh") | buffer term://.//394429:/usr/bin/zsh | else | edit term://.//394429:/usr/bin/zsh | endif
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
tabnext 15
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
