"
" The MIT License (MIT)
" Copyright (c) 2015 Sergei Dyshel
"
" Permission is hereby granted, free of charge, to any person obtaining a copy
" of this software and associated documentation files (the "Software"), to deal
" in the Software without restriction, including without limitation the rights
" to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
" copies of the Software, and to permit persons to whom the Software is
" furnished to do so, subject to the following conditions:
"
" The above copyright notice and this permission notice shall be included in all
" copies or substantial portions of the Software.
"
" THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
" IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
" FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
" AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
" LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
" OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
" SOFTWARE.
" ==========================================================================

" fuzzy abbreviation matcher for Unite

let s:save_cpo = &cpo
set cpo&vim

if !has('python')
  echoerr 'In order to use "matcher_abbrev" plugin, you need +python vim'
  finish
endif

function! unite#filters#matcher_abbrev#define() "{{{
  return s:matcher
endfunction"}}}


let s:matcher = {
      \ 'name' : 'matcher_abbrev',
      \ 'description' : 'abbrev matcher',
      \}

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')

python << EOF
import sys
import os.path
_root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
vim.eval('s:plugin_path')))), 'src')
sys.path.append(_root_dir)
import abbrev_matcher
EOF

function! s:matcher.filter(candidates, context) "{{{
  if a:context.input == ''
    return unite#filters#filter_matcher(
          \ a:candidates, '', a:context)
  endif

  if len(a:context.input) == 1
    " Fallback to glob matcher.
    return unite#filters#matcher_glob#define().filter(
          \ a:candidates, a:context)
  endif


  let candidates = a:candidates
  for input in a:context.input_list
    if input == '!' || input == ''
      continue
    elseif input =~ '^:'
      " Executes command.
      let a:context.execute_command = input[1:]
      continue
    endif

    python abbrev_matcher.filter_unite()
  endfor

  return candidates
endfunction"}}}


let &cpo = s:save_cpo
unlet s:save_cpo

" vim: foldmethod=marker
