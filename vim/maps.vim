"
"
" C-Q t  - touch log, start xterm tailing log, run current file through python; tail -f, buffer
" C-k    - next class definition
" C-A-k  - prev class definition
" ,O     - fold python comments and docstrings
"        - search python code, ignore comments and docstrings
" C-Q c  - pYchecker

"        - repeat python searchcode; Next
" K      - python help on word under cursor
" Alt-t  - :!!  Run/Repeat last shell command
" \e     - list python def / classes; functions
" ,o     - python run current buffer; file
" C-Q 1  - run python interpreter
" Alt-x  - delete buffer

" _V     - vertically split window
" C-J U  - go to a Utl link; follow
"        - fuzzy find file; edit

" Ctrl-N - cd ~/links/
" _I     - edit file in ~/.vim/ dir
" ^Tab   - Ctrl-^, previous buffer
" gx     - delete XHTML tag (if inside or on border); erase
" _M     - vim command list; cmd, open, edit, notes
" ,gs    - list of scripts; open, edit, notes

" ^P     - paste from clipboard
" _R     - list buffers and remove; delete
" ,l     - :ls - list buffers
" \n     - toggle line numbers; :nu
" _H     - helpgrep words in any order; find, search
" \z     - paste from 'z' register
" ,gh    - run helptags on vim docs dir; add
" ,y     - run buffer through python, show in preview window (c-w,z); file

" C-Q g  - django syntax highlight; html
" _U     - align equal signs or comments; code, line up
" Alt-l  - :, colon, start command mode
"        - open all folds under cursor recursively; fully, current
" Ctrl-k - cycle to next window; c-w w
" \w     - open all folds; increase, fold level, zR
" \v     - close all folds; minimize, decrease, fold level, zM
" \h     - interactive search for vim commands (vimcmds.py v)
" _J     - interactive search for django commands (vimcmds.py d)

" ,gg    - grep word under cursor in current file (,G same but type pattern)
" k+/-   - next/prev quickfix error (+ctrl first/last), k* - focus curr. error
" C-Q z  - fold everything but the search pattern; find, all
" C-J P  - run python on current file; execute
" _Q     - insert quote signature; email, add, random, quotation
" \2     - toggle colour mode, hide comments, strings; color


"        - manual folding
" ,gx    - sync fromstart; fix syntax, highlight
" C-a    - interactive vim command help; mappings, find
" Alt-z  - python folding
" Alt-g  - find specific python def by pattern; function, search
" ,0     - find specific python class by pattern; search
" Alt-e  - next python def; function
" C-A-e  - previous python def; function
"
" gl     - insert empty line below (gL above); add, blank
"
" Enter  - /tmp/zsh keep and run current line; execute
" D      - /tmp/zsh delete short lines
"
" \r     - remote edit settings, no swap file, only complete in current file
" gc     - cd to current file's directory; cwd, pwd
"
"
" gy     - python notes; open, edit, outlines
" C-Q v  - edit vimrc
" Alt-)  - edit maps.vim; mappings, commands
" \m     - edit finance text file; open, notes, balance, expenses
"
" _L     - ls current working directory; show, list, !ls
" Alt+op - window smaller/larger; increase, decrease
"
"        - toggle fold manual/indent
" _N     - Toggle NERDTree file browser
" Alt-j/k - move current line down/up
" Y      - yank to the end of current line; copy
" Space  - Go to screen line number; refresh
" m-i    - hide current buffer
" \t     - del trailing spaces in current file
" ,w , c-s - write buffer to disk; save
" \s     - source current file; :so, buffer
" ,q     - :q, quit vim
" Alt-H  - help
"
" gl     - add a blank line below current; insert, make, empty
" C-Q x  - syntax on; :sy on
" ,f, m-f - toggle fold under cursor; za
" Alt-m/n - make vim window smaller / larger; increase, decrease
" Alt-d  - delete current line; dd, erase
" _B     - backup current file; bkup.py
" \d     - duplicate line; copy
" \a     - email signature; andrei
" m-c    - :cd
" \u     - :cd .. , cd one directory level up
" Ctrl-h - previous window; c-w P, back (DISABLED, NOW next window)
" Alt-q  - format current paragraph; gqip
" _X     - maXimize current window; increase, size
" \o     - set gui font size; character
" Alt-v  - edit file; :e, load
"        - fix cursorline highlight color
" \5     - open todo list win; wtodo, buffer
" ga     - switch to window above; up
" ,k     - del buffer, keep window layout; rm, remove, bdelete
" Q      - @q, run 'q' register, after qq command
" _d     - delete line without saving to unnamed register; erase
" zff    - fold python defs and classes; outline
" \j     - project, switch to left window (usually vimject)
" _W     - :wqa, write all buffers and quit; exit, save
" gs     - vimp3 status
" g9     - django notes, outline
" \av    - email signature with vim pysuite links DISABLED
" \ad    - email signature with django by example links DISABLED
" g3     - edit lst.todo; buffer, list
" [[     - edit main.trak; tracking, project, buffer
" C-J a  - ToggleAcp, toggle auto complete popup; disable, enable
" g6     - delete line above; dd, erase, up
" c-tab  - toggle pseudo code outline view; pcotl
" ,gq    - find next single-quoted string
" ,b     - remind rare commands; list, cmds
" ,t     - filelist, files, edit
" ,1     - insert highlight symbol, prepend, 1, one
" ,2     - insert highlight symbol, prepend, 2, two
" ,9     - visual select pasted; highlight
" C-J T  - show current trak time; display, project, timesheet
" ,,     - top of screen and scroll down; zt
" ,4     - switch to buffer with models.py; edit, change, django
" ,5     - switch to buffer with views.py; edit, change, django
" F3     - go to brackets at the end; )), ]], find
" _"     - expand single line docstring to multi-line; convert, python
" \3     - close all folds except for current
" ]e     - make session, mksession; write, save
" _E     - make default session, mksession; write, save to def-session file
" dD     - delete back to comma; arg
" ,gw    - toggle wrap setting; invwrap, invert
" C-j o  - only current window, close all other windows except for special ones (in pysuite.vim)
" C-j l  - fold to level given as count;
" C-j m  - reminders; (in pysuite.vim)
" ,gf    - factor out function; refactor function call line into def with return line
" Alt-0  - insert one char; single
" C-J h  - remove html tags from current line, strip, delete; H remove from all lines
" C-J i  - toggle virtual edit off | none | all
" C-J l  - delete surrounding function; remove
" C-J s  - delete vim swap file after restoring; remove
" C-J >  - align indent of lines below current; < for lines above; fix
" C-J n  - visually select current python function; method
" C-J e  - execute current line in command line; cmd, run, copy
" C-J x  - toggle between X append mode / regular yank; x register
" C-Q d  - mark buffers in scratch window and :bdelete selected; multiple, bulk
" \1     - set foldlevel to 1
" gb     - enter insert on next line and backspace; indent, level
" Alt-x  - alt-tab, ctrl-R to reload browser; chrome, refresh
" F2     - multiply by 30 percent; 30%, add
" N C-J L - set foldlevel to N
" gn      - find next capital letter or underscore; _, camel; gN for previous
" Alt-s   - split window horizontally
" F9      - increase font size; larger, gui
" S-F9    - decrease font size; smaller, gui
" F1      - open practice outline file; go, edit
" [t      - add a todo item; new, (pysuite)
" \c      - toggle conceal level 1/2; hide
" [s      - open scratch buffer; edit, new
" F10     - current syntax highlight group
" ,2      - switch to last python file; go, buffer
" ,3      - switch to last html file; go, buffer
" \q      - solarized color scheme, set background to dark; bg
" \g      - edit logs potl file, outline, open
" [f      - add print statement with current python function; debug, insert
" ,.      - convert comment to sentence; capitalize, period
" [S      - remove leading and trailing single space in a docstring; delete, python
" [M      - meditation setup buffer, nofile, scratch, double spaced
" [c      - search for class, find class name
" _O      - edit notes
" _A      - fix camelcase variable names to snakecase; change, replace
" ]f      - search for def or class under cursor; find, python, function
"
"endlist
"===============================================================================================
" abcdefghijklmnopqrstuvwxyz
" F     - F2
" Ctrl  - k
" Alt   - b s
" ,     - b i h  1 6 7
" g     - 1 4 5 7 n x z  (gz something with folding?!)
" \     - a x  \ 0 4 6 7 9
" _     - A E K, 012345679, _
" [     - / [ ]   a b d g h i j k l m n o p q r u v w x y       A B E F G H I J K L M N O P Q R T U V W X Y
" ]     - / [ ]   a b e g h i j k l m n o p q r t u v w x y   A B E F G H I J K L M N O P Q R S T U V W X Y
"
" Available after ,g    - a b g i j t u x z  ABCDEFGHIJKLMNOPQRTUVWXYZ [and some others...]

" Fix camelcase
nnoremap _A :%s/\(\l\)\(\u\)/\1\_\l\2/g

nnoremap ]f m':exe '/^\s*\(def\\|class\) ' . expand('<cword>') \| <cr>

command! DiffOrig vert new | set bt=nofile | r # | 0d_ | diffthis | wincmd p | diffthis

nnoremap _O :e ~/docs/notes.potl<CR>

nnoremap [M :set buftype=nofile<cr>:inoremap \<lt>cr> \<lt>cr>\<lt>cr><cr>
nnoremap [S ^f x$BX
nnoremap ,. ^w~A.<esc>
" add print statement with current py function:  ml ?^\s*def <cr> 2w yt( 'l O print "in <c-r>"()" <esc>
nnoremap [f ml?^\s*def <cr>2wyt('lOprint "in <c-r>"()"<esc>
nnoremap \g :e ~/docs/logs.potl<cr>
nnoremap \q :colo solarized<cr>:set bg=dark<cr>
nnoremap zc zC
nnoremap ]e :mksession! ~/.vim/session<CR>
nnoremap _E :mksession! ~/.vim/def-session<CR>
nnoremap <c-e> @="3\<lt>c-e>"<CR>
nnoremap <c-y> @="3\<lt>c-y>"<CR>
nnoremap - zC
nnoremap [s :new<cr>:set buftype=nofile<cr><c-w>6-i
nnoremap [' ^gUli"""<esc>$a."""<esc>
nnoremap <a-c-a> <c-a>
nnoremap \c :exe ":set cole=" . ((&cole) ? 0 : 1)<CR>
nmap zo zO
nnoremap [a f<
nnoremap ]a F<
nnoremap <m-s> <c-w>S
nnoremap gn :call SubWord(0)<cr>
nnoremap gN :call SubWord(1)<cr>
nnoremap <m-x> :w<cr>:call ReloadChrome()<cr>
nnoremap gb o<bs>
nnoremap \1 :call FoldLevel1()<cr>
nnoremap $ :<c-u>call EndOfLine()<cr>
nnoremap _I :e ~/.vim/
nmap <c-j>l ds)db
nnoremap <c-j>e 0y$:<c-r>"<cr>
nnoremap <c-j>i :call ToggleVE()<cr>
nnoremap <c-j>h :s#<[^>]\+>##g<cr>
nnoremap <c-j>H :%s#<[^>]\+>##g<cr>

" current syn group
map <F10> :echo "hi<" . synIDattr(synID(line("."),col("."),1),"name") . '> trans<'
    \ . synIDattr(synID(line("."),col("."),0),"name") . "> lo<"
    \ . synIDattr(synIDtrans(synID(line("."),col("."),1)),"name") . ">"<CR>

nnoremap <down> 8<c-e>
nnoremap <up> 8<c-y>
nnoremap <Leader>gw :set invwrap<CR>
nnoremap \3 zMzozozo
nnoremap _" ^2f"a <esc>f"i<cr><cr><cr><up><up><esc>0DjA<tab>
nnoremap _' a<cr><tab><esc>f"i<cr><esc><<2k^2f"a <esc>
nnoremap <c-j>) /)\+$\\|]\+$\\|$/s-1<CR>:nohl<CR>
vnoremap <c-j>) /)\+$\\|]\+$\\|$/s-1<CR><esc>:nohl<CR>gv

nnoremap dD dF,
nnoremap ,4 :b models.py<CR>
nnoremap ,5 :b views.py<CR>
nnoremap <c-j>T :call Trak("calc_current")<CR>|    " trak current total
nnoremap ,9 V']|                               " visual select last pasted lines

nnoremap <Leader>gq /'[-0-9a-zA-Z_%()/. ]\{2,999\}'<CR>|    " next single-quoted string
nnoremap <c-tab> :call Pcotl()<CR>|                         " toggle pseudo-code outline
nnoremap g9 :e ~/docs/django.potl<CR>|                      " django notes
nnoremap g3 :e ~/docs/lst.todo<CR>|                         " todo list
nnoremap <m-r> :e ~/docs/main.trak<CR>|                     " project trak
nnoremap <F1> :e ~/docs/practice.potl<CR>|                  " practice outline file
nnoremap <c-j>a :call ToggleAcp()<CR>|                      " toggle AutoCompPopup
nnoremap g6 kdd|                                            " delete line above
nnoremap \2 :call ToggleColorMode()<CR>|                    " toggle color mode

nnoremap _Q :r!~/mypython/sig.py<CR>|                     " insert random signature
nnoremap _d "_dd|                                         " delete line into blank register
vnoremap _d "_dd|
nnoremap <Leader>gs :e ~/win-projects/scripts.txt<CR>|    " scripts list file
nnoremap ,gx :syntax sync fromstart<CR>|                  " sync syntax from start
nnoremap ,o :!python "%"<CR>|                         " run current file through python

nnoremap <c-j>< :FixIndentUp<CR>
nnoremap <c-j>> :FixIndentDown<CR>
nnoremap _W :wqa<CR>
nnoremap zff :/^\s*class\s\\|^\s*function\s\\|^\s*def\s/<CR>:setlocal foldexpr=getline(v:lnum)!~@/ foldmethod=expr foldlevel=0 foldcolumn=1<CR><CR>:nohl<CR>
nnoremap <silent> <c-q>z :setlocal foldexpr=getline(v:lnum)!~@/ foldlevel=0 foldcolumn=0 foldmethod=expr<CR>
nnoremap Q @q
nnoremap _U :AlignCode<CR>

nnoremap <c-q>g :set ft=htmldjango<CR>
nnoremap <Leader>y :RunPyBuffer<CR>
nnoremap <Leader>gh :helptags ~/.vim/doc/<CR>
nnoremap \z "zP
nnoremap _H :call HelpGrep()<cr>
nnoremap \o :set guifont=Inconsolata\ Medium\ 
nnoremap \w zR
nnoremap \v zM
nnoremap <c-q>t :!touch log<CR><CR>:!xterm -e 'tail -f log'&<CR><CR>:!python %  >>log<left><left><left><left><left><left>

nnoremap <Leader>w :write<CR>
nnoremap <c-q>v :e ~/.vimrc<CR>
nnoremap <Leader>e ?^\s*def <CR>:nohls<CR>
vnoremap <Leader>e ?^\s*def <CR><ESC>:nohls<CR>gv

nnoremap <Leader>k /^class<CR>:nohls<CR>
nnoremap \k ?^class<CR>:nohls<CR>
vnoremap <Leader>k /^class<CR><ESC>:nohls<CR>gv
vnoremap \k ?^class<CR><ESC>:nohls<CR>gv
nnoremap \n :set invnu<CR>
nnoremap \t :%s/\s\+$//g<CR>:nohls<CR>

nnoremap <c-q>1 :!ipython -colors NoColor<CR>
nnoremap _V :vertical split<CR>
nnoremap _N :NERDTreeToggle<CR>:set columns=132<CR>
nnoremap \e :r!grep '^[ ]*\(def\\|class\)' %
nnoremap <m-c-p> "+[p
nnoremap \s :w<CR>:so %<CR>
nnoremap _R :ls<CR>:bd 
nnoremap <Leader>l :ls<CR>:b 
nnoremap \r :set noswf<CR>:set cpt=.<CR>

nnoremap <c-j>U :Utl<CR>
nnoremap <2-LeftMouse> :Utl ol<cr>
nnoremap gc :lchdir %:p:h<CR>:pwd<CR>
nnoremap <Leader>gg :exe 'vimgrep '.expand('<cword>').' '.expand('%') \| :copen \| :cc<CR>
nnoremap <Leader>G :exe 'vimgrep  '.expand('%') \| :copen \| :cc
nnoremap Y y$
nnoremap j :<c-u>call DownUp('j')<cr>
nnoremap k :<c-u>call DownUp('k')<cr>

nnoremap ,, zt5<c-y>|      " zt then scroll 5 lines up
nnoremap _M :e ~/.vim/vimnotes.potl<CR>
nnoremap <Leader>F :set ft=txtfmt.
nnoremap <c-q>c :!pychecker --limit 100 %<CR>
nnoremap <Leader>O :call Pdocfold()<CR>
nnoremap <Leader>q :q<CR>


nnoremap gl :AddLine<CR>
nnoremap gL :AddLineAbove<CR>
command! AddLine s/$/\r/ | :nohl | normal k
command! AddLineAbove exe "normal k" | :s/$/\r/ | :nohl | exe "normal j"
nnoremap _L :!ls<CR>
nnoremap <Leader>t :e ~/.vim/filelist<CR>
nnoremap gy :e ~/docs/python.potl<CR>
nnoremap \m :e ~/docs/balance.fin<CR>

" call motpat#Map(0, 'w', 'b', '\i\+\ze.\|$')   " moved to after/

nnoremap <kPlus>     :cnext<CR>
nnoremap <kMinus>    :cprev<CR>
nnoremap <kMultiply> :cc<CR>
nnoremap <c-kPlus>   :clast<CR>
nnoremap <c-kMinus>  :cfirst<CR>
nnoremap <m-kPlus>   :cnewer<CR>
nnoremap <m-kMinus>  :colder<CR>

nnoremap <c-q>x :syntax on<CR>
nnoremap <M-f> za
nnoremap _B :!bkup.py %<CR>
nnoremap \d yyp

nnoremap \u :cd ..<cr>
nnoremap \h :!python ~/mypython/ifilter.py v<CR><CR>
nnoremap _J :!python ~/mypython/ifilter.py d<CR><CR>
nnoremap ga <c-w>k
nnoremap _X <c-w>_
nnoremap \j <c-w>h
nnoremap <c-down> j<c-e>
nnoremap <c-up> k<c-y>

nnoremap <c-s> :write<CR>
" nnoremap <c-p> "+gp
nnoremap <c-n> :cd ~/links/
nnoremap <silent> <C-l> :set invhlsearch<CR><C-l>
nnoremap <c-a> :!python ~/mypython/ifilter.py<CR><CR>
nnoremap <c-h> :call NextWin()<CR>

nnoremap <M-)> :e ~/.vim/maps.vim<CR>
nnoremap <M-,> :call Jump(1)<CR>
nnoremap <M-.> :call Jump(2)<CR>
nnoremap <M-/> :call Jump(3)<CR>

nnoremap <M-c> :cd 
nnoremap <M-d> dd
nnoremap <M-e> /^\s*def <CR>:nohls<CR>
vnoremap <M-e> /^\s*def <CR><ESC>:nohls<CR>gv
nnoremap <C-m-e> ?^\s*def <CR>:nohls<CR>
vnoremap <C-m-e> ?^\s*def <CR><ESC>:nohls<CR>gv
nnoremap <c-k> /^class<CR>:nohls<CR>
nnoremap <c-m-k> ?^class<CR>:nohls<CR>

nnoremap <M-g> /^\s*def 
nnoremap [c /^\s*class 
nnoremap <Leader>0 /^\s*class 
nnoremap <M-h> :help 
nnoremap <M-i> :hide<cr>
nnoremap <M-j> :call MoveLine(1)<cr>
nnoremap <M-k> :call MoveLine(0)<cr>
nnoremap <M-l> :
nnoremap <M-m> <c-w>2+
nnoremap <M-n> <c-w>2-
nnoremap <M-o> :call Resize(0)<CR>
nnoremap <M-p> :call Resize(1)<CR>
nnoremap <M-q> gqip
nnoremap <M-t> :w<CR>:!<up><CR><CR>
nnoremap <M-v> :e 
nnoremap <M-z> :setlocal foldmethod=expr foldexpr=GetPythonFoldBest(v:lnum) foldtext=PyFoldText()
        \ <CR>:call ToggleFold()<CR>gg

nnoremap <m-b> <c-b>
nnoremap <m-s> <c-f>

""
" nmap <Leader>gl :sp<CR>:sp<CR><c-w>jg3:setlocal winfixheight<CR>5<c-w>_<c-w>j
"     \ g4:setlocal winfixheight<CR>4<c-w>_
" nmap \5 :sp<CR>:sp<CR><c-w>jg3:setlocal winfixheight<CR>5<c-w>_
" nnoremap ,4 :s,\v(\w+)(\W*%#\W*)(\w+),\3\2\1\r,kgJ:nohl<CR>
" nnoremap ,1 i˙<esc>l|                          " insert highlight char 1
" nnoremap ,2 iˑ<esc>l|                          " insert highlight char 2
" nnoremap <Leader>gw :set winfixwidth<CR>
" nnoremap \1 :call Pcotl()<CR>|                              " toggle pseudo-code outline

" nnoremap _O :call ToggleFold(1)<CR>
" nnoremap g1 :hi CursorLine  guibg=grey30<CR>
" nnoremap <Leader>i :call ToggleFold()<CR>
" nnoremap _F :FufFile<CR>
" nnoremap <Leader>/ :call SearchCode()<CR>
" nnoremap . .`[|  " interferes with repeat.vim

" nnoremap <esc>0 :e ~/.vim/maps.vim<CR>
" nnoremap <esc>. :cd ..<CR>

" nnoremap <esc>, :call Jump(1)<CR>
" nnoremap <esc>. :call Jump(2)<CR>
" nnoremap <esc>/ :call Jump(3)<CR>

" nnoremap <esc>c :cd 
" nmap <esc>d dd
" nnoremap <esc>e /^\s*def<CR>:nohls<CR>
" nnoremap <esc>f za
" nnoremap <esc>g /^\s*def 
" nnoremap <esc>h :help 
" nnoremap <esc>i :hide<cr>
" nnoremap <esc>j mz:m+<CR>`z==
" nnoremap <esc>k mz:m-2<CR>`z==
" nnoremap <esc>l :
" nnoremap <esc>m <c-w>2+
" nnoremap <esc>n <c-w>2-
" nnoremap <esc>o :call Resize(0)<CR>
" nnoremap <esc>p :call Resize(1)<CR>
" nnoremap <esc>q gqip
" nnoremap <esc>r :ls<CR>:b 
" nnoremap <esc>s :!ls<CR>
" nnoremap <esc>t :w<CR>:!<up><CR><CR>
" nnoremap <esc>v :e 
" nnoremap <esc>x :bd<CR>
" nnoremap <esc>z :set foldmethod=expr \| :set foldexpr=GetPythonFoldBest(v:lnum)<CR>:call ToggleFold()<CR>
