"
"

" C-Q t  - touch log, start xterm tailing log, run current file through python; tail -f, buffer
" C-Q c  - pYchecker
" C-Q 1  - run python interpreter
" C-Q g  - django syntax highlight; html
" C-Q z  - fold everything but the search pattern; find, all
" C-Q v  - edit vimrc
" C-Q x  - syntax on; :sy on
" C-Q n  - remind normal maps, nmap, shortcuts
" C-Q i  - remind insert maps, imap, shortcuts
" C-Q o  - remind other, shortcuts

" C-k    - next class definition
" C-A-k  - prev class definition
" Ctrl-k - cycle to next window; c-w w
" C-a    - interactive vim command help; mappings, find
" C-A-e  - previous python def; function
" Ctrl-h - next window, switch

" C-J p  - run python on current file; execute
" C-J u  - go to a Utl link; follow
" C-J a  - ToggleAcp, toggle auto complete popup; disable, enable
" C-J t  - show current trak time; display, project, timesheet
" C-J o  - only current window, close all other windows except for special ones (in pysuite.vim)
" C-J l  - fold to level given as count;
" C-J m  - reminders; (in pysuite.vim)
" C-J h  - remove html tags from current line, strip, delete; H remove from all lines
" C-J i  - toggle virtual edit off | none | all
" C-J l  - delete surrounding function; remove
" C-J s  - delete vim swap file after restoring; remove
" C-J >  - align indent of lines below current; < for lines above; fix
" C-J n  - visually select current python function; method
" C-J e  - execute current line in command line; cmd, run, copy
" N C-J l - set foldlevel to N

" C-tab  - toggle pseudo code outline view; pcotl
" C-P    - paste from clipboard
"
" ,o     - python run current buffer; file
" ,i     - cd ~/links/
" ,gs    - list of scripts; open, edit, notes
" ,gh    - run helptags on vim docs dir; add
" ,gx    - sync fromstart; fix syntax, highlight
" ,0     - find specific python class by pattern; search
" ,q     - :q, quit vim
" ,gq    - find next single-quoted string
" ,b     - remind rare commands; list, cmds
" ,t     - filelist, files, edit
" ,9     - visual select pasted; highlight
" ,f     - helpgrep words in any order; find, search
" ,l     - align equal signs or comments; code, line up
" ,,     - top of screen and scroll down; zt
" ,4     - switch to buffer with models.py; edit, change, django
" ,5     - switch to buffer with views.py; edit, change, django
" ,gw    - toggle wrap setting; invwrap, invert
" ,2      - switch to last python file; go, buffer
" ,3      - switch to last html file; go, buffer
" ,.      - convert comment to sentence; capitalize, period
" ,h      - invert hlsearch; toggle, highlight
" ,O     - fold python comments and docstrings
" ,w , c-s - write buffer to disk; save

" Alt-f  - toggle fold under cursor; za
" Alt-r  - mark buffers in scratch window and :bdelete selected; multiple, bulk, remove
" Alt-x  - delete buffer
" Alt-w  - window resize mode, using h and l keys
" Alt-l  - :, colon, start command mode
" Alt-b  - del buffer, keep window layout; rm, remove, bdelete, close
" Alt-z  - python folding
" Alt-g  - find specific python def by pattern; function, search
" Alt-e  - next python def; function
" Alt-i  - grep word under cursor in current file (,G same but type pattern), cword
" Alt-h  - help
" Alt-d  - delete current line; dd, erase
" Alt-q  - format current paragraph; gqip
" Alt-v  - edit file; :e, load
" Alt-0  - insert one char; single
" Alt-x  - alt-tab, ctrl-R to reload browser; chrome, refresh
" Alt-s   - split window horizontally
" Alt-c  - :cd
" Alt-)  - edit maps.vim; mappings, commands
" Alt-p  - list python def / classes; functions
" Alt-o  - edit file in ~/.vim/ dir
" Alt-j/k - move current line down/up

" \z     - paste from 'z' register
" \w     - open all folds; increase, fold level, zR
" \v     - close all folds; minimize, decrease, fold level, zM
" \h     - interactive search for vim commands (vimcmds.py v)
" \2     - toggle colour mode, hide comments, strings; color
" \m     - edit finance text file; open, notes, balance, expenses
" \t     - del trailing spaces in current file
" \s     - source current file; :so, buffer (only .vim)
" \d     - duplicate line; copy
" \a     - email signature; andrei (only in emails)
" \u     - :cd .. , cd one directory level up
" \5     - open todo list win; wtodo, buffer
" \j     - project, switch to left window (usually vimject)
" \av    - email signature with vim pysuite links DISABLED
" \ad    - email signature with django by example links DISABLED
" \3     - close all folds except for current
" \1     - set foldlevel to 1
" \c      - toggle conceal level 1/2; hide
" \g      - edit logs potl file, outline, open
" \x     - :wqa, write all buffers and quit; exit, save
" \s S   - change between 4 line if else block and 1 line; single, one, convert, expand

" _V     - vertically split window
" _M     - vim command list; cmd, open, edit, notes
" _R     - list buffers and remove; delete
" _J     - interactive search for django commands (vimcmds.py d)
" _S     - :ls - list buffers
" _Q     - insert quote signature; email, add, random, quotation
" _L     - ls current working directory; show, list, !ls
" _B     - backup current file; bkup.py
" _X     - maXimize current window; increase, size
" _d     - delete line without saving to unnamed register; erase
" _"     - expand single line docstring to multi-line; convert, python
" _E     - make default session, mksession; write, save to def-session file
" _O      - edit notes
" _A      - fix camelcase variable names to snakecase; change, replace

" [P      - multiply by X percent; 20% default, add
" [O      - solarized color scheme, set background to dark; bg
" [N     - toggle line numbers; :nu
" [F     - set gui font size; character
" [P     - run buffer through python, show in preview window (c-w,z); file
" [A     - :!!  Run/Repeat last shell command
" [R      - remote edit settings, no swap file, only complete in current file
" [t      - add a todo item; new, (pysuite)
" [s      - open scratch buffer; edit, new
" [f      - add print statement with current python function; debug, insert
" [S      - remove leading and trailing single space in a docstring; delete, python
" [M      - meditation setup buffer, nofile, scratch, double spaced
" [c      - search for class, find class name
"
" ]t     - edit main.trak; tracking, project, buffer
" ]e     - make session, mksession; write, save
" ]f      - search for def or class under cursor; find, python, function, cword
" ]s      - global replace word under cursor; substitute, cword, replace

" gn      - find next capital letter or underscore; _, camel; gN for previous
" gx     - toggle between X append mode / regular yank; x register (pysuite.vim)
" gl     - insert empty line below (gL above); add, blank
" gc     - cd to current file's directory; cwd, pwd
" gy     - python notes; open, edit, outlines
" gl     - add a blank line below current; insert, make, empty
" g9     - django notes, outline
" g3     - edit lst.todo; buffer, list
" g6     - delete line above; dd, erase, up
" gb     - enter insert on next line and backspace; indent, level
"
" K      - python help on word under cursor, cword
" Enter  - /tmp/zsh keep and run current line; execute
" D      - /tmp/zsh delete short lines
" Y      - yank to the end of current line; copy
" Space  - Go to screen line number; refresh
" Q      - @q, run 'q' register, after qq command
" zff    - fold python defs and classes; outline
" dD     - delete back to comma; arg
" k+/-   - next/prev quickfix error (+ctrl first/last), k* - focus curr. error

" F1      - open practice outline file; go, edit
" F3     - go to brackets at the end; )), ]], find
" F9      - increase font size; larger, gui
" S-F9    - decrease font size; smaller, gui
" F10     - current syntax highlight group

"         - make vim window smaller / larger; increase, decrease
"        - window smaller/larger; increase, decrease
"        - fix cursorline highlight color
"        - vimp3 status
"        - switch to window above; up
"        - toggle fold manual/indent
"        - search python code, ignore comments and docstrings
"        - repeat python searchcode; Next
"        - fuzzy find file; edit
"        - open all folds under cursor recursively; fully, current, cword
"        - manual folding
"        - hide current buffer
"
"endlist
"===============================================================================================
" abcdefghijklmnopqrstuvwxyz
" F     - 2
" Ctrl  - n
" Alt   - m n t
" ,     - b k y  1 6 7
" g     - a s n z  1 4 5 7  (gz something with folding?!)
" \     - a e n o r  \ 0 4 6 7 9
" _     - A E K N S W, 012345679, _
" [     - / [ ]   a b d g h i j k l m n o p q r u v w x y       A B E F G H I J K L M N Q R T U V W X Y
" ]     - / [ ]   a b e g h i j k l m n o p q r t u v w x y   A B E F G H I J K L M N O P Q R S T U V W X Y
"
" Available after ,g    - a b g i j t u x z  ABCDEFGHIJKLMNOPQRTUVWXYZ [and some others...]

nnoremap \s ^daWk$xkk$xjddkP<<JJJ
nnoremap \S ^/if<cr>hs<cr><esc>/else<cr>hs<cr><esc>ea:<cr><esc>kkA:<esc>kddp>>2yaWjjP
nnoremap <m-i> :call GrepQuickFixToggle()<CR>

command! -count=1 Go :call GotoLine(<count>)
nnoremap <silent> <Space> :<C-U>exe ":Go" . v:count1<cr>

nnoremap <m-w> :call WinSizeMode()<CR>
nnoremap ,h :set invhlsearch<cr>
nnoremap ]s yiw:%s/<c-r>"/<c-r>"/g<left><left>

" Fix camelcase
nnoremap _A :%s/\(\l\)\(\u\)/\1\_\l\2/g

nnoremap ]f m':call search('^\s*\(def\\|class\) ' . expand('<cword>'), 'ws')<cr>

command! DiffOrig vert new | set bt=nofile | r # | 0d_ | diffthis | wincmd p | diffthis

nnoremap _O :e ~/docs/notes.potl<CR>

nnoremap [M :set buftype=nofile<cr>:inoremap \<lt>cr> \<lt>cr>\<lt>cr><cr>
nnoremap [S ^f x$BX
nnoremap ,. ^w~A.<esc>
" add print statement with current py function:  ml ?^\s*def <cr> 2w yt( 'l O print "in <c-r>"()" <esc>
nnoremap [f ml?^\s*def <cr>2wyt('lOprint "in <c-r>"()"<esc>
nnoremap \g :e ~/docs/logs.potl<cr>
nnoremap [O :colo solarized<cr>:set bg=dark<cr>
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
nnoremap <m-o> :e ~/.vim/
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
" nnoremap ,4 :b models.py<CR>
" nnoremap ,5 :b views.py<CR>
nnoremap <c-j>T :call Trak("calc_current")<CR>|    " trak current total
nnoremap ,9 V']|                               " visual select last pasted lines

nnoremap <Leader>gq /'[-0-9a-zA-Z_%()/. ]\{2,999\}'<CR>|    " next single-quoted string
nnoremap <c-tab> :call Pcotl()<CR>|                         " toggle pseudo-code outline
nnoremap g9 :e ~/docs/django.potl<CR>|                      " django notes
nnoremap g3 :e ~/docs/lst.todo<CR>|                         " todo list
nnoremap ]t :e ~/docs/main.trak<CR>|                        " project trak
nnoremap <F1> :e ~/docs/practice.potl<CR>|                  " practice outline file
nnoremap <c-j>a :call ToggleAcp()<CR>|                      " toggle AutoCompPopup
nnoremap g6 kdd|                                            " delete line above
nnoremap \2 :call ToggleColorMode()<CR>|                    " toggle color mode

nnoremap _Q :r!~/mypython/sig.py<CR>|                     " insert random signature
nnoremap _d "_dd|                                         " delete line into blank register
vnoremap _d "_dd|
nnoremap <Leader>gs :e ~/win-projects/scripts.txt<CR>|    " scripts list file
nnoremap ,gx :syntax sync fromstart<CR>|                  " sync syntax from start
nnoremap ,o :!python3 "%"<CR>|                         " run current file through python

nnoremap <c-j>< :FixIndentUp<CR>
nnoremap <c-j>> :FixIndentDown<CR>
nnoremap \x :wqa<CR>
nnoremap zff :/^\s*class\s\\|^\s*function\s\\|^\s*def\s/<CR>:setlocal foldexpr=getline(v:lnum)!~@/ foldmethod=expr foldlevel=0 foldcolumn=1<CR><CR>:nohl<CR>
nnoremap <silent> <c-q>z :setlocal foldexpr=getline(v:lnum)!~@/ foldlevel=0 foldcolumn=0 foldmethod=expr<CR>
nnoremap Q @q
nnoremap ,l :AlignCode<CR>

nnoremap <c-q>g :set ft=htmldjango<CR>
nnoremap [P :RunPyBuffer<CR>
nnoremap <Leader>gh :helptags ~/.vim/doc/<CR>
nnoremap \z "zP
nnoremap ,f :call HelpGrep()<cr>
nnoremap [F :set guifont=Inconsolata\ Medium\ 
nnoremap \w zR
nnoremap \v zM
nnoremap <c-q>t :!touch log<CR><CR>:!xterm -e 'tail -f log'&<CR><CR>:!python %  >>log<left><left><left><left><left><left>

nnoremap <Leader>w :write<CR>
nnoremap <c-q>v :e ~/.vimrc<CR>
nnoremap <Leader>e ?^\s*def <CR>:nohls<CR>
vnoremap <Leader>e ?^\s*def <CR><ESC>:nohls<CR>gv

nnoremap \k ?^class<CR>:nohls<CR>
vnoremap <Leader>k /^class<CR><ESC>:nohls<CR>gv
vnoremap \k ?^class<CR><ESC>:nohls<CR>gv
nnoremap [N :set invnu<CR>
nnoremap \t :%s/\s\+$//g<CR>:nohls<CR>

nnoremap <c-q>1 :!ipython -colors NoColor<CR>
nnoremap _V :vertical split<CR>
" nnoremap _N :NERDTreeToggle<CR>:set columns=132<CR>
" nnoremap \e :r!grep '^[ ]*\(def\\|class\)' %
nnoremap <m-c-p> "+[p
nnoremap _R :ls<CR>:bd 
nnoremap _S :ls<CR>:b 
nnoremap [R :set noswf<CR>:set cpt=.<CR>

nnoremap <c-j>U :Utl<CR>
nnoremap <2-LeftMouse> :Utl ol<cr>
nnoremap gc :lchdir %:p:h<CR>:pwd<CR>
nnoremap <m-i> :exe 'vimgrep '.expand('<cword>').' '.expand('%') \| :copen \| :cc<CR>
nnoremap <Leader>G :exe 'vimgrep  '.expand('%') \| :copen \| :cc
nnoremap Y y$
nnoremap j :<c-u>call DownUp('j')<cr>
nnoremap k :<c-u>call DownUp('k')<cr>

nnoremap ,, zt5<c-y>kj|      " zt then scroll 5 lines up; kj to update line numbers
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
nnoremap _X <c-w>_
nnoremap \j <c-w>h
nnoremap <c-down> j<c-e>
nnoremap <c-up> k<c-y>

nnoremap <c-s> :write<CR>
" nnoremap ga <c-w>k
" nnoremap <c-p> "+gp
" nnoremap <silent> <C-l> :set invhlsearch<CR><C-l>
nnoremap ,i :cd ~/links/
nnoremap <c-a> :!python ~/mypython/ifilter.py<CR><CR>
nnoremap <c-h> :call NextWin()<CR>

nnoremap <M-)> :edit ~/.vim/maps.vim<CR>
nnoremap <C-Q>n :edit ~/docs/map-remind<CR>
nnoremap <C-Q>i :edit ~/docs/imap-remind<CR>
nnoremap <C-Q>o :edit ~/docs/other-remind<CR>

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

nnoremap <M-g> /^\s*\(def\\|class\) 
nnoremap [c /^\s*class 
nnoremap <Leader>0 /^\s*class 
nnoremap <M-h> :help 
" nnoremap <M-i> :hide<cr>
nnoremap <M-j> :call MoveLine(1)<cr>
nnoremap <M-k> :call MoveLine(0)<cr>
nnoremap <M-l> :
" nnoremap <M-m> <c-w>2+
" nnoremap <M-n> <c-w>2-
" nnoremap <M-o> :call Resize(0)<CR>
" nnoremap <M-p> :call Resize(1)<CR>
nnoremap <M-q> gqip
nnoremap [A :w<CR>:!<up><CR><CR>
nnoremap <M-v> :e 
nnoremap <M-z> :setlocal foldmethod=expr foldexpr=GetPythonFoldBest(v:lnum) foldtext=PyFoldText()
        \ <CR>:call ToggleFold()<CR>gg

" nnoremap <m-b> <c-b>
" nnoremap <m-s> <c-f>

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
