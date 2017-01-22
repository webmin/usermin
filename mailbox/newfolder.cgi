#!/usr/local/bin/perl
# Just re-directs to the appropriate folder creator
use strict;
use warnings;
our %in;

require './mailbox-lib.pl';
&ReadParse();
&redirect($in{'prog'});
