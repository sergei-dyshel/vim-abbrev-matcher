import sys
import argparse
import abbrev_matcher

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--method',
                        choices=['re2', 'simple', 'auto'],
                        default='auto')
    parser.add_argument('--rank',
                        choices=['disable', 'general', 'file'],
                        default='disable')
    parser.add_argument('--reverse', action='store_true', default=False)
    parser.add_argument('abbrev')
    args = parser.parse_args()

    use_re2 = {'re2': True, 'simple': False, 'auto': None}[args.method]
    matcher = abbrev_matcher.Matcher(args.abbrev,
                                     use_re2=use_re2,
                                     debug=args.debug)

    results = filter(matcher.match, sys.stdin)
    if args.rank in ['general', 'file']:
        ranker = abbrev_matcher.Ranker(args.abbrev,
                                       is_file=(args.rank == 'file'))
        results.sort(key=ranker.rank, reverse=args.reverse)

    for line in results:
        if args.rank and args.debug:
            print ranker.rank(line),
        print line,

    sys.exit(0 if results else 1)

if __name__ == '__main__':
    main()

