" Csaba Palankai <csaba.palankai@gmail.com>

" Don't be compatible with original vi. Must be first, changes other settings
set nocompatible

" mouse and keyboard selections enter visual mode, not select mode
set selectmode=

" right mouse button extends selection instead of context menu
set mousemodel=extend

" shift plus movement keys changes selection
set keymodel=startsel,stopsel

" allow cursor to be positioned one char past end of line
" and apply operations to all of selection including last char
set selection=exclusive

" allow backgrounding buffers without writing them
" and remember marks/undo for backgrounded buffers
set hidden

" Keep more context when scrolling off the end of a buffer
set scrolloff=3

" Make searches case-sensitive only if they contain upper-case characters
set noignorecase
set smartcase
" show search matches as the search pattern is typed
set incsearch

" don't flick the cursor to show matching brackets, they are already highlighted
set noshowmatch

" highlight last search matches
set hlsearch
" ctl-l doesn't just refresh window, but also hides search highlights
nnoremap <silent> <c-l> :nohlsearch<cr><c-l>
inoremap <silent> <c-l> :nohlsearch<cr><c-l>

" search-next wraps back to start of file
set wrapscan

" make tab completion for files/buffers act like bash
set wildmenu
set wildmode=list:longest
" stuff to ignore when autocompleting filenames
set wildignore=*.pyc,*.pyo

" allow backspacing over everything in insert mode
set backspace=indent,eol,start

set backupdir=~/.vim-tmp//
set directory=~/.vim-tmp//
set backupskip=/tmp/*,/private/tmp/*"
set backup
" persist undo info, so you can undo even after closing and re-opening a file
if version >= 730
    set undofile
    set undodir=~/.vim/tmp//
endif

" use 'comma' prefix for user-defined multi-stroke keyboard mappings
let mapleader = ","

if has("autocmd")

    " enables filetype detection
    filetype on
    " enables filetype specific plugins
    filetype plugin on
    " do language-dependent indenting.
    filetype indent off

    " For all text files set 'textwidth' to 80 characters.
    autocmd FileType text setlocal textwidth=80

    " make syntax highlighting work correctly on long files
    autocmd BufEnter * :syntax sync fromstart

    " When editing a file, always jump to the last known cursor position.
    autocmd BufReadPost * call SetLastCursorPosition()
    function! SetLastCursorPosition()
      " Don't do it when the position is invalid or when inside an event
      " handler (happens when dropping a file on gvim).
      if line("'\"") > 0 && line("'\"") <= line("$")
        exe "normal g`\""
        normal! zz
      endif
    endfunction

    " highlighting for unusual file extensions
    au BufNewFile,BufRead *.hql set filetype=sql
    au BufNewFile,BufRead *.sqli set filetype=sql

endif " has("autocmd")

" sane text files
set fileformat=unix
set fileformats=unix,dos,mac
set encoding=utf-8

" sane editing
set tabstop=4
set shiftwidth=4
set softtabstop=4
set expandtab

" indenting.
" *All* the smart indent settings and plugins are TOTALLY FUCKED.
" Disable them all
set nocindent
set indentexpr=
" except for plain autoindent, which preserves indent from the previous line)
set autoindent
" and smartindent, which indents in and out after { and }
set smartindent

" stop autoindent from unindenting lines typed starting with '#'
inoremap # X<backspace>#

" display and colors
set background=dark

" lastline: don't display truncated last lines as '@' chars
" uhex: show unprintable chars as hex <xx> instead of ^C and ~C.
set display+=lastline

" display current mode on the last line (e.g. '-- INSERT --')
set showmode

" display number of selected chars, lines, or size of blocks.
set showcmd

set formatoptions-=t
set formatoptions-=c
set formatoptions+=r
set formatoptions+=o
set formatoptions+=q
set formatoptions-=w
set formatoptions-=a
" formatoptions 'n' stops autoformat from messing up numbered lists.
set formatoptions+=n
" Make autoformat of numbered lists also handle bullets, using asterisks:
set formatlistpat=^\\s*[0-9*]\\+[\\]:.)}\\t\ ]\\s*

" display long lines as wrapped
set wrap
" wrap at exactly char 80, not at word breaks
set nolinebreak
" show an ellipsis at the start of wrapped lines
set showbreak=\

" toggle wrapped appearance of long lines
function! ToggleWrap()
    if &wrap == 0
        set wrap
    else
        set nowrap
    endif
endfunction

noremap <leader>w :call ToggleWrap()<cr>


" key to toggle visibility of tabs & trailing whitespace
set listchars=tab:>-,trail:.
set nolist
nmap <silent> <leader>s :set nolist!<cr>

" key to strip trailing whitespace
nmap <silent> <leader>S ms:%s/\s\+$//<cr>`s

" key to toggle line numbers
" set nonumber
nmap <leader>n :set number!<cr>

" toggle between last two buffers
noremap <Leader><Leader> <c-^>

" allow cursor keys to go right off end of one line, onto start of next
set whichwrap+=<,>,[,]

" when joining lines, don't insert two spaces after punctuation
set nojoinspaces

" enable automatic yanking to and pasting from the selection
set clipboard+=unnamed

" make Y yank to end of line (consistent with C and D)
noremap Y y$

" I don't like folded regions
" set nofoldenable

" omit intrusive 'press ENTER' (etc) status line messages
set shortmess=atTWI

set history=999


" 'grep' command should use 'grp' bash function, a wrapper for system grep
" which adds some common flags, like --exclude-dir=\.git.
" We add '-n' into that mix, so that output is parsable by vim quickfix window.
set grepprg=grp\ -n\ $*\ /dev/null

" make commands invoked by grep go via an interactive shell
" Without this, the bash alias 'grp' in 'grpprg' is not expanded
"set shellcmdflag=-ci

" silent grep and then show results in quickfix
function! Grep(args)
    execute "silent grep " . a:args
    botright copen
endfunction

command! -nargs=* -complete=file Grep call Grep(<q-args>)

" Grep all files for the word under the cursor (& case insensitive version)
noremap <Leader>g :Ack -w '<c-r><c-w>' .<cr>
noremap <Leader>G :Ack -wi '<c-r><c-w>' .<cr>

" allow use of mouse pretty much everywhere
set mouse=a
set ttymouse=xterm2

" prevent security exploits. I never used modelines anyway.
set modelines=0

" places to look for tags files:
set tags=./tags,tags
" recursively search file's parent dirs for tags file
" set tags+=./tags;/
" recursively search cwd's parent dirs for tags file
set tags+=tags;/

" indicate a fast terminal - more redraw chars sent for smoother redraw
set ttyfast
" don't redraw while running macros
" set nolazyredraw
set lazyredraw

" turn on syntax highlighting
syntax on

" files to hide in directory listings
let g:netrw_list_hide='\.py[oc]$,\.svn/$,\.swp/$,\.git/$,\.hg/$'

filetype plugin indent on


" KEYBINDS

" move up/down by visible lines on long wrapped lines of text
" nnoremap k gk
" nnoremap j gj
vnoremap <a-4> g$
nnoremap <a-4> g$
vnoremap <a-0> g^
nnoremap <a-0> g^
nnoremap <a-6> g^
vnoremap <a-6> g^

map <C-A> <Home>
map <C-E> <End>
imap <C-A> <Home>
imap <C-E> <End>
vmap <C-A> 0
vmap <C-E> $
cmap <C-A> <Home>
cmap <C-E> <End>
map <C-F> w

" save file
noremap <silent> <c-s> :wa<cr>
inoremap <silent> <c-s> <ESC>:wa<cr>

" close buffer
noremap <c-backspace> :Bclose<cr>
noremap <c-s-backspace> :Bclose!<cr>

" navigating between windows
noremap <c-left> <c-w>h
noremap <c-right> <c-w>l
noremap <c-up> <c-w>k
noremap <c-down> <c-w>j
map! <c-left> <esc><c-left>
map! <c-right> <esc><c-right>
map! <c-up> <esc><c-up>
map! <c-down> <esc><c-down>

" make cursor keys work during visual block selection
vnoremap <left> h
vnoremap <right> l
vnoremap <up> k
vnoremap <down> j
"map <S-F12> :cp<cr>
"map <F12> :cn<cr>

" nmap <S-CR> O<Esc>j
" show vim in window title
set title

set colorcolumn=80
set linebreak
set nu
set relativenumber
set splitbelow                  " Split windows at bottom
set splitright

" Highlight
highlight clear SpellBad
highlight SpellBad term=standout ctermfg=15 ctermbg=1 guifg=White guibg=Red
highlight clear MatchParen
highlight MatchParen term=standout ctermfg=Red
set nolist!

" NERDTree
let NERDTreeIgnore = ['\.pyc$', '__pycache__']
" let g:NERDTreeMapPreview="<CR>"
let g:NERDTreeMapPreviewVSplit="<TAB>"
let g:NERDTreeMapPreviewSplit="<S-TAB>"
let g:NERDTreeWinSize = 40
let NERDTreeQuitOnOpen=1
" Open NERD Tree file
nnoremap <Leader>o :NERDTreeToggle<cr>


" Tagbar
nmap <F4> :TagbarOpenAutoClose<CR>

" Tabs
nmap <c-n> :tabnew<CR>
nmap <F6> :tabnext<CR>
nmap <s-F6> :tabprevious<CR>

" Airline
set laststatus=2
let g:airline#extensions#tagbar#enabled = 0

" Buffers
nnoremap <Leader>b :CtrlPBuffer<cr>
nnoremap <Leader>f :CtrlP<cr>
nnoremap <Leader>t :CtrlPTag<cr>
nnoremap <Leader>l :TagbarOpenAutoClose<cr>
nnoremap <Leader>L :TagbarToggle<cr>
nnoremap <Leader>c :ccl<cr>
nnoremap <Leader>k :PyFlake<cr>
nnoremap <Leader>K :PyFlakeAuto<cr>

" PyFlake
let g:PyFlakeOnWrite = 0
let g:PyFlakeCheckers = 'pep8,mccabe'
map <F11> :PyFlake<cr>
map <S-F11> :PyFlakeAuto<cr>

" Mouse fix
if has("mouse_sgr")
    set ttymouse=sgr
else
    set ttymouse=xterm2
end


" EXPERIMENTAL ARROW KEY AVOIDANCE

function! DelEmptyLineAbove()
    if line(".") == 1
        return
    endif
    let l:line = getline(line(".") - 1)
    if l:line =~ '^s*$'
        let l:colsave = col(".")
        .-1d
        silent normal! <C-y>
        call cursor(line("."), l:colsave)
    endif
endfunction

function! AddEmptyLineAbove()
    let l:scrolloffsave = &scrolloff
    " Avoid jerky scrolling with ^E at top of window
    set scrolloff=0
    call append(line(".") - 1, "")
    if winline() != winheight(0)
        silent normal! <C-e>
    endif
    let &scrolloff = l:scrolloffsave
endfunction

function! DelEmptyLineBelow()
    if line(".") == line("$")
        return
    endif
    let l:line = getline(line(".") + 1)
    if l:line =~ '^s*$'
        let l:colsave = col(".")
        .+1d
        ''
        call cursor(line("."), l:colsave)
    endif
endfunction

function! AddEmptyLineBelow()
    call append(line("."), "")
endfunction

" Arrow key remapping: Up/Dn = move line up/dn; Left/Right = indent/unindent
function! SetArrowKeysAsTextShifters()
    " normal mode
    nmap <silent> <Left> <<
    nmap <silent> <Right> >>
    nnoremap <silent> <Up> <Esc>:call DelEmptyLineAbove()<CR>
    nnoremap <silent> <S-UP> <Esc>:call AddEmptyLineAbove()<CR>k
    nnoremap <silent> <S-Down> <Esc>:call DelEmptyLineBelow()<CR>
    nnoremap <silent> <Down>  <Esc>:call AddEmptyLineAbove()<CR>
    nnoremap <silent> <C-Up> <Esc>:call DelEmptyLineBelow()<CR>
    nnoremap <silent> <C-Down> <Esc>:call AddEmptyLineBelow()<CR>

    " visual mode
    vmap <silent> <Left> <
    vmap <silent> <Right> >
    vnoremap <silent> <Up> <Esc>:call DelEmptyLineAbove()<CR>gv
    vnoremap <silent> <Down>  <Esc>:call AddEmptyLineAbove()<CR>gv
    vnoremap <silent> <C-Up> <Esc>:call DelEmptyLineBelow()<CR>gv
    vnoremap <silent> <C-Down> <Esc>:call AddEmptyLineBelow()<CR>gv

    " insert mode
    imap <silent> <Left> <C-D>
    imap <silent> <Right> <C-T>
    inoremap <silent> <Up> <Esc>:call DelEmptyLineAbove()<CR>a
    inoremap <silent> <Down> <Esc>:call AddEmptyLineAbove()<CR>a
    inoremap <silent> <C-Up> <Esc>:call DelEmptyLineBelow()<CR>a
    inoremap <silent> <C-Down> <Esc>:call AddEmptyLineBelow()<CR>a

    " disable modified versions we are not using
    "nnoremap  <S-Up>     <NOP>
    "nnoremap  <S-Down>   <NOP>
    nnoremap  <S-Left>   <NOP>
    nnoremap  <S-Right>  <NOP>
    vnoremap  <S-Up>     <NOP>
    vnoremap  <S-Down>   <NOP>
    vnoremap  <S-Left>   <NOP>
    vnoremap  <S-Right>  <NOP>

    inoremap  <S-Up>     <NOP>
    inoremap  <S-Down>   <NOP>
    inoremap  <S-Left>   <NOP>
    inoremap  <S-Right>  <NOP>
endfunction

"call SetArrowKeysAsTextShifters()

if &term =~ '^screen'
    " tmux will send xterm-style keys when its xterm-keys option is on
    execute "set <xUp>=\e[1;*A"
    execute "set <xDown>=\e[1;*B"
    execute "set <xRight>=\e[1;*C"
    execute "set <xLeft>=\e[1;*D"
endif

let g:ctrlp_max_depth=10

nnoremap <C-j> O<ESC>

" Indention colors
hi IndentGuidesOdd  ctermbg=black
hi IndentGuidesEven ctermbg=235


set modeline
set modelines=5


function! LoadLocal()
    if !empty(glob("../../.vimrc_local"))
        source ../../.vimrc_local
    endif
    if !empty(glob("../.vimrc_local"))
        source ../.vimrc_local
    endif
    if !empty(glob(".vimrc_local"))
        source .vimrc_local
    endif
endfunction

call LoadLocal()


" Spell Check
let b:myLang=0

let g:myLangList=["nospell","en","en_us","en_gb", "hu"]
function! ToggleSpell()
  if !exists( "b:myLang" )
    if &spell
      let b:myLang=index(g:myLangList, &spelllang)
    else
      let b:myLang=0
    endif
  endif
  let b:myLang=b:myLang+1
  if b:myLang>=len(g:myLangList) | let b:myLang=0 | endif
  if b:myLang==0
    setlocal nospell
  else
    execute "setlocal spell spelllang=".get(g:myLangList, b:myLang)
  endif
  echo "spell checking language:" g:myLangList[b:myLang]
endfunction


nmap <silent> <Leader>1 :call ToggleSpell()<CR>

hi User1 guifg=#eea040 guibg=#222222
hi User2 guifg=#dd3333 guibg=#222222
hi User3 guifg=#ff66ff guibg=#222222
hi User4 guifg=#a0ee40 guibg=#222222
hi User5 guifg=#eeee40 guibg=#222222

set statusline=
"set statusline +=%1*\ %n\ %*            "buffer number
"set statusline +=%5*%{&ff}%*            "file format
"set statusline +=%3*%y%*                "file type
set statusline +=%4*\ %<%F%*            "full path
set statusline +=%2*%m%*                "modified flag
set statusline +=%1*%=%5l%*             "current line
set statusline +=%2*/%L%*               "total lines
set statusline +=%1*%4v\ %*             "virtual column number
"set statusline +=%2*0x%04B\ %*          "character under cursor
"set statusline=%f\ [%l/%L]
set statusline=%f%m%=%l/%L\ (%p%%)\ %4v\ [%{&spell?&spelllang:'nospell'}]

" now set it up to change the status line based on mode
" http://vim.wikia.com/wiki/Change_statusline_color_to_show_insert_or_normal_mode
"if version >= 700
"  au InsertEnter * hi StatusLine term=reverse ctermbg=5 gui=undercurl guisp=Magenta
"  au InsertLeave * hi StatusLine term=reverse ctermfg=0 ctermbg=2 gui=bold,reverse
"endif

"ensure plug
if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

call plug#begin('~/.vim/plugged')

" Typescript syntax
Plug 'leafgarland/typescript-vim'
Plug 'yggdroot/indentline'
Plug 'mileszs/ack.vim'

call plug#end()


" Custom plugin configs
