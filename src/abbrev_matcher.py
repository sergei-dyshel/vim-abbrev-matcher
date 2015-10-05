import os
import os.path

try:
    import re2
    has_re2 = True
except ImportError:
    has_re2 = False

try:
    import vim
except:
    pass


def _find_ignorecase(string, sub, start=0):
    if sub.isalpha():
        lo = string.find(sub.lower(), start)
        hi = string.find(sub.upper(), start)
        if lo == -1:
            return hi
        elif hi == -1:
            return lo
        else:
            return min(hi, lo)
    else:
        return string.find(sub, start)


def match_generator(abbrev, string, offset=0):
    if abbrev == '':
        yield []
        return

    if string == '':
        return

    indices = range(len(string))

    abbrev_0 = abbrev[0]
    abbrev_rest = abbrev[1:]

    if abbrev_0.lower() == string[0].lower():
        matches = match_generator(abbrev_rest, string[1:], offset + 1)
        for m in matches:
            m.insert(0, offset)
            yield m

    i = _find_ignorecase(string, abbrev_0, 1)
    while i != -1:
        curr = string[i]

        prev = string[i - 1]
        word_boundary = ((curr.isupper() and not prev.isupper())
                or (curr.islower() and not prev.isalpha())
                or (curr.isdigit() and not prev.isdigit())
                or (not curr.isalnum() and curr != prev))
        if word_boundary:
            matches = match_generator(abbrev_rest, string[i + 1:], offset + i + 1)
            for m in matches:
                m.insert(0, offset + i)
                yield m

        i = _find_ignorecase(string, abbrev_0, i + 1)


def make_regex(abbrev, vim=False):
    def re_group(regex):
        if vim:
            return r'\%(' + regex + r'\)'
        return r'(?:' + regex + r')'

    def re_or(re1, re2):
        op = '\|' if vim else '|'
        return re_group(re_group(re1) + op + re_group(re2))


    def re_opt(regex):
        return re_group(regex) + ('\?' if vim else '?')

    res = '^'
    for ch in abbrev:
        if ch.isalpha():
            lo = ch.lower()
            up = ch.upper()
            anycase = re_opt(r'.*[^a-zA-Z]') + '[{lo}{up}]'
            camelcase = re_opt(r'.*[^A-Z]') + '{up}'
            ch_res = re_or(anycase, camelcase)
        elif ch.isdigit():
            ch_res = (re_opt(r'.*[^0-9]') + '{ch}')
        else:
            ch_res = r'.*\{ch}'
        res += ch_res.format(**locals())
    return res


class Matcher(object):
    def __init__(self, abbrev, use_re2=None, debug=False):
        self.abbrev = abbrev
        self.debug = debug
        if use_re2 and not has_re2:
            raise Exception('Google RE2 not found!')
        self.using_re2 = False
        if has_re2 and use_re2 != False:
            self.using_re2 = True
            regex = make_regex(abbrev)
            if debug:
                print regex
            self.re_abbrev = re2.compile(regex)

    def match(self, string):
        if self.using_re2:
            return re2.match(self.re_abbrev, string)
        else:
            match_gen = match_generator(self.abbrev, string)
            try:
                m = match_gen.next()
                return m
            except StopIteration:
                return None

class Ranker(object):
    def __init__(self, abbrev, is_file=False):
        self.is_file = is_file
        self.abbrev = abbrev

    def rank(self, string):
        matches = match_generator(self.abbrev, string)
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
        r = r / len(self.abbrev) * 100
        r = r * (len(string) ** 0.05)

        if self.is_file:
            basename_start = len(os.path.split(string)[0])
            if match[0] >= basename_start:
                r = r / 10

        return r


def filter_unite():
    abbrev = vim.eval('input')
    candidates = vim.eval('candidates')
    matcher = Matcher(abbrev, use_re2=True)
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

    matcher = Matcher(pattern, use_re2=None)
    ranker = Ranker(pattern, is_file=ispath)

    results = filter(matcher.match, items)
    results.sort(key=ranker.rank)
    results = results[0:limit]

    vimres = ['"' + line.replace('\\', '\\\\').replace('"', '\\"') + '"' for line in results]

    vim.command('let results = [%s]' % ','.join(vimres))
