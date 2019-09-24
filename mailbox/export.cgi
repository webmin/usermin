#!/usr/local/bin/perl
# Output the address book in some format
use strict;
use warnings;
our (%text, %in);

require './mailbox-lib.pl';
&ReadParse();
&error_setup($text{'export_err'});

# Build the list of addresses
my @addrs = &list_addresses();
my %done;
if ($in{'dup'}) {
	@addrs = grep { !$done{$_->[0]}++ } @addrs;
	}

if ($in{'fmt'} eq 'csv') {
	# CSV format
	print "Content-type: text/csv\n\n";
	foreach my $a (@addrs) {
		print "\"$a->[0]\",\"$a->[1]\"\n";
		}
	}
else {
	# VCard format
	eval "use Net::vCard";
	$@ && &error($text{'import_enetvcard'});
	print "Content-type: text/vcard\n\n";
	foreach my $a (@addrs) {
		my ($first, $last) = split(/\s+/, $a->[1], 2);
		print "BEGIN:VCARD\n";
		print "VERSION:4.0\n";
		if ($first && $last) {
			print "FN:$a->[1]\n";
			print "N:${last};${first};;;\n";
			}
		elsif ($first) {
			print "FN:$a->[1]\n";
			print "N:${first};;;;\n";
			}
		if ($a->[0]) {
			print "EMAIL:$a->[0]\n";
			}
		print "END:VCARD\n";
		}
	}
