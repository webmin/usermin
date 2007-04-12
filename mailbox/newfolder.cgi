#!/usr/local/bin/perl
# Just re-directs to the appropriate folder creator

require './mailbox-lib.pl';
&ReadParse();
&redirect($in{'prog'});

