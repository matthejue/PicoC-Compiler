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
badd +162 src/abstract_syntax_tree.py
badd +113 src/arithmetic_expression_grammar.py
badd +13 src/assignment_allocation_grammar.py
badd +1 src/ast_builder.py
badd +1 src/errors.py
badd +1 src/function_grammar.py
badd +1 src/globals.py
badd +1 src/grammar.py
badd +14 src/if_else_grammar.py
badd +131 src/lexer.py
badd +15 src/logic_expression_grammar.py
badd +1 src/loop_grammar.py
badd +1 src/parser_.py
badd +1 src/pico_c_compiler.py
badd +3 src/statement_sequence_grammar.py
badd +269 test/grammar_test.py
badd +1 input.picoc
badd +1 test/gcd.picoc
badd +82 src/code_generator.py
badd +95 src/symbol_table.py
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
edit src/abstract_syntax_tree.py
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe '2resize ' . ((&lines * 8 + 23) / 47)
exe 'vert 2resize ' . ((&columns * 1 + 95) / 190)
argglobal
balt test/grammar_test.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
102
normal! zo
104
normal! zo
114
normal! zo
122
normal! zo
124
normal! zo
132
normal! zo
154
normal! zo
154
normal! zo
164
normal! zo
142
normal! zo
145
normal! zo
157
normal! zo
162
normal! zo
166
normal! zo
170
normal! zo
170
normal! zo
170
normal! zo
180
normal! zo
363
normal! zo
365
normal! zo
let s:l = 162 - ((35 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 162
normal! 0
wincmd w
argglobal
enew
balt src/code_generator.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
wincmd w
exe '2resize ' . ((&lines * 8 + 23) / 47)
exe 'vert 2resize ' . ((&columns * 1 + 95) / 190)
if exists(':tcd') == 2 | tcd ~/Documents/Studium/pico_c_compiler | endif
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
