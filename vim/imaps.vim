"
" <m-v>      - search; find
" <m-r>      - repeat search; find
" <m-b>      - repeat search back; find
" <m-p>      - paste vim clipboard default register
" <c-z>      - undo
" <c-q>      - return, backspace; enter, cr

" <m-y>      - previous block; jump, paragraph
" <m-u>      - next block; jump, paragraph
" <m-i>      - top of screen; H
" <m-w>      - bottom of screen; L
" <m-m>      - redraw cursor line center screen; M

" <m-3>      - scroll one line up; 1
" <m-4>      - scroll one line down; 1
" <m-8>      - next html tag
" <m-7>      - previous html tag
" <m-t>      - blank html Tag open/close; new
" <m-z>      - enter and add comment to next line; return, newline, continue
" <c-s>      - pydiction complete python keyword; auto, function, module


"
" <F5>       - paste X win clipboard
" <m-n>      - copy curreNt line; yy
"
" <c-y>      - previous word; jump
" <c-u>      - next word; jump
" <c-l>      - <right>
" <c-f>      - <right>
" <c-h>      - <left>
" <c-j>      - <down>
" <c-k>      - <up>
" <m-k>      - up 4 lines
" <m-j>      - down 4 lines
" <m-l>      - right 4 chars
" <m-h>      - left 4 chars
" <c-m-l>    - right 12 chars
" <c-m-h>    - left 12 chars
" <c-m-j>    - down 12 chars
" <c-m-k>    - up 12 chars
" <m-,>      - jump to 25% in line
" <m-.>      - jump to 50% in line
" <m-/>      - jump to 75% in line
"
"
" ^- &#8212; - html long em dash
"
" <m-9>      - 1 (opening) parenS
" <c-e>      - delete one char; Erase
" <c-^>      - first char on current line
" <c-a>      - end of current line
" <m-s>      - Save current buffer; write
" <c-c>      - Change next word; delete
" <m-x>      - end of line and Enter; neXt
"
" <s-m-d>    - ToggleAcp, toggle auto complete popup; disable, enable
" <m-e>      - Erase current line; delete
"
" <m-c>      - delete to end of line; Clear, erase
"
" <m-1>      - python print name and value of variable
" <m-'>      - six quotes for python docstring
" <m-g>      - : at the end, Enter; python, semicolon
" <m-o>      - dOt (in autocmd) for python
" <m-q>      - join lines
" <m-c-p>    - run current buffer through python; file
" <m-2>      - close xhtml tag
" <m-0>      - uncapitalize preceding word; decapitalize, lowercase

" <m-5>      - esc and save; write, file, normal mode
" <m-">      - real quotes; pretty, nice
" <F3>       - go to brackets at the end; )), ]], find
" S-Alt-O    - add line above; insert, up
" C-Alt-M    - jump to matching parens; %
" Alt-D      - backspace
" F1 p       - python imports popup completion menu
" F1 d       - django imports popup completion menu
" F1 u       - add super() line, insert
"
" Digraphs: °:DG, ²:2S,3S, ·:.M, º:-o, »:>>, ×:*X, :set digraph; 1st<BS>2nd
"endlist
"" # X#    - don't force comment to 1st col
"
" Available Alt: (alt-a is move win to cursor)  | Available Ctrl: 123456789:
"
" Leaders: ^]]
"

inoremap <f1>d <c-r>=DjangoImports()<cr>
inoremap <f1>p <c-r>=PythonImports()<cr>

inoremap <m-d> <bs>
inoremap <s-a-o> <c-o>O
inoremap <c-a-m> <c-o>%

inoremap <F3> <esc>/)\+$\\|]\+$\\|$<CR>:nohl<CR>:call InsAtBracket()<CR>
inoremap <m-f> _
inoremap <m-"> “”<left>
inoremap <F1> <end><cr><bs>-<space>

inoremap ( ()<left>
inoremap ) <c-r>=ClosePair(')')<CR>
inoremap { {}<left>
inoremap } <c-r>=ClosePair('}')<CR>
inoremap [ []<left>
inoremap ] <c-r>=ClosePair(']')<CR>
" inoremap > <c-r>=ClosePair('>')<CR>

inoremap <s-m-d> <c-o>:call ToggleAcp()<CR>
" inoremap <m-d> <esc>ddddko

inoremap ` ``<left>

inoremap <m-6> <C-X><C-L>
inoremap <m-5> <esc>:w<CR>
inoremap <m-0> <esc>b~ea
inoremap <m-z> <C-R>=pumvisible() ? "\<lt>c-e>\<lt>cr># " : "\<lt>cr># "<CR>
inoremap <m-2> </<c-x><c-o>
inoremap <m-q> <c-o>J
imap <c-y> <esc>bi
" <c-u> is handled in functions.vim, using NextWord()

cmap <c-y> <s-left>
cmap <c-u> <s-right>

inoremap <m-y> <esc>{i
inoremap <m-u> <esc>}i
inoremap <c-q> <end><cr><bs>
inoremap <c-l> <right>
inoremap <c-f> <right>
inoremap <c-h> <left>

inoremap <c-j> <C-R>=pumvisible() ? "\<lt>c-e>\<lt>down>" : "\<lt>down>"<CR>
inoremap <c-k> <C-R>=pumvisible() ? "\<lt>c-e>\<lt>up>" : "\<lt>up>"<CR>

inoremap <c-e> <del>
inoremap <c-a> <end>
inoremap <m-s> <esc>:w<cr>a<c-o>:call CloseMenu()<CR>
" inoremap <c-c> <esc>ldwi
inoremap <c-c> <esc>lce

inoremap <c-^> <c-o>^
inoremap <c-z> <C-o>u
inoremap <c-g> -

inoremap <m-9> (
inoremap <m-e> x<bs><down><c-o>dd<up><end>

inoremap <m-t> <></><esc>4ha
inoremap <m-'> """"""<left><left><left>
" inoremap <m-1> <esc>F lviWyiprint("<c-r>": ",<space><end>)
" inoremap <m-1> <esc>:call AddPrint()<CR>

inoremap <m-j> <C-R>=pumvisible() ? "\<lt>c-e>\<lt>down>\<lt>down>\<lt>down>" : "\<lt>down>\<lt>down>\<lt>down>"<CR>
inoremap <m-k> <C-R>=pumvisible() ? "\<lt>c-e>\<lt>up>\<lt>up>\<lt>up>" : "\<lt>up>\<lt>up>\<lt>up>"<CR>
inoremap <c-m-j> <down><down><down><down><down><down><down><down><down>
inoremap <c-m-k> <up><up><up><up><up><up><up><up><up>

inoremap <m-l> <right><right><right>
inoremap <m-h> <left><left><left>
inoremap <c-m-l> <right><right><right><right><right><right><right><right><right>
inoremap <c-m-h> <left><left><left><left><left><left><left><left><left>
inoremap <m-,> <c-o>:call Jump(1)<CR>
inoremap <m-.> <c-o>:call Jump(2)<CR>
inoremap <m-/> <c-o>:call Jump(3)<CR>

inoremap <m-8> <esc>lf<i
inoremap <m-7> <esc>F>li
inoremap <m-x> <end><cr>

inoremap <m-c> <C-\><C-O>D
inoremap <m-n> <C-O>yy
inoremap <m-p> x<bs><esc>pi
inoremap <F5> x<bs><esc>"+]p
" inoremap <m-f> x<bs><esc>
inoremap <m-v> <C-O>/
inoremap <m-r> <C-O>n
inoremap <m-b> <C-O>N

inoremap <m-i> <C-O>H
inoremap <m-w> <C-O>L
inoremap <m-m> <C-O>zz
inoremap <m-3> <C-O><C-Y>
inoremap <m-4> <C-O><C-E>
inoremap <m-g> <esc>A:<cr>

inoremap <m-c-p> <c-o>:!python %<cr>

""
" inoremap <esc>9 (
" inoremap <esc>e <space><c-o>dd
" inoremap <esc>t <></><esc>4ha
" inoremap <esc>' """"""<left><left><left>
" inoremap <esc>1 <esc>F lviWyiprint "<c-r>": ",<space><end>

" inoremap <esc>j <C-R>=pumvisible() ? "\<lt>c-e>\<lt>down>\<lt>down>\<lt>down>\<lt>down>" : "\<lt>down>\<lt>down>\<lt>down>\<lt>down>"<CR>
" inoremap <m-k> <C-R>=pumvisible() ? "\<lt>c-e>\<lt>up>\<lt>up>\<lt>up>\<lt>up>" : "\<lt>up>\<lt>up>\<lt>up>\<lt>up>"<CR>

" inoremap <esc>l <right><right><right><right>
" inoremap <esc>h <left><left><left><left>
" inoremap <esc>8 <esc>lf<i
" inoremap <esc>7 <esc>F>li
" inoremap <esc>x <end><cr>

" inoremap <esc>c <C-\><C-O>D
" inoremap <esc>n <C-O>yy
" inoremap <esc>p <C-O>P
" inoremap <esc>f x<bs><esc>"+pa
" inoremap <esc>v <C-O>/
" inoremap <esc>r <C-O>n
" inoremap <esc>b <C-O>N

" inoremap <esc>i <C-O>H
" inoremap <esc>w <C-O>L
" inoremap <esc>m <C-O>zz
" inoremap <esc>3 <C-O><C-Y>
" inoremap <esc>4 <C-O><C-E>
" inoremap <esc>g <esc>A:<cr>

" inoremap <esc><c-p> <c-o>:!python %<cr>


""
inoremap # X#
" inoremap <tab> -

inoremap <s-tab> <tab>

" python log current line
"inoremap <m-e> <esc>bdealog("<c-r>": %s\n" % <c-r>")
"inoremap ^- &#8212;
"inoremap <Tab> <C-R>=pumvisible() ? "\<lt>CR>" : "\<lt>Tab>"<CR>
