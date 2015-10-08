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

import subprocess

RE_SYNTAXES = ['general', 'vim']


# for embedded use
logging.basicConfig(format='[abbrev_matcher.py] %(message)s',
                    level=logging.WARNING)


def filter_grep(pattern, strings):
    grep = subprocess.Popen(['grep', '-E', '-n', pattern],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    out, err = grep.communicate('\n'.join(strings))
    res = set()
    for out_str in out.splitlines():
        line_num = out_str.split(':', 1)[0]
        res.add(int(line_num))
    return res



def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('pattern')
    args = parser.parse_args()

    strings = map(str.strip, list(sys.stdin))
    line_nums = filter_grep(args.pattern, strings)
    for line_num in line_nums:
        print(strings[line_num])

if __name__ == '__main__':
    sys.exit(main())
