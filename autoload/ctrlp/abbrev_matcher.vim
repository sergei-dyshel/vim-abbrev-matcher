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

" fuzzy abbreviation matcher for CtrlP

if !has('python')
  echo 'In order to use pymatcher plugin, you need +python'
endif

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')

python << EOF
import sys
import os.path
_root_dir = os.path.join(os.path.dirname(os.path.dirname(
                         vim.eval('s:plugin_path'))), 'src')
sys.path.append(_root_dir)
import abbrev_matcher
EOF

function! ctrlp#abbrev_matcher#match(items, str, limit, mmode, ispath,
      \ crfile, regex)

  if a:str == ''
    return a:items[0:a:limit]
  endif

  let results = []

  python abbrev_matcher.filter_ctrlp()

  return results
endfunction
