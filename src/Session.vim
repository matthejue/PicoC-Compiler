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
badd +5 ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
badd +69 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/ast_builder.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/errors.py
badd +8 ~/Documents/Studium/pico_c_compiler/src/function_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/globals.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/if_else_grammar.py
badd +99 ~/Documents/Studium/pico_c_compiler/src/lexer.py
badd +24 ~/Documents/Studium/pico_c_compiler/src/logic_expression_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/loop_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/parser_.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py
badd +14 ~/Documents/Studium/pico_c_compiler/src/statement_sequence_grammar.py
badd +51 ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
badd +7 ~/Documents/Studium/pico_c_compiler/input.picoc
badd +6 ~/Documents/Studium/pico_c_compiler/test/gcd.picoc
badd +0 term://~/Documents/Studium/pico_c_compiler//571704:/usr/bin/python
badd +1 term://~/Documents/Studium/pico_c_compiler//572106:/usr/bin/python
argglobal
%argdel
$argadd abstract_syntax_tree.py
$argadd arithmetic_expression_grammar.py
$argadd assignment_allocation_grammar.py
$argadd ast_builder.py
$argadd errors.py
$argadd function_grammar.py
$argadd globals.py
$argadd grammar.py
$argadd if_else_grammar.py
$argadd lexer.py
$argadd logic_expression_grammar.py
$argadd loop_grammar.py
$argadd parser_.py
$argadd pico_c_compiler.py
$argadd statement_sequence_grammar.py
edit ~/Documents/Studium/pico_c_compiler/src/lexer.py
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe '2resize ' . ((&lines * 6 + 23) / 47)
exe 'vert 2resize ' . ((&columns * 1 + 95) / 190)
argglobal
if bufexists("~/Documents/Studium/pico_c_compiler/src/lexer.py") | buffer ~/Documents/Studium/pico_c_compiler/src/lexer.py | else | edit ~/Documents/Studium/pico_c_compiler/src/lexer.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico_c_compiler/src/lexer.py
endif
balt ~/Documents/Studium/pico_c_compiler/test/gcd.picoc
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
let s:l = 99 - ((3 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 99
normal! 0
wincmd w
argglobal
enew
balt ~/Documents/Studium/pico_c_compiler/src/lexer.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
wincmd w
exe '2resize ' . ((&lines * 6 + 23) / 47)
exe 'vert 2resize ' . ((&columns * 1 + 95) / 190)
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0&& getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxIAoOaFTt
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
