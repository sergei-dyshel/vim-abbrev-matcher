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

import os
import os.path
import sys

try:
    # import re2
    import pcre as re2
    has_re2 = True
except ImportError:
    has_re2 = False

try:
    import vim
except:
    pass

RE_ENGINES = ['pcre', 're2']  # in the order of preference

REGEX_ENGINES = ['general', 'vim']

def MatchGenerator(pattern, string, offset=0):
    """Generate matches of `pattern` in `string`."""

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


def make_regex(pattern, engine='general', escape=False):
    """Build regular expression corresponding to `pattern`."""

    assert engine in REGEX_ENGINES

    def re_group(r):
        if engine == 'vim':
            return r'%(' + r + r')'
        return r'(?:' + r + r')'

    def re_or(r1, r2):
        return re_group(re_group(r1) + '|' + re_group(r2))

    def re_opt(r):
        return re_group(r) + '?'

    res = ''
    if engine == 'vim':
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
    def __init__(self, pattern):
        self.pattern = pattern

    def match(self, string):
        match_gen = MatchGenerator(self.pattern, string)
        try:
            m = match_gen.next()
            return m
        except StopIteration:
            return None


class RE2Matcher(BaseMatcher):
    def __init__(self, pattern):
        self.pattern = pattern
        regex = make_regex(pattern, engine='general')
        self.comp_regex = re2.compile(regex)

    def match(self, string):
        return re2.match(self.comp_regex, string)


class RegexMatcher(BaseMatcher):
    def __init__(self, pattern, re_engine):
        self.re_engine = __import__(re_engine)
        self.pattern = pattern
        regex = make_regex(pattern, engine='general')
        self.comp_regex = re_engine.compile(regex)

    def match(self, string):
        return re2.match(self.comp_regex, string)


def create_matcher(pattern, use_re2=None):
    if use_re2 == True and not has_re2:
        raise Exception('Google RE2 not found!')
    if has_re2 and use_re2 != False:
        return RE2Matcher(pattern)
    if use_re2 != False:
        print >>sys.stderr, "Google RE2 not found, using slow algorithm"
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
    pattern = vim.eval('input')
    candidates = vim.eval('candidates')
    matcher = create_matcher(pattern)
    for i in reversed(xrange(len(candidates))):
        word = (candidates[i]['word'] if isinstance(candidates[i], dict) else
                candidates[i])
        if not matcher.match(word):
            vim.command('unlet candidates[{}]'.format(i))


def filter_ctrlp():
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
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--re_engine',
                        choices=RE_ENGINES + ['no', 'auto'],
                        default='auto')
    parser.add_argument('--rank',
                        choices=['no', 'general', 'file'],
                        default='no')
    parser.add_argument('--reverse', action='store_true', default=False)
    parser.add_argument('--regex', choices=REGEX_ENGINES)
    parser.add_argument('pattern')
    args = parser.parse_args()

    use_re2 = {'re2': True, 'simple': False, 'auto': None}[args.method]
    if args.debug:
        for engine in REGEX_ENGINES:
            print '{} regex: {}'.format(engine, make_regex(args.pattern,
                                                           engine=engine,
                                                           escape=True))
    if args.regex is not None:
        print make_regex(args.pattern, engine=args.regex, escape=True)
        return 0

    matcher = create_matcher(args.pattern, use_re2=use_re2)

    results = filter(matcher.match, sys.stdin)
    if args.rank != 'no':
        ranker = Ranker(args.pattern, is_file=(args.rank == 'file'))
        results.sort(key=ranker.rank, reverse=args.reverse)

    for line in results:
        if args.rank and args.debug:
            print ranker.rank(line),
        print line,

    return 0 if results else 1


if __name__ == '__main__':
    sys.exit(main())
