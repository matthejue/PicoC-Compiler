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
badd +1 .gitignore
badd +1 src/abstract_syntax_tree.py
badd +1 src/arithmetic_expression_grammar.py
badd +1 src/assignment_allocation_grammar.py
badd +1 src/ast_builder.py
badd +1 src/conditional_grammar.py
badd +1 src/errors.py
badd +3 src/function_grammar.py
badd +1 src/globals.py
badd +1 src/grammar.py
badd +1 src/lexer.py
badd +1 src/logic_expression_grammar.py
badd +1 src/parser_.py
badd +82 src/pico_c_compiler.py
badd +1 src/statement_sequence_grammar.py
badd +49 ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
badd +0 src/pico_c_compiler.py.e02aafcd51c7ccbf4bb5d0d02f2a2bd0.py
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
$argadd src/lexer.py
$argadd src/logic_expression_grammar.py
$argadd src/parser_.py
$argadd src/pico_c_compiler.py
$argadd src/pico_c_compiler.py.e02aafcd51c7ccbf4bb5d0d02f2a2bd0.py
$argadd src/statement_sequence_grammar.py
argglobal
enew
balt ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0&& getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxAoOaFTtI
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
