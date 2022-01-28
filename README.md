<h1 align="center">PicoC-Compiler</h3>
<p align="center">Compiles <strong>PicoC</strong> (a subset of C) into <strong>RETI-Assembler</strong>.</p>

<p align="center">
<a href="./LICENSE.md"><img src="https://img.shields.io/github/license/matthejue/PicoC-Compiler.svg"></a>
<img src="https://img.shields.io/badge/Maintained%3F-yes-green.svg">
<img height="20px" src="http://ForTheBadge.com/images/badges/made-with-python.svg">
</p>

# Usage


# Used patterns
- **LL(1) Recursive-Descent Lexer** (p. 50 et seq. from [[1]](#1))
- **Backtracking Parser** (p. 71 et seq. from [[1]](#1)))
- **Factory Function** used to implement **Singleton Pattern** (from [[2]](#2))

# Used literature
- for the patterns and knowledge about **lexers** and **parsers** [[1]](#1)
- the desgin of the **abstract syntax** is greatly inspired by [[3]](#3)

# Used software
- **Neovim** with plugins in [[4]](#4) and **Tmux** with plugins in [[5]](#5) for **coding** the compiler and writing the **presentation**
- **Marp** for creating the **presentation** [[6]](#6)
- **Drawio-desktop** for planning the **architecture** [[7]](#7)
- **PyInstaller** [[8]](#8) and **StaticX** [[9]](#9) to create the **executable**
- **Zatero** for **citing** [[10]](#10)

# References
- <a id="1">[1]</a> Parr, Terence. Language implementation patterns: create your own domain-specific and general programming languages. Pragmatic Bookshelf, 2009.
- <a id="2">[2]</a> Keith. “Singleton Pattern In Python.” Stack Overflow. Accessed January 28, 2022. https://stackoverflow.com/questions/52351312/singleton-pattern-in-python.
- <a id="3">[3]</a> IU-Fall-2021. “Course Webpage for Compilers (P423, P523, E313, and E513).” Accessed January 28, 2022. https://iucompilercourse.github.io/IU-Fall-2021/.
- <a id="4">[4]</a> **Used Vim Plugins:**
'vifm/vifm.vim', 'lilydjwg/colorizer', 'ferrine/md-img-paste.vim', 'tpope/vim-fugitive', 'airblade/vim-gitgutter', 'tpope/vim-dispatch', 'honza/vim-snippets', 'tpope/vim-surround', 'godlygeek/tabular', 'justinmk/vim-sneak', 'unblevable/quick-scope', puremourning/vimspector', 'tpope/vim-eunuch', 'Vimjas/vim-python-pep8-indent', 'terrortylor/nvim-comment', 'neoclide/coc.nvim', 'fannheyward/coc-pyright', 'airblade/vim-rooter', 'sk1418/howmuch', 'metakirby5/codi.vim', 'sedm0784/vim-you-autocorrect', 'wfxr/minimap.vim', 'folke/which-key.nvim', 'voldikss/vim-floaterm', 'mhinz/vim-startify', 'nvim-telescope/telescope.nvim', 'nvim-lua/popup.nvim', 'nvim-lua/plenary.nvim', 'folke/zen-mode.nvim', 'romgrk/barbar.nvim', 'karb94/neoscroll.nvim', 'chaoren/vim-wordmotion', 'gcmt/wildfire.vim', 'cohama/lexima.vim', 'AckslD/nvim-neoclip.lua', 'preservim/tagbar', 'xolox/vim-easytags', 'xolox/vim-misc', 'tversteeg/registers.nvim', 'svermeulen/vim-subversive', 'mg979/vim-visual-multi', 'akinsho/toggleterm.nvim', 'simnalamburt/vim-mundo', 'AndrewRadev/switch.vim'
- <a id="5">[5]</a> **Used Tmux Plugins:**
'tmux-plugins/tmux-copycat', 'tmux-plugins/tmux-open', 'tmux-plugins/tmux-resurrect', 'schasse/tmux-jump', 'laktak/extrakto'
- <a id="6">[6]</a> https://github.com/marp-team/marp-cli
- <a id="7">[7]</a> https://github.com/jgraph/drawio-desktop/releases
- <a id="8">[8]</a> https://github.com/pyinstaller/pyinstaller/wiki/FAQ
- <a id="9">[9]</a> https://github.com/JonathonReinhart/staticx/
- <a id="10">[10]</a> https://www.zotero.org/
