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
badd +93 src/abstract_syntax_tree.py
badd +100 src/arithmetic_expression_grammar.py
badd +54 src/assignment_allocation_grammar.py
badd +30 src/ast_builder.py
badd +89 src/errors.py
badd +44 src/function_grammar.py
badd +3 src/globals.py
badd +18 src/grammar.py
badd +79 src/if_else_grammar.py
badd +1 src/lexer.py
badd +1 src/loop_grammar.py
badd +70 src/parser_.py
badd +104 src/pico_c_compiler.py
badd +47 src/statement_sequence_grammar.py
badd +88 test/grammar_test.py
badd +16 input.picoc
badd +1 test/gcd.picoc
badd +1 src/code_generator.py
badd +1 src/symbol_table.py
badd +1 output.reti
badd +1 Makefile
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
edit src/errors.py
let s:save_splitbelow = &splitbelow
let s:save_splitright = &splitright
set splitbelow splitright
wincmd _ | wincmd |
vsplit
wincmd _ | wincmd |
vsplit
2wincmd h
wincmd w
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
exe 'vert 1resize ' . ((&columns * 125 + 95) / 190)
exe 'vert 2resize ' . ((&columns * 27 + 95) / 190)
exe 'vert 3resize ' . ((&columns * 36 + 95) / 190)
exe '4resize ' . ((&lines * 22 + 23) / 47)
exe 'vert 4resize ' . ((&columns * 1 + 95) / 190)
exe '5resize ' . ((&lines * 21 + 23) / 47)
exe 'vert 5resize ' . ((&columns * 1 + 95) / 190)
argglobal
if bufexists("src/errors.py") | buffer src/errors.py | else | edit src/errors.py | endif
if &buftype ==# 'terminal'
  silent file src/errors.py
endif
balt src/lexer.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
let s:l = 89 - ((42 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 89
normal! 03|
wincmd w
argglobal
if bufexists("output.reti") | buffer output.reti | else | edit output.reti | endif
if &buftype ==# 'terminal'
  silent file output.reti
endif
balt input.picoc
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
let s:l = 1 - ((0 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 0
wincmd w
argglobal
enew
file __Tagbar__.3
balt input.picoc
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
wincmd w
argglobal
enew
balt output.reti
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
wincmd w
argglobal
enew
balt src/if_else_grammar.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
wincmd w
exe 'vert 1resize ' . ((&columns * 125 + 95) / 190)
exe 'vert 2resize ' . ((&columns * 27 + 95) / 190)
exe 'vert 3resize ' . ((&columns * 36 + 95) / 190)
exe '4resize ' . ((&lines * 22 + 23) / 47)
exe 'vert 4resize ' . ((&columns * 1 + 95) / 190)
exe '5resize ' . ((&lines * 21 + 23) / 47)
exe 'vert 5resize ' . ((&columns * 1 + 95) / 190)
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
