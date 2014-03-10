" ======================================================
" Maintainer:	Derrick J Wippler <thrawn01@gmail.com>
" ======================================================

set ch=2		    " Make command line two lines high
set mousehide		" Hide the mouse when typing text
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

" Required for vundle
filetype off 
filetype plugin indent on

" Fuzzy Finder file ignores
set wildignore+=*.pyc,*.so,*.swp,

" Required for vim-python-pep8-indent
let g:pymode_indent = 0 

" Vundle
set rtp+=~/.vim/bundle/vundle/
call vundle#rc()

" Vundle Managed Vim Plugins ( :BundleInstall to install the Managed Bundles )
Bundle 'gmarik/vundle'

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

nmap <F8> :TagbarToggle<CR>
nmap <C-j> :YcmCompleter GoToDefinition<CR>
nmap <C-p> :CtrlP<CR>

