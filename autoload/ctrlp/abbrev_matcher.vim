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

	echomsg 'here'
    python abbrev_matcher.filter_ctrlp()

    return results
endfunction
