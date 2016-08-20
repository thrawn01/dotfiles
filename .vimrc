" ======================================================
" Maintainer:  Derrick J Wippler <thrawn01@gmail.com>
" ======================================================

set ch=1            " Make command line 1 line high
set mousehide       " Hide the mouse when typing text
set dir=~/.vimswap  " Don't litter the filesystem with swapfiles
set expandtab
set shiftwidth=4
set tabstop=4
set nowrap
set background=dark
set guioptions-=T
set mousemodel=popup
set hlsearch
set autoindent
set tags=./tags;/ " Loads any files named 'tags' in the directory tree
set nocompatible
set ruler
set backspace=indent,eol,start
let python_highlight_all = 1
syntax on

" Show matching braces when cursor is over a brace
set showmatch

" Smart Indent
set si

" Set Font Size, Because I'm old and blind now
if has("gui_running")
  if has("gui_gtk2")
    set guifont=Inconsolata\ 12
  elseif has("gui_macvim")
    set guifont=Menlo\ Regular:h14
  elseif has("gui_win32")
    set guifont=Consolas:h11:cANSI
  elseif has("gui_vimr")
    set guifont=Menlo\ Regular:h14
  endif
endif

" Make shift-insert work like in Xterm
map <S-Insert> <MiddleMouse>
map! <S-Insert> <MiddleMouse>

" My personal Keybindings for Navigating Tabs
nmap <C-S-h> :tabprevious<cr>
nmap <C-S-l> :tabnext<cr>
map <C-S-h> :tabprevious<cr>
map <C-S-l> :tabnext<cr>
imap <C-S-h> <ESC>:tabprevious<cr>i
imap <C-S-l> <ESC>:tabnext<cr>i
nmap <C-S-N> :tabnew<cr>
imap <C-t> <ESC>:tabnew<cr>

" Support virtualenv if it exists
if has('python')
py << EOF
import os.path
import sys
import vim
if 'VIRTUAL_ENV' in os.environ:
    project_base_dir = os.environ['VIRTUAL_ENV']
    sys.path.insert(0, project_base_dir)
    activate_this = os.path.join(project_base_dir, 'bin/activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))
EOF
endif

" Put the basename on the GUI Tabs instead of the full path
function GuiTabLabel()
      let label = ''
      let bufnrlist = tabpagebuflist(v:lnum)

      " Add '+' if one of the buffers in the tab page is modified
      for bufnr in bufnrlist
        if getbufvar(bufnr, "&modified")
          let label = '+'
          break
        endif
      endfor

      " Append the number of windows in the tab page if more than one
      let wincount = tabpagewinnr(v:lnum, '$')
      if wincount > 1
        let label .= wincount
      endif
      if label != ''
        let label .= ' '
      endif

      " Append the buffer name
      return label . simplify(bufname(bufnrlist[tabpagewinnr(v:lnum) - 1]))
endfunction

"set guitablabel=%{GuiTabLabel()}
set guitablabel=%t

" Include go syntax highlighting
set rtp+=$GOROOT/misc/vim

" Required for vundle
filetype off 
filetype plugin indent on

" Fuzzy Finder file ignores
set wildignore+=*.pyc,*.so,*.swp,

" Required for vim-python-pep8-indent
let g:pymode_indent = 0 

" Vundle
set rtp+=~/.vim/bundle/Vundle.vim/
call vundle#rc()

" Vundle Managed Vim Plugins ( :PluginInstall to install the Managed Bundles )
Bundle 'gmarik/Vundle.vim'

" Completion with CTRL-J
Bundle 'Valloric/YouCompleteMe'
" GIT plugin :Gdiff
Bundle 'tpope/vim-fugitive'
" Start TagBar with F8
Bundle 'majutsushi/tagbar'
" Pep8 Check with F7
Bundle 'nvie/vim-flake8'
" Search for files with CTRL-P
Bundle 'kien/ctrlp.vim'
" Fixes indent to be pep8 compatable
Bundle 'hynek/vim-python-pep8-indent'
" Opens when VIM gets a directory to open
Bundle 'scrooloose/nerdtree'
" Fancy Status Line
Plugin 'bling/vim-airline'
" Go Language Plugins
Plugin 'fatih/vim-go'
" GeekNote Plugin
Bundle 'https://github.com/neilagabriel/vim-geeknote'

" GeekNote Plugin Settings
noremap <F9> :Geeknote<CR>
let g:GeeknoteFormat="markdown"

nmap <F8> :TagbarToggle<CR>
"nmap <C-j> :YcmCompleter GoToDefinition<CR>
nmap <C-j> :YcmCompleter GoToDefinitionElseDeclaration<CR>
nmap <C-p> :CtrlP<CR>

" Mark line longer than 79 characters in RED
highlight ColorColumn ctermbg=red
au BufWinEnter *.py let w:m1=matchadd('ColorColumn', '\%81v', 100)

" Make TABS and trailling spaces visible
"set listchars=tab:>~,nbsp:_,trail:.
set listchars=tab:>-,nbsp:_,trail:.
set list
set laststatus=2

" Enable Syntax highlighting
let g:go_highlight_functions = 1
let g:go_highlight_methods = 1
let g:go_highlight_structs = 1

au FileType *.go set tabstop=4 shiftwidth=4 noexpandtab nolist
au BufEnter *.go set ai sw=4 ts=4 noet nolist
au BufWinEnter *.go set ai sw=4 ts=4 noet nolist

au FileType *.sls set autoindent tabstop=2 shiftwidth=2 expandtab list
au BufEnter *.sls set ai sw=2 ts=2 et list
