#!/usr/local/bin/perl
# add_address.cgi
# Add an address from an email to the user's address book
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our %in;

require './mailbox-lib.pl';
&ReadParse();

# Check for a duplicate
my @addrs = &list_addresses();
my $found;
foreach my $a (@addrs) {
	if (lc($a->[0]) eq lc($in{'addr'})) {
		$found = $a;
		}
	}

if (!$found) {
	&create_address($in{'addr'}, $in{'name'});
	}
my @sub = split(/\0/, $in{'sub'});
my $subs = join("", map { "&sub=$_" } @sub);
my $qid = &urlize($in{'id'});
&redirect("view_mail.cgi?id=$qid&folder=$in{'folder'}$subs");
