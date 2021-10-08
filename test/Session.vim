let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/Documents/Studium/pico_c_compiler/test
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +743 ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
badd +119 ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
badd +54 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_grammar.py
badd +5 ~/Documents/Studium/pico_c_compiler/src/ast_builder.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/errors.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/function_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/globals.py
badd +21 ~/Documents/Studium/pico_c_compiler/src/grammar.py
badd +17 ~/Documents/Studium/pico_c_compiler/src/if_else_grammar.py
badd +3 ~/Documents/Studium/pico_c_compiler/src/lexer.py
badd +18 ~/Documents/Studium/pico_c_compiler/src/logic_expression_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/loop_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/parser_.py
badd +104 ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py
badd +3 ~/Documents/Studium/pico_c_compiler/src/statement_sequence_grammar.py
badd +58 ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
badd +1 ~/Documents/Studium/pico_c_compiler/input.picoc
badd +1 ~/Documents/Studium/pico_c_compiler/test/gcd.picoc
badd +37 ~/Documents/Studium/pico_c_compiler/src/code_generator.py
badd +114 ~/Documents/Studium/pico_c_compiler/src/symbol_table.py
badd +61 ~/Documents/Studium/pico_c_compiler/output.reti
badd +0 term://~/Documents/Studium/pico_c_compiler//155051:/usr/bin/python
badd +1 term://~/Documents/Studium/pico_c_compiler//171935:/usr/bin/python
badd +1 term://~/Documents/Studium/pico_c_compiler//192566:/usr/bin/python
badd +0 term://~/Documents/Studium/pico_c_compiler//198396:/usr/bin/python
badd +0 term://~/Documents/Studium/pico_c_compiler//205889:/usr/bin/python
badd +0 term://~/Documents/Studium/pico_c_compiler//207108:/usr/bin/python
badd +1 term://~/Documents/Studium/pico_c_compiler//222794:/usr/bin/python
argglobal
%argdel
$argadd ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
$argadd ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/ast_builder.py
$argadd ~/Documents/Studium/pico_c_compiler/src/errors.py
$argadd ~/Documents/Studium/pico_c_compiler/src/function_grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/globals.py
$argadd ~/Documents/Studium/pico_c_compiler/src/grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/if_else_grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/lexer.py
$argadd ~/Documents/Studium/pico_c_compiler/src/logic_expression_grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/loop_grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/src/parser_.py
$argadd ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py
$argadd ~/Documents/Studium/pico_c_compiler/src/statement_sequence_grammar.py
edit ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
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
exe 'vert 1resize ' . ((&columns * 95 + 95) / 190)
exe 'vert 2resize ' . ((&columns * 94 + 95) / 190)
argglobal
if bufexists("~/Documents/Studium/pico_c_compiler/test/grammar_test.py") | buffer ~/Documents/Studium/pico_c_compiler/test/grammar_test.py | else | edit ~/Documents/Studium/pico_c_compiler/test/grammar_test.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
endif
balt ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
let s:l = 58 - ((39 * winheight(0) + 20) / 41)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 58
normal! 0
wincmd w
argglobal
if bufexists("~/Documents/Studium/pico_c_compiler/test/grammar_test.py") | buffer ~/Documents/Studium/pico_c_compiler/test/grammar_test.py | else | edit ~/Documents/Studium/pico_c_compiler/test/grammar_test.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico_c_compiler/test/grammar_test.py
endif
balt ~/Documents/Studium/pico_c_compiler/src/logic_expression_grammar.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 50 - ((19 * winheight(0) + 20) / 41)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 50
normal! 0
wincmd w
exe 'vert 1resize ' . ((&columns * 95 + 95) / 190)
exe 'vert 2resize ' . ((&columns * 94 + 95) / 190)
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
