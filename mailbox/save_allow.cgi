#!/usr/local/bin/perl
# Update allowed or denied email addresses
use strict;
use warnings;
our (%text, %in);

require './mailbox-lib.pl';
&ReadParse();
&error_setup($text{$in{'mode'}.'_err'});
&foreign_require("spam", "spam-lib.pl");
my $conf = &spam::get_config();

# Parse and save addresses
my @addrs;
foreach my $l (split(/\r?\n/, $in{'addrs'})) {
	foreach my $e (&split_addresses($l)) {
		$e->[0] =~ /^\S+\@[a-z0-9\.\-\_\*]+$/i ||
		    $e->[0] =~ /^[a-z0-9\.\-\_\*]+$/i ||
			&error(&text('allow_eaddr', $e->[0]));
		push(@addrs, $e->[0]);
		}
	}
&spam::save_directives($conf, $in{'mode'} eq 'allow' ? 'whitelist_from'
						     : 'blacklist_from',
		       \@addrs, 1);
&flush_file_lines();
&redirect("");
