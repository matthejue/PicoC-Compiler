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

nnoremap n :set nu!<CR>
nnoremap r :set rnu!<CR>

autocmd VimEnter *
        \ highlight Color1 ctermbg=1 ctermfg=0 guibg=1 guifg=0 |
        \ highlight Color2 ctermbg=2 ctermfg=0 guibg=2 guifg=0 |
        \ highlight Color3 ctermbg=3 ctermfg=0 guibg=3 guifg=0 |
        \ highlight Color4 ctermbg=4 ctermfg=0 guibg=4 guifg=0 |
        \ highlight Color5 ctermbg=5 ctermfg=0 guibg=5 guifg=0 |
        \ highlight Color6 ctermbg=6 ctermfg=0 guibg=6 guifg=0 |
        \ highlight Color7 ctermbg=7 ctermfg=0 guibg=7 guifg=0
  nnoremap 1 :call matchadd("Color1", '\%'.line('.').'l')<CR>
  nnoremap 2 :call matchadd("Color2", '\%'.line('.').'l')<CR>
  nnoremap 3 :call matchadd("Color3", '\%'.line('.').'l')<CR>
  nnoremap 4 :call matchadd("Color4", '\%'.line('.').'l')<CR>
  nnoremap 5 :call matchadd("Color5", '\%'.line('.').'l')<CR>
  nnoremap 6 :call matchadd("Color6", '\%'.line('.').'l')<CR>
  nnoremap 7 :call matchadd("Color7", '\%'.line('.').'l')<CR>
  nnoremap C :call clearmatches()<CR>
