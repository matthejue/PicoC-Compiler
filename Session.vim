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
badd +4 ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
badd +3 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/ast_builder.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/conditional_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/errors.py
badd +3 ~/Documents/Studium/pico_c_compiler/src/function_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/globals.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/input.picoc
badd +4 ~/Documents/Studium/pico_c_compiler/src/lexer.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/logic_expression_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/output.reti
badd +3 ~/Documents/Studium/pico_c_compiler/src/parser.py
badd +7 ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py
badd +2 ~/Documents/Studium/pico_c_compiler/src/statement_sequence_grammar.py
badd +4 ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
badd +16 ~/Documents/Studium/pico_c_compiler/.vimspector.json
badd +13 ~/Documents/Studium/pico_c_compiler/Makefile
argglobal
%argdel
$argadd src/abstract_syntax_tree.py
$argadd src/arithmetic_expression_grammar.py
$argadd src/assignment_allocation_grammar.py
$argadd src/ast_builder.py
$argadd src/conditional_grammar.py
$argadd src/errors.py
$argadd src/function_grammar.py
$argadd src/globals.py
$argadd src/grammar.py
$argadd src/grammar_2.py
$argadd src/input.picoc
$argadd src/lexer.py
$argadd src/logic_expression_grammar.py
$argadd src/output.reti
$argadd src/parser.py
$argadd src/pico_c_compiler.py
$argadd src/statement_sequence_grammar.py
edit ~/Documents/Studium/pico_c_compiler/.vimspector.json
argglobal
if bufexists("~/Documents/Studium/pico_c_compiler/.vimspector.json") | buffer ~/Documents/Studium/pico_c_compiler/.vimspector.json | else | edit ~/Documents/Studium/pico_c_compiler/.vimspector.json | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico_c_compiler/.vimspector.json
endif
balt ~/Documents/Studium/pico_c_compiler/Makefile
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
1
normal! zo
2
normal! zo
3
normal! zo
5
normal! zo
17
normal! zo
let s:l = 16 - ((15 * winheight(0) + 21) / 42)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 16
normal! 09|
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
