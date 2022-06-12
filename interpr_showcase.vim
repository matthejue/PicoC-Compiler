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

set mouse=a


nnoremap <tab> /index:<CR>:noh<CR>zt
nnoremap <S-tab> ?index:<CR>:noh<CR>zt
nnoremap <esc> :qa!<CR>
nnoremap q :qa!<CR>

nnoremap s ggzR:<C-u>:set noscb<CR>:bo vs<CR>zRLjzt:setl scb<CR><C-w>p:setl scb<CR>

" minimize / maximize window and equalize windows
nnoremap m <C-w>1<bar>
nnoremap M <C-w><bar>
nnoremap e <C-w>=

let s:comments = 1
function! ToggleComments()
    if s:comments
      execute 'g/\/\/\|\#/d'
      set nu
      let s:comments = 0
    else
      norm u
      set nonu
      let s:comments = 1
    endif
endfunction

nnoremap c :call ToggleComments()<CR>

