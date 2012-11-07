"======FUNCTIONS======================================================
" SynGroupName        - return current syntax group name at cursor
" OpenCloseOrig       - open file in filelist, close filelist
" FontSize            - increase/decrease font size
" AddPerc             - add 20% to a number
" RestoreScreenPos    - restore win layout after changing to a buffer
" ReloadChrome        - switch to next window, Ctrl-R, switch back
" Edit                - edit multiple files, :E similar to :e

" EndOfLine           - emulate $ cmd, n chars before end of line
" PythonImports       - complete menu with common python imports
" DjangoImports       - complete menu with common django imports
" Cleanup             - cleanup python code
" RepeatChar          - insert n chars and return to command mode

" Foldlevel           - fold to level given as count
" Underline           - underline current line with = or -'s
" InsAtBracket        - if at bracket, insert, otherwise append
" InsEnd              - if at end of line, append, otherwise insert
" ToggleVE            - toggle virtual edit between none and all

" DelLine             - delete next line if blank
" ClosePair           - close a char e.g. ) ] }
" ApplyColorMode      -
" ToggleColorMode     - normal | hide comments | hide comments & strings
" ToggleAcp           - normal | hide comments | hide comments & strings

" Jump                - jump to a location in line
" DelBuffer           - del buffer, keep win layout UNUSED
" CloseMenu           - close completion menu if it's open
" DoRunPyBuffer       - run buffer through Python and show output in a new window
" FindHiLite          - find and display (in a new buffer) with syntax highlighting on

" SearchNoFolds       - search skipping closed folds
" RemindCmds          - print reminder screen with commands
" ToggleFold          - toggle between manual/indent folding
" PyFoldText          - python folding text
" Resize              - resize main vim window
" GetPythonFoldBest   - python folding, for use with foldexpr
"

let g:color_mode = 0
let g:acp_enabled = 1
let g:grep_quickfix = 0
let g:win_size_mode = 0

fun! GrepQuickFixToggle()
    " create grep quickfix window or close it if exists
    let g:grep_quickfix = 1 - g:grep_quickfix
    if g:grep_quickfix
        exe 'vimgrep '.expand('<cword>').' '.expand('%') | :copen | :cc
    else
        cclose
    endif
endfu


fun! WinSizeMode()
    " toggle mode to change window size with h and l keys
    let g:win_size_mode = 1 - g:win_size_mode
    if g:win_size_mode
        echo "Win resize mode ON"
        nnoremap h <c-w>-
        nnoremap l <c-w>+
        nnoremap <esc> :call WinSizeMode()<cr>
    else
        echo "Win resize mode OFF"
        nunmap h
        nunmap l
        nunmap <esc>
    endif
endfu

fun! DoInsertGotoLine()
    " go to line from insert mode
    let c = nr2char(getchar())
    let c = c . nr2char(getchar())
    exe "normal " . c . 'H'
endfu

fun! InsertGotoLine()
    " go to line from insert mode
    call DoInsertGotoLine()
endfu

fun! CurrentChar()
    return getline('.')[col('.')-1]
endfu

fun! NextWord()
    " go to start of next word, or end of current word if at the end of line (check if matches keyword pattern)
    " Using call feedkeys('i') or 'a' may be easier?
    normal lw
    if IsLineEnd()
        if CurrentChar() !~ '\k'
            normal ge
        endif
    else
        normal h
    endif
endfu
imap <c-u> <esc>:call NextWord()<cr>a

fun! GotoLine(count)
    " Go to given line in current screen
    if a:count == 1
        " normal H
        call ToggleJump()
    else
        exe "normal ".a:count."H"
    endif
endfu

function! MoveLine(dir) range
    let c = v:count
    if !c | let c = 1 | endif
    if a:dir
        exec ":m+".c
    else
        let c += 1
        exec ":m-".c
    endif
endfunction

function! TrimEndLines()
    let save_cursor = getpos(".")
    :silent! %s#\($\n\s*\)\+\%$##
    call setpos('.', save_cursor)
endfunction

function! FoldLevel1()
    normal! mx
    set foldlevel=1
    normal! gg
    if search("# Imports")
        normal! zc
    endif
    if search("# Init")
        normal! zc
    endif
    :silent! normal! `xzo
endfu

function! SynGroupName()
    return synIDattr( synID( line("."), col("."), 1 ), "name" )
endfu

function! OpenCloseOrig()
    " open file in current line & close original buffer (used for filelist buffer in autocmd)
    :write
    let orig = bufnr('%')

    " keepalt to avoid setting filelist as alternate buffer '#'
    keepalt silent! normal gf
    if bufnr('%') != orig
        exe "bdelete " . orig
    endif
endfu

function! FontSize(val)
    let g:fontsize += a:val
    exe 'set guifont=Inconsolata\ Medium\ ' . g:fontsize
    sleep 500m
    echo g:fontsize
endfu
nnoremap <f9> :call FontSize(1)<CR>
nnoremap <s-f9> :call FontSize(-1)<CR>

function! AddPerc()
    echo str2float( input("+20% > ") ) * 1.2
endfu
nnoremap [P :call AddPerc()<CR>

function! RestoreScreenPos()
    if &filetype != "vimject" && getpos("'t")[1] && getpos("'s")[1]
        :silent! normal! 'tzt`s
    endif
endfu
" Save screen position when switching files with ctrl-^
" (disable for now because of interferance from tabbar)
" nnoremap <silent> <c-^> msHmt<c-^>:call RestoreScreenPos()<CR>
augroup RestoreScreen
    au!
    au BufLeave * :normal! msHmt
    au BufEnter * :call RestoreScreenPos()
augroup END

function! ReloadChrome()
    :silent! !xmacroplay :0 <~/.vim/reload-browser-xmacro
endfu

function! Edit(really, ...)
    if len(a:000)
      for globspec in a:000
        let l:files = split(glob(globspec), "\n")
        for fname in l:files
          exec 'e'.(a:really).' '.(fname)
        endfor
      endfor
    else
      exec 'e'.(a:really)
    endif
endfunction
command! -nargs=* -complete=file -bang E call Edit("<bang>", <f-args>)

func! SubWord(dir)
    " In variable names like my_var_name, MyVarName, go to subword, capital letter or after '_'
    if (a:dir == 0)
        call search('\v[a-z]([A-Z]|_)[a-z]')
    else
        call search('\v[a-z]([A-Z]|_)[a-z]', 'b')
    endif
    normal l
    if (CurrentChar() == '_')
        if (a:dir == 0)
            normal l
        else
            normal h
        endif
    endif
endfu

func! DownUp(cmd)
    " insert ' mark to add a jump to jumplist when count is large enough; use j or k cmds
    let c = v:count     " v:count will be reset by the mark command
    if (v:count >= 6)
        normal m'
    endif
    exe "normal! " . (c ? c : '') . a:cmd
endfu


func! EndOfLine(n)
    " Go to Nth char before end of line (does not work in newer vims)
    normal! $
    if a:n > 1 | exe "normal ".(a:n-1)."h" | endif
endfu
nnoremap $ :<c-u>call EndOfLine(v:count1)<cr>
" does not always work: (if command with count was used just before)
" nnoremap <expr> $ "<right>$".((v:count>1)?((v:count-1).'h'):(''))


func! PythonImports()
  call complete(col('.'), [
        \ 'import os, sys',
        \ 'import re',
        \ 'from string import join',
        \ 'from pprint import pprint',
        \ 'from collections import defaultdict',
        \ 'from time import localtime, strftime, sleep',
        \ 'from datetime import date, datetime',
        \ 'from copy import copy',
        \ 'from vim import *',
        \ 'from os.path import basename, split, exists, join as pjoin',
        \ 'import json',
        \ 'from __future__ import print_function, unicode_literals, division'
        \ ])
  return ''
endfunc

func! DjangoImports()
  call complete(col('.'), [
        \ 'from django.core.paginator import Paginator, InvalidPage, EmptyPage',
        \ 'from django.core.context_processors import csrf',
        \ 'from django.core.urlresolvers import reverse',
        \ 'from django.http import HttpResponseRedirect, HttpResponse',
        \ 'from django.shortcuts import render_to_response',
        \ 'from django.shortcuts import get_object_or_404',
        \ 'from django.contrib.auth.decorators import login_required',
        \ 'from django.contrib import messages',
        \ 'from django.template import RequestContext, Template, Context, loader, TemplateSyntaxError',
        \ 'from django.utils.http import urlencode',
        \ 'from django.db.models import Q',
        \ 'from django.db import DatabaseError',
        \ 'from django.forms.util import ErrorList',
        \ 'from django.contrib.auth.models import User, Group',
        \ 'from django.utils.html import escape, strip_tags',
        \ 'from django.views.generic.simple import direct_to_template',
        \ 'from django.views.generic.simple import redirect_to'
        \ ])
  return ''
endfunc

function! Cleanup()
    %s/,/, /g
    %s/==/ == /g

    %s/,  /, /g
    %s/==  /== /g
    %s/  ==/ ==/g
endfu

function! RepeatChar(char, count)
    return repeat(a:char, a:count)
endfunction
nnoremap <m-0> :<C-U>exec "normal i".RepeatChar(nr2char(getchar()), v:count1)<CR>

" nnoremap S :<C-U>exec "normal a".RepeatChar(nr2char(getchar()), v:count1)<CR>


fu! Foldlevel(n)
    let n = a:n
    if (n==0) | let n = 1 | endif
    exe "set foldlevel=" . n
endfu
nnoremap <c-j>L :<C-U>call Foldlevel(v:count)<CR>

function! Underline(char)
    normal yyp
    exe ':s/./' . a:char . '/g'
    " call setline('.', repeat(a:char, len(getline('.'))))
endf
nnoremap _= :call Underline('=')<CR>
nnoremap _- :call Underline('-')<CR>

function! InsAtBracket()
    " if at bracket, insert, otherwise append
    let c = CurrentChar()
    if (c == ')' || c == ']')
        call feedkeys("i")
    else
        call feedkeys("a")
    endif
endf


function! IsLineEnd()
    return len(getline('.')) == col('.')
endfu

function! InsEnd()
    if IsLineEnd() | call feedkeys("a") | else | call feedkeys("i") | endif
endf


function! ToggleVE()
    " Toggle virtual edit between none and all
    if (&ve == '')
        set ve=all
        echo "set ve=all"
    else
        set ve=
        echo "set ve="
    endif
endf


function! DelLine()
    " If next line is blank, delete it, else delete current, works but slow!
    let lnum = line('.')
    let last = line('$')
    if lnum != last
        let l = getline(lnum)
        let next = getline(lnum+1)
        if (substitute(next, ' ', '', 'g') == '') && (substitute(l, ' ', '', 'g') == '')
            normal jddkA
        else
            normal dd
        endif
    else
        normal dd
    endif
endf
nnoremap <c-F9> ax<bs><down>dd<up>
inoremap <m-e> x<bs><c-o>:call DelLine()<CR>


function! ClosePair(char)
    if CurrentChar() == a:char
        return "\<Right>"
    else
        return a:char
    endif
endf


func! ApplyColorMode()
    if !exists("b:color_mode") | let b:color_mode = 0 | endif
    if b:color_mode == 0
        hi String guifg=#2aa198
        hi Comment guifg=#586e75
    elseif b:color_mode == 1
        hi Comment guifg=#002b36
    else
        hi String guifg=#002b36
    endif
endfu

func! ToggleColorMode()
    " Normal | Hide comments | Hide comments and strings
    if !exists("b:color_mode") | let b:color_mode = 2 | endif
    let b:color_mode += 1
    if b:color_mode == 3 | let b:color_mode = 0 | endif
    call ApplyColorMode()
endfu

func! ToggleAcp()
    if g:acp_enabled
        :AcpDisable
        let g:acp_enabled = 0
        echo "Acp OFF"
    else
        :AcpEnable
        let g:acp_enabled = 1
        echo "Acp ON"
    endif
endfu


func! Jump(location)
    " Jump to location: `1` - quarter of line, `2`: middle of line, `3`: 3/4 of line
    let line   = getline('.')
    let indent = indent('.')
    let w      = len(line) - indent
    let col    = col('.')
    if w > 98 | let w = 98 | endif

    let loc = w*0.25
    if a:location == 2
        let loc = w*0.5
    elseif a:location == 3
        let loc = w*0.75
    endif
    exe "normal " . string( float2nr(loc) ) . "|"
endfu


func! ToggleJump()
    " Jump between: quarter of line, middle of line, 3/4 of line (if close to boundary, jump to next one)
    let line   = getline('.')
    let indent = indent('.')
    let w      = len(line) - indent
    let col    = col('.')
    if w > 98 | let w = 98 | endif

    let loc1 = w*0.25 + indent
    let loc2 = w*0.5 + indent
    let loc3 = w*0.75 + indent
    let loc  = loc1
    if loc1 - col < 5 | let loc = loc2 | endif
    if loc2 - col < 5 | let loc = loc3 | endif
    if loc3 - col < 5 | let loc = loc1 | endif

    exe "normal " . string( float2nr(loc) ) . "|"
endfu


func! DelBuffer()  " UNUSED
    let bufname=expand('%')
    bnext
    exe ":bdelete! " . fnameescape(bufname)
    let n = 0
    while 1
        let fn = expand('%')
        if (fn !~ '.*\.proj') && (fn !~ '.*\.todo') && (fn !~ '.*\.trak')
            break
        elseif n >= 10
            break
        endif
        bnext
    endwhile
endfunc

fun! CloseMenu()
    " Close completion menu if it's open (for snipMate to work)
    if pumvisible()
        call feedkeys("\<esc>a\<left>", 'n') " Close completion menu
    endif
    " return ''
endfu


fu! DoRunPyBuffer()
    " Run buffer through Python and show output in a new window
    pclose! " force preview window closed
    setlocal ft=python
    " copy the buffer into a new window, then run that buffer through python
    sil %y a | below new | sil put a | sil %!python -
    setlocal previewwindow ro nomodifiable nomodified
    wincmd p
endfu
command! RunPyBuffer call DoRunPyBuffer()


function! FindHiLite(regex) range
" Find and display (in a new buffer) with syntax highlighting on
" Courtesy of Dr. Chip Campbell
" Try putting the following into your <.vimrc>; then
"     :[range]FindHiLite 'pattern'
" will set up a separate window using the syntax highlighting
" and highlight-search emphasis.
  let akeep = @a
  let @a    = ""
  let ft    = &ft
  " Escape special characters in the regex
  let regex = substitute(
              \     substitute(
              \         escape(a:regex, '\\/.*$^~[]'),
              \         "\n$",
              \         "", ""
              \     ),
              \     "\n", '\\_[[:return:]]', "g"
              \ )
  " Do not escape the special characters
  let regex = a:regex
  " Add line numbers followed by a tab for each
  " line found
  exe a:firstline.','.a:lastline."g/".
              \ (&ignorecase==1?'\c':'\C').
              \ regex.'/' .
              \ ':let @a = @a . line(".") . "\t" . getline(".") . "\n"'
  topleft split
  enew!
  put a
  norm! 1G2dd
  exe "set hls nomod ft=".ft
  let @a= akeep
endfunction

command! -range=% -nargs=1 FindHiLite <line1>,<line2>call FindHiLite(<q-args>)


fun! SearchNoFolds()
    " search, skipping closed folds
    let pat = input("/")
    let start = line(".")
    let cur = start
    let last = line("$")
    while cur <= last
        let fold_end = foldclosedend(cur)
        if fold_end != -1
            let cur = fold_end + 1
        endif
        let txt = getline(cur)
        if txt =~ pat
            let i = stridx(txt, pat)
            call cursor(cur, i+1)
            return
        endif
        let cur += 1
    endwhile
    let cur = 0
    while cur <= start
        let fold_end = foldclosedend(cur)
        if fold_end != -1
            let cur = fold_end + 1
        endif
        let txt = getline(cur)
        if txt =~ pat
            let i = stridx(txt, pat)
            call cursor(cur, i+1)
            return
        endif
        let cur += 1
    endwhile
endfu


fun! RemindCmds()
python <<
print r"""
" <m-v>      - search
" <m-r>      - repeat search
" <m-b>      - repeat search back
" <c-z>      - undo

" <m-y>      - previous block
" <m-u>      - next block
" <m-i>      - top of screen
" <m-w>      - bottom of screen
" <m-m>      - redraw cursor line center screen

" <m-3>      - scroll one line up
" <m-4>      - scroll one line down
" <m-8>      - next html tag
" <m-7>      - previous html tag
" <m-t>      - blank html Tag open/close
" <m-z>      - enter and add comment to next line
" <c-s>      - pydiction complete python keyword

        ==NORMAL==

" ,k         - next class definition
" \k         - prev class definition
" ,o         - fold python comments and docstrings
" gk         - pYchecker
" K          - python help on word under cursor
" Alt-t      - :!!  Run/Repeat last shell command
" Ctrl-N     - cd ~/links/
" ,j         - django syntax highlight
" Alt-l      - :, colon, start command mode
" \h         - interactive search for vim commands (vimcmds.py v)
" ,gg        - grep word under cursor in current file (,G same but type pattern)
" _Z         - fold everything but the search pattern
" \2         - toggle colour mode, hide comments, strings
" gx         - delete nearby XHTML tag
" _M         - vim command list
" ,l         - :ls - list buffers
" \n         - toggle line numbers
" _H         - helpgrep words in any order
" \z         - paste from 'z' register (vis Z to copy to z)
" ,gh        - run helptags on vim docs dir

" ,y         - run buffer through python, show in preview window (c-w,z)
" c-j P      - python run current buffer
" \p         - run python interpreter
" \g         - touch log, start xterm tailing log, run current file through python

" ,u         - go to link
" ,gs        - list of scripts
" _R         - list buffers and remove
"""
.
endfu


fun! ToggleFold(...)
    " Toggle fold between manual and indent
    if &foldmethod == "indent" || &foldmethod == "expr"
        setlocal foldmethod=manual
        echo "set to manual fold"
    elseif a:0 == 0
        setlocal foldmethod=indent
        echo "set to indent fold"
    else
        setlocal foldmethod=expr
        echo "set to expr fold"
    endif
endfu


function! PyFoldText()
    " Make a more outline-friendly fold view.
    let uselen = 64     " length of text to include up to bar
    let barlen = 28.0   " length of bar showing func size
    let maxfunc = 90.0  " function size that will show full bar

    " show leading indent
    let size = v:foldend - v:foldstart
    let l = getline(v:foldstart)
    let line = substitute(l, '^[ ]*', '', '')
    let prefix = repeat(' ', (strlen(l) - strlen(line)))
    let c = ''
    if l =~ '^\s*class\s' | let c = '(c)--' | endif
    let line = prefix . '+--' . c . '  ' . line

    " truncate or pad line text to `uselen` length
    let llen = strlen(line)
    if llen < uselen
        let line = line . repeat('-', uselen-llen)
    elseif llen > uselen
        let line = strpart(line, 0, uselen)
    endif

    " add size and pad line again
    let line = line . ' ' . size
    let llen = strlen(line)
    let uselen = uselen + 5
    if llen < uselen
        let line = line . repeat(' ', uselen-llen)
    endif

    " add size bar
    let x = float2nr(barlen * (size / maxfunc))
    if (x > barlen) | let x = float2nr(barlen) | endif
    let rest = float2nr(barlen - x)
    let line = line . '[' . repeat('=', x) . repeat(' ', rest) . ']'
    return line
endfunction


function! GetPythonFoldBest(lnum)
    " Fold python classes and functions (function taken from python_ifold)
    let foldblanks = 0      " Fold trailing blank lines after the function
    let line = getline(a:lnum)

    " Handle Support markers
    if line =~ '{{{'
        let w:sm = 1
        return ">1"
    elseif line =~ '}}}'
        let w:sm = 0
        return "<1"
    endif
    if w:sm
        return "="
    endif

    if line =~ '^\s*\(class\|def\)\s'
    " Verify if the next line is a class or function definition as well
        let imm_nnum = a:lnum + 1
        let nnum = nextnonblank(imm_nnum)
        let nind = indent(nnum)
        let pind = indent(prevnonblank(a:lnum))
        if pind >= nind
            let nline = getline(nnum)
            let w:nestinglevel = nind
            return "<" . ((w:nestinglevel + &sw) / &sw)
        endif
        let w:nestinglevel = indent(prevnonblank(a:lnum))
        return ">" . ((w:nestinglevel + &sw) / &sw)
    endif

    " If next line has less or equal indentation than the first one, we end a fold.
    if foldblanks == 1
        let nnonblank = a:lnum + 1
        let nextline = getline(nnonblank)
    else
        let nnonblank = nextnonblank(a:lnum + 1)
        let nextline = getline(nnonblank)
    endif

    if ((nextline !~ '^#+.*') && (nextline !~ '^$'))
        let nind = indent(nnonblank)
        if nind <= w:nestinglevel
            let w:nestinglevel = nind
            return "<" . ((w:nestinglevel + &sw) / &sw)
        else
            let ind = indent(a:lnum)
            if ind == (w:nestinglevel + &sw)
                if nind < ind
                    let w:nestinglevel = nind
                    return "<" . ((w:nestinglevel + &sw) / &sw)
                endif
            endif
        endif
    endif

    return "="  " per vim docs, this is slow..
    " return -1
endfu
