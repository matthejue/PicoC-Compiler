se nonu
se nornu
se so=0
se nocursorcolumn
se nocursorline

set expandtab     " insert spaces whenever tab key is pressed
set tabstop=2     " number of space characters that will be inserted with tab
set shiftwidth=2  " indentation by 2 spaces

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

nnoremap S ggzR:<C-u>:set noscb<CR>:bo vs<CR>zRLjzt:setl scb<CR><C-w>p:setl scb<CR>

" minimize / maximize window and equalize windows
nnoremap m <C-w>1<bar>
nnoremap M <C-w><bar>
nnoremap E <C-w>=

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

nnoremap N :set nu!<CR>
nnoremap R :set rnu!<CR>

" hide/unhide colorized lines
let s:higlight_on = 1
function! ToggleMatchHighlight()
    if s:higlight_on  == 1
        let s:higlight_on = 0
        highlight Color1 ctermbg=1 ctermfg=0 guibg=1 guifg=0
        highlight Color2 ctermbg=2 ctermfg=0 guibg=2 guifg=0
        highlight Color3 ctermbg=3 ctermfg=0 guibg=3 guifg=0
        highlight Color4 ctermbg=4 ctermfg=0 guibg=4 guifg=0
        highlight Color5 ctermbg=5 ctermfg=0 guibg=5 guifg=0
        highlight Color6 ctermbg=6 ctermfg=0 guibg=6 guifg=0
        highlight Color7 ctermbg=7 ctermfg=0 guibg=7 guifg=0
    else
        let s:higlight_on = 1
        highlight clear Color1
        highlight clear Color2
        highlight clear Color3
        highlight clear Color4
        highlight clear Color5
        highlight clear Color6
        highlight clear Color7
    endif
endfunction

nnoremap H :call ToggleMatchHighlight()<CR>

call ToggleMatchHighlight()

" colorize line under cursor
nnoremap 1 :call matchadd("Color1", '\%'.line('.').'l')<CR>
nnoremap 2 :call matchadd("Color2", '\%'.line('.').'l')<CR>
nnoremap 3 :call matchadd("Color3", '\%'.line('.').'l')<CR>
nnoremap 4 :call matchadd("Color4", '\%'.line('.').'l')<CR>
nnoremap 5 :call matchadd("Color5", '\%'.line('.').'l')<CR>
nnoremap 6 :call matchadd("Color6", '\%'.line('.').'l')<CR>
nnoremap 7 :call matchadd("Color7", '\%'.line('.').'l')<CR>
" remove colorized lines
nnoremap D :call clearmatches()<CR>

" colorize selectection everywhere
vnoremap 1 "ay:call matchadd("Color1", "<C-r>a")<CR>
vnoremap 2 "ay:call matchadd("Color2", "<C-r>a")<CR>
vnoremap 3 "ay:call matchadd("Color3", "<C-r>a")<CR>
vnoremap 4 "ay:call matchadd("Color4", "<C-r>a")<CR>
vnoremap 5 "ay:call matchadd("Color5", "<C-r>a")<CR>
vnoremap 6 "ay:call matchadd("Color6", "<C-r>a")<CR>
vnoremap 7 "ay:call matchadd("Color7", "<C-r>a")<CR>
