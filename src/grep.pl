#!/usr/bin/env perl

use strict;
use warnings;

my $reobj = qr/$ARGV[0]/;

while (<STDIN>) {
    print $_ if /$reobj/;
}
