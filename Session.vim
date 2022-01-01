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
argglobal
%argdel
argglobal
enew
file NERD_tree_6
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal nofen
if exists(':tcd') == 2 | tcd ~/Documents/Studium/pico_c_compiler | endif
tabnext 1
badd +36 ~/Documents/Studium/pico_c_compiler/src/lexer.py
badd +4 ~/Documents/Studium/pico_c_compiler/lexer.py
badd +41 ~/Documents/Studium/pico_c_compiler/src/if_else_grammar.py
badd +34 ~/Documents/Studium/pico_c_compiler/src/arithmetic_nodes.py
badd +29 ~/Documents/Studium/pico_c_compiler/src/symbol_table.py
badd +18 ~/Documents/Studium/pico_c_compiler/.misc/python_match_args_example.py
badd +37 ~/Documents/Studium/pico_c_compiler/src/abstract_syntax_tree.py
badd +59 ~/Documents/Studium/pico_c_compiler/src/arithmetic_expression_grammar.py
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0 && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxcsAoOaFTt
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
set hlsearch
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
