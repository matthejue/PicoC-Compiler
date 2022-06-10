se nonu
se nornu
se so=0
se nocursorcolumn
se nocursorline

set noshowmode
set noruler
set laststatus=0
set noshowcmd

set noautoread

nnoremap <tab> /index:<CR>:noh<CR>zt
nnoremap <S-tab> ?index:<CR>:noh<CR>zt
nnoremap <esc> :qa!<CR>
nnoremap q :qa!<CR>

nnoremap s ggzR:<C-u>:set noscb<CR>:bo vs<CR>zRLjzt:setl scb<CR><C-w>p:setl scb<CR>
