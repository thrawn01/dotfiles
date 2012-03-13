" An example for a gvimrc file.
" The commands in this are executed when the GUI is started.
"
" Maintainer:	Bram Moolenaar <Bram@vim.org>
" Last change:	2001 Sep 02
"
" To use it, copy it to
"     for Unix and OS/2:  ~/.gvimrc
"	      for Amiga:  s:.gvimrc
"  for MS-DOS and Win32:  $VIM\_gvimrc
"	    for OpenVMS:  sys$login:.gvimrc

" Make external commands work through a pipe instead of a pseudo-tty
"set noguipty

" set the X11 font to use
" set guifont=-misc-fixed-medium-r-normal--14-130-75-75-c-70-iso8859-1

set ch=2		" Make command line two lines high

set mousehide		" Hide the mouse when typing text
set dir=~/.vimswap
set expandtab
set shiftwidth=4
set tabstop=4
set nowrap
syntax on
set background=dark
set guioptions-=T
set mousemodel=popup
set hlsearch
set autoindent
set tags=~/.vim/tags
filetype on
let python_highlight_all = 1

" Make shift-insert work like in Xterm
map <S-Insert> <MiddleMouse>
map! <S-Insert> <MiddleMouse>

nmap <C-S-h> :tabprevious<cr>
nmap <C-S-l> :tabnext<cr>
map <C-S-h> :tabprevious<cr>
map <C-S-l> :tabnext<cr>
imap <C-S-h> <ESC>:tabprevious<cr>i
imap <C-S-l> <ESC>:tabnext<cr>i
nmap <C-S-N> :tabnew<cr>
imap <C-t> <ESC>:tabnew<cr>

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

