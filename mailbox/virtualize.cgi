#!/usr/local/bin/perl
# Create a new virtual folder from some search results
use strict;
use warnings;
our (%text, %in);

require './mailbox-lib.pl';
&ReadParse();
my @folders = &list_folders();
$in{'virtual'} || &error($text{'virtualize_ename'});

my $folder = { 'type' => 6,
	    'mode' => 0,
	    'name' => $in{'virtual'},
	    'virtual' => 1,
	    'members' => [ ] };
foreach my $k (keys %in) {
	if ($k =~ /^idx_(\d+)$/) {
		my ($idx, $fidx) = split(/\s+/, $in{$k}, 2);
		$folder->{'members'}->[$1] = [ $folders[$fidx], $idx ];
		}
	}
&save_folder($folder);
&redirect("index.cgi?folder=".scalar(@folders));
