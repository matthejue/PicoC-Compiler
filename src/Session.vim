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
badd +100 ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/arithmetic_nodes.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/assignment_allocation_nodes.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/ast_builder.py
badd +44 ~/Documents/Studium/pico_c_compiler/src/code_generator.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/errors.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/function_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/function_nodes.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/global_vars.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/grammar.py
badd +60 ~/Documents/Studium/pico_c_compiler/src/if_else_grammar.py
badd +98 ~/Documents/Studium/pico_c_compiler/src/if_else_nodes.py
badd +38 ~/Documents/Studium/pico_c_compiler/src/lexer.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/lexer_2.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/logic_expression_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/logic_nodes.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/loop_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/loop_nodes.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/parser_.py
badd +19 ~/Documents/Studium/pico_c_compiler/src/pico_c_compiler.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/statement_grammar.py
badd +1 ~/Documents/Studium/pico_c_compiler/src/symbol_table.py
badd +1 ~/Documents/Studium/pico_c_compiler/test/parser_test.py
badd +95 ~/Documents/Studium/pico_c_compiler/test/code_generator_test.py
badd +1 ~/.config_stow/nvim/.config/nvim/plugin_settings.vim
badd +47 ~/Documents/Studium/pico_c_compiler/test/testing_helpers.py
badd +1 ~/Documents/Studium/pico_c_compiler/statement_nodes.py
badd +3 ~/Documents/Studium/pico_c_compiler/test/execution_test.py
badd +7 ~/Documents/Studium/pico_c_compiler/test/misc_test.py
badd +43 ~/Documents/Studium/pico_c_compiler/Makefile
badd +4 ~/Documents/Studium/pico_c_compiler/input.picoc
badd +0 ~/Documents/Studium/pico_c_compiler/output.reti
badd +15 ~/Documents/Studium/pico_c_compiler/.vimspector.json
argglobal
%argdel
$argadd abstract_syntax_tree.py
$argadd arithmetic_expression_grammar.py
$argadd arithmetic_nodes.py
$argadd assignment_allocation_grammar.py
$argadd assignment_allocation_nodes.py
$argadd ast_builder.py
$argadd code_generator.py
$argadd errors.py
$argadd function_grammar.py
$argadd function_nodes.py
$argadd global_vars.py
$argadd grammar.py
$argadd if_else_grammar.py
$argadd if_else_nodes.py
$argadd lexer.py
$argadd lexer_2.py
$argadd logic_expression_grammar.py
$argadd logic_nodes.py
$argadd loop_grammar.py
$argadd loop_nodes.py
$argadd parser_.py
$argadd pico_c_compiler.py
$argadd statement_grammar.py
$argadd ~/Documents/Studium/pico_c_compiler/statement_nodes.py
$argadd symbol_table.py
edit ~/Documents/Studium/pico_c_compiler/src/if_else_nodes.py
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
exe 'vert 1resize ' . ((&columns * 108 + 95) / 190)
exe 'vert 2resize ' . ((&columns * 40 + 95) / 190)
exe 'vert 3resize ' . ((&columns * 40 + 95) / 190)
argglobal
if bufexists("~/Documents/Studium/pico_c_compiler/src/if_else_nodes.py") | buffer ~/Documents/Studium/pico_c_compiler/src/if_else_nodes.py | else | edit ~/Documents/Studium/pico_c_compiler/src/if_else_nodes.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico_c_compiler/src/if_else_nodes.py
endif
balt ~/Documents/Studium/pico_c_compiler/src/lexer.py
setlocal fdm=expr
setlocal fde=nvim_treesitter#foldexpr()
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
let s:l = 98 - ((39 * winheight(0) + 21) / 43)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 98
normal! 0
wincmd w
argglobal
if bufexists("~/Documents/Studium/pico_c_compiler/output.reti") | buffer ~/Documents/Studium/pico_c_compiler/output.reti | else | edit ~/Documents/Studium/pico_c_compiler/output.reti | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/Studium/pico_c_compiler/output.reti
endif
balt ~/Documents/Studium/pico_c_compiler/output.reti
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
file ~/Documents/Studium/pico_c_compiler/__Tagbar__.1
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal nofen
wincmd w
exe 'vert 1resize ' . ((&columns * 108 + 95) / 190)
exe 'vert 2resize ' . ((&columns * 40 + 95) / 190)
exe 'vert 3resize ' . ((&columns * 40 + 95) / 190)
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
