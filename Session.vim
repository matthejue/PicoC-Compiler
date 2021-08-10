let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/Documents/Studium/pico-c-compiler/test
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +4 ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammar.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/assignment_allocation_grammar.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/ast_builder.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/conditional_grammar.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/errors.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/function_grammar.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/globals.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/input.picoc
badd +1 ~/Documents/Studium/pico-c-compiler/src/lexer.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/logic_expression_grammar.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/output.reti
badd +1 ~/Documents/Studium/pico-c-compiler/src/parser.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/pico_c_compiler.py
badd +1 ~/Documents/Studium/pico-c-compiler/src/statement_sequence_grammar.py
badd +24 ~/Documents/Studium/pico-c-compiler/test/test_grammar.py
argglobal
%argdel
$argadd ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
$argadd ~/Documents/Studium/pico-c-compiler/src/arithmetic_expression_grammar.py
$argadd ~/Documents/Studium/pico-c-compiler/src/assignment_allocation_grammar.py
$argadd ~/Documents/Studium/pico-c-compiler/src/ast_builder.py
$argadd ~/Documents/Studium/pico-c-compiler/src/conditional_grammar.py
$argadd ~/Documents/Studium/pico-c-compiler/src/errors.py
$argadd ~/Documents/Studium/pico-c-compiler/src/function_grammar.py
$argadd ~/Documents/Studium/pico-c-compiler/src/globals.py
$argadd ~/Documents/Studium/pico-c-compiler/src/input.picoc
$argadd ~/Documents/Studium/pico-c-compiler/src/lexer.py
$argadd ~/Documents/Studium/pico-c-compiler/src/logic_expression_grammar.py
$argadd ~/Documents/Studium/pico-c-compiler/src/output.reti
$argadd ~/Documents/Studium/pico-c-compiler/src/parser.py
$argadd ~/Documents/Studium/pico-c-compiler/src/pico_c_compiler.py
$argadd ~/Documents/Studium/pico-c-compiler/src/statement_sequence_grammar.py
edit ~/Documents/Studium/pico-c-compiler/test/test_grammar.py
argglobal
if bufexists("~/Documents/Studium/pico-c-compiler/test/test_grammar.py") | buffer ~/Documents/Studium/pico-c-compiler/test/test_grammar.py | else | edit ~/Documents/Studium/pico-c-compiler/test/test_grammar.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico-c-compiler/test/test_grammar.py
endif
balt ~/Documents/Studium/pico-c-compiler/src/abstract_syntax_tree.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
10
normal! zo
11
normal! zo
19
normal! zo
let s:l = 24 - ((23 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 24
normal! 012|
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0&& getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=IAoOaFTt
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
