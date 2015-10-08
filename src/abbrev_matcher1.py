#!/usr/bin/env python

""" The MIT License (MIT)

Copyright (c) 2015 Sergei Dyshel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import print_function

import os
import os.path
import sys
import logging


RE_SYNTAXES = ['general', 'vim']


# for embedded use
logging.basicConfig(format='[abbrev_matcher.py] %(message)s',
                    level=logging.WARNING)


def MatchGenerator(pattern, string, offset=0):
    """Recursively generate matches of `pattern` in `string`."""

    def _find_ignorecase(string, char, start=0):
        """Find first occurrence of `char` inside `string`,
           starting with `start`-th character."""
        if char.isalpha():
            lo = string.find(char.lower(), start)
            hi = string.find(char.upper(), start)
            if lo == -1:
                return hi
            elif hi == -1:
                return lo
            else:
                return min(hi, lo)
        else:
            return string.find(char, start)

    if pattern == '':
        yield []
        return

    if string == '':
        return

    indices = range(len(string))

    abbrev_0 = pattern[0]
    abbrev_rest = pattern[1:]

    if abbrev_0.lower() == string[0].lower():
        matches = MatchGenerator(abbrev_rest, string[1:], offset + 1)
        for m in matches:
            m.insert(0, offset)
            yield m

    i = _find_ignorecase(string, abbrev_0, 1)
    while i != -1:
        curr = string[i]

        prev = string[i - 1]
        word_boundary = ((curr.isupper() and not prev.isupper()) or
                         (curr.islower() and not prev.isalpha()) or
                         (curr.isdigit() and not prev.isdigit()) or
                         (not curr.isalnum() and curr != prev))
        if word_boundary:
            matches = MatchGenerator(abbrev_rest, string[i + 1:],
                                     offset + i + 1)
            for m in matches:
                m.insert(0, offset + i)
                yield m

        i = _find_ignorecase(string, abbrev_0, i + 1)


def make_regex(pattern, syntax='general', escape=False):
    """Build regular expression corresponding to `pattern`."""

    assert syntax in RE_SYNTAXES

    def re_group(r):
        if syntax == 'vim':
            return r'%(' + r + r')'
        # return r'(?:' + r + r')'
        return r'(' + r + r')'

    def re_or(r1, r2):
        return re_group(re_group(r1) + '|' + re_group(r2))

    def re_opt(r):
        return re_group(r) + '?'

    res = ''
    if syntax == 'vim':
        res += r'\v'
    res += '^'
    for i, ch in enumerate(pattern):
        if ch.isalpha():
            ch_lower = ch.lower()
            ch_upper = ch.upper()
            not_alpha = '[^a-zA-Z]'
            not_upper = '[^A-Z]'
            anycase = re_opt(r'.*{not_alpha}') + '[{ch_lower}{ch_upper}]'
            camelcase = re_opt(r'.*{not_upper}') + '{ch_upper}'
            ch_res = re_or(anycase, camelcase)
        elif ch.isdigit():
            ch_res = (re_opt(r'.*[^0-9]') + '{ch}')
        else:
            ch_res = r'.*\{ch}'
        res += ch_res.format(**locals())
    if escape:
        res = res.replace('\\', '\\\\')
    return res


class BaseMatcher(object):
    def match(self, string):
        pass


class SlowMatcher(BaseMatcher):
    """Matches using recursive algorithm."""

    def __init__(self, pattern):
        self.pattern = pattern

    def match(self, string):
        match_gen = MatchGenerator(self.pattern, string)
        try:
            m = match_gen.next()
            return m
        except StopIteration:
            return None


class RegexMatcher(BaseMatcher):
    """Matches using regular expression."""

    RE_ENGINES = ['pcre', 're2']  # in the order of preference

    def __init__(self, pattern, re_engine):
        self.re_module = __import__(re_engine)
        self.pattern = pattern
        regex = make_regex(pattern, syntax='general')
        self.comp_regex = self.re_module.compile(regex)

    def match(self, string):
        return self.re_module.match(self.comp_regex, string)


def create_matcher(pattern, re_engine='auto'):
    """Create specific or best-available matcher."""

    if re_engine != 'no':
        for curr_engine in RegexMatcher.RE_ENGINES:
            if re_engine != 'auto' and re_engine != curr_engine:
                continue
            try:
                matcher = RegexMatcher(pattern, re_engine=curr_engine)
                logging.info('using {curr_engine} engine'.format(**locals()))
                return matcher
            except ImportError:
                msg = '{curr_engine} engine not found'.format(**locals())
                if re_engine == 'auto':
                    logging.info(msg)
                else:  # 'no'
                    logging.error(msg)
        logging.warning('no regex engine found, falling back to slow method')
    else:
        logging.info('using slow matching algorithm')
    return SlowMatcher(pattern)


class Ranker(object):
    def __init__(self, pattern, is_file=False):
        self.is_file = is_file
        self.pattern = pattern

    def rank(self, string):
        matches = MatchGenerator(self.pattern, string)
        match_list = list(matches)
        if not match_list:
            return 0
        best_match = min(match_list, key=lambda m: self._rank_match(string, m))
        best_rank = self._rank_match(string, best_match)
        return best_rank

    def _rank_match(self, string, match):
        r = 0.0
        prev = -2
        for i in match:
            if i != prev + 1:
                w = 1
                if self.is_file and i == 0 or string[i - 1] == os.sep:
                    w = 0.5
                r += w
            prev = i
        r = r / len(self.pattern) * 100
        r = r * (len(string) ** 0.05)

        if self.is_file:
            basename_start = len(os.path.split(string)[0])
            if match[0] >= basename_start:
                r = r / 10

        return r


def filter_unite():
    import vim
    pattern = vim.eval('input')
    candidates = vim.eval('candidates')
    matcher = create_matcher(pattern)
    for i in reversed(xrange(len(candidates))):
        word = (candidates[i]['word'] if isinstance(candidates[i], dict) else
                candidates[i])
        if not matcher.match(word):
            vim.command('unlet candidates[{}]'.format(i))


def filter_ctrlp():
    import vim
    items = vim.eval('a:items')
    pattern = vim.eval('a:str')
    limit = int(vim.eval('a:limit'))
    ispath = vim.eval('a:ispath')

    matcher = create_matcher(pattern)
    ranker = Ranker(pattern, is_file=ispath)

    results = filter(matcher.match, items)
    results.sort(key=ranker.rank)
    results = results[0:limit]

    vimres = ['"' + line.replace('\\', '\\\\').replace('"', '\\"') + '"'
              for line in results]

    vim.command('let results = [%s]' % ','.join(vimres))


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug',
                        action='store_const',
                        dest='loglevel',
                        const=logging.DEBUG,
                        default=logging.WARNING)
    parser.add_argument('-v', '--verbose',
                        action='store_const',
                        dest='loglevel',
                        const=logging.INFO)
    parser.add_argument('--re-engine',
                        choices=RegexMatcher.RE_ENGINES + ['no', 'auto'],
                        default='auto')
    parser.add_argument('--no-re',
                        action='store_const',
                        dest='re_engine',
                        const='no',
                        help='same as --re_engine=no')
    parser.add_argument('--pcre',
                        action='store_const',
                        dest='re_engine',
                        const='pcre',
                        help='same as --re_engine=pcre')
    parser.add_argument('--re2',
                        action='store_const',
                        dest='re_engine',
                        const='re2',
                        help='same as --re_engine=re2')
    parser.add_argument('--rank',
                        choices=['no', 'general', 'file'],
                        default='no')
    parser.add_argument('--reverse', action='store_true', default=False)
    parser.add_argument('--regex-only', action='store_true', default=False)
    parser.add_argument('pattern')
    args = parser.parse_args()

    logging.basicConfig(format='%(message)s', level=args.loglevel)

    for syntax in RE_SYNTAXES:
        regex = make_regex(args.pattern, syntax=syntax, escape=True)
        logging.debug('{syntax} regex: {regex}'.format(**locals()))

    if args.regex_only:
        print(make_regex(args.pattern, syntax='general', escape=True), end='')
        return 0

    matcher = create_matcher(args.pattern, re_engine=args.re_engine)

    results = filter(matcher.match, sys.stdin)
    if args.rank != 'no':
        ranker = Ranker(args.pattern, is_file=(args.rank == 'file'))
        results.sort(key=ranker.rank, reverse=args.reverse)

    for line in results:
        if args.rank and args.loglevel <= logging.DEBUG:
            print(ranker.rank(line), end=' ')
        print(line, end='')

    return 0 if results else 1


if __name__ == '__main__':
    sys.exit(main())
