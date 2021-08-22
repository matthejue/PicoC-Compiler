let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/Documents/Studium/pico_c_compiler
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +5 ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/ast_builder.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/errors.py
badd +8 ~/Documents/Studium/pico_c_compiler/src/function_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/globals.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/if_else_grammar.py
badd +131 ~/Documents/Studium/pico_c_compiler/src/lexer.py
badd +24 ~/Documents/Studium/pico_c_compiler/src/logic_expression_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/loop_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/parser_.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py
badd +14 ~/Documents/Studium/pico_c_compiler/src/statement_sequence_grammar.py
badd +44 ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
badd +12 ~/Documents/Studium/pico_c_compiler/input.picoc
argglobal
%argdel
$argadd src/abstract_syntax_tree.py
$argadd src/arithmetic_expression_grammar.py
$argadd src/assignment_allocation_grammar.py
$argadd src/ast_builder.py
$argadd src/errors.py
$argadd src/function_grammar.py
$argadd src/globals.py
$argadd src/grammar.py
$argadd src/if_else_grammar.py
$argadd src/lexer.py
$argadd src/logic_expression_grammar.py
$argadd src/loop_grammar.py
$argadd src/parser_.py
$argadd src/pico_c_compiler.py
$argadd src/statement_sequence_grammar.py
edit ~/Documents/Studium/pico_c_compiler/input.picoc
argglobal
if bufexists("~/Documents/Studium/pico_c_compiler/input.picoc") | buffer ~/Documents/Studium/pico_c_compiler/input.picoc | else | edit ~/Documents/Studium/pico_c_compiler/input.picoc | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico_c_compiler/input.picoc
endif
balt ~/Documents/Studium/pico_c_compiler/src/logic_expression_grammar.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
let s:l = 12 - ((11 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 12
normal! 06|
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0&& getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxIAoOaFTt
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
