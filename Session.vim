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
argglobal
%argdel
$argadd src/pico_c_compiler.py
argglobal
enew
file NERD_tree_1
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal nofen
tabnext 1
badd +55 src/pico_c_compiler.py
badd +0 src/error_handler.py
badd +1 errors.py
badd +1 NERD_tree_2
badd +9 ~/.SpaceVim.d/init.toml
badd +616 ~/.config_stow/spacevim/.SpaceVim.d/autoload/myspacevim.vim
badd +55 src/errors.py
badd +12 src/file_grammar.py
badd +1 src/file_node.py
badd +23 src/function_grammar.py
badd +26 src/function_nodes.py
badd +44 src/statement_grammar.py
badd +24 Makefile
badd +6 run_tests.sh
badd +19 ~/.SpaceVim/init.vim
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
nohlsearch
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
