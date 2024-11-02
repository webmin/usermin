#!/usr/local/bin/perl
# Create a new virtual folder from some search results
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
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
		my ($folder) = grep { $_->{'index'} == $fidx } @folders;
		$folder || &error($text{'view_efolder'});
		$folder->{'members'}->[$1] = [ $folder, $idx ];
		}
	}
&save_folder($folder);
&redirect("index.cgi?folder=".scalar(@folders));
