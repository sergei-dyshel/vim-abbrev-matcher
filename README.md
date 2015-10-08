vim-abbrev-matcher
==================

Abbreviation matcher for [CtrlP] and [Unite].

Unlike "traditional" fuzzy search it matches by beginnings of words.
For example, `fb` matches `foo_bar` but not `if_bar`. Words considered are
groups of alphabetic characters, groups of digits and CamelCase words.
All other characters constitute words by themselves.


TOC
-----------------

- [Requirements](#requirements)
- [Rationale](#rationale)
- [Installation](#installation)
- [Configuration](#configuration)
- [Standalone usage](#standalone)
- [Limitations](#limitations)


Requirements
------------
 - Vim compiled with `+python` support.
 - Google [RE2] library recommended for best performance.


Rationale
---------

Most of the modern popular "fuzzy" searches allow matching of pattern letters
anywhere in the string. This leads to big number of irrelavant results.
In order to prioritize "good" these searches need to rely on sophisticated
ranking algorithms.

However, most programmers just type few first letters of some words of the
filename/identifier they are searching. By knowing that, the searcher can return
much less matcher so that only minimal ranking will be needed.


Installation
------------

For the plugin itself just use your favourite plugin manager.

For best performance you need to install [RE2] library (available in most
distributions) and corresponding Python binding.

```bash
apt-get install libre2-dev  # Debian-based
yum install re2-devel # Fedora-based

easy_install re2
# ...or...
pip install re2
```

pcre2:
```
pip install python-pcre

Configuration
-------------

For [Unite]:
```vim
" use matcher for all sources
call unite#filters#matcher_default#use(['matcher_abbrev'])

" use matcher for specific source
call unite#custom#source('line', 'matchers', 'matcher_abbrev')

" use sorter for all sources
call unite#filters#sorter_default#use(['sorter_abbrev'])

" use sorter for specific sources
call unite#custom#source('file,file_rec,file_rec/async,file_rec/git',
    \ 'sorters', 'sorter_abbrev')
```

For [CtrlP]:
```vim
let g:ctrlp_match_func = { 'match': 'ctrlp#abbrev_matcher#match' }
```


Standalone usage
----------------
The Python script provided in `src/abbrev_matcher.py` can also be used as a
standalone utility in two ways:

- As simple grep-like searcher, it filters input and outputs only lines matching
pattern.
```bash
cat some-file.txt | abbrev_matcher.py mypat
```

- As 


Limitations
-----------

The work is still in its early stage and therefore lack some features:
- Only english patterns supported.
- No highlighting of matched characters.
- No cofiguration yet for ranking mechanism.



[CtrlP]: https://github.com/ctrlpvim/ctrlp.vim
[Unite]: https://github.com/Shougo/unite.vim
[RE2]: https://github.com/google/re2
