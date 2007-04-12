#!/usr/local/bin/perl
# Create a new virtual folder from some search results

require './mailbox-lib.pl';
&ReadParse();
@folders = &list_folders();
$in{'virtual'} || &error($text{'virtualize_ename'});

$folder = { 'type' => 6,
	    'mode' => 0,
	    'name' => $in{'virtual'},
	    'virtual' => 1,
	    'members' => [ ] };
foreach $k (keys %in) {
	if ($k =~ /^idx_(\d+)$/) {
		($idx, $fidx) = split(/\s+/, $in{$k}, 2);
		$folder->{'members'}->[$1] = [ $folders[$fidx], $idx ];
		}
	}
&save_folder($folder);
&redirect("index.cgi?folder=".scalar(@folders));

