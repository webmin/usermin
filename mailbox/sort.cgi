#!/usr/local/bin/perl
# Adjust the sort order and field, and return to the index
use strict;
use warnings;
our %in;

require './mailbox-lib.pl';
&ReadParse();
my @folders = &list_folders();
my ($folder) = grep { $_->{'index'} == $in{'folder'} } @folders;
&save_sort_field($folder, $in{'field'}, $in{'dir'});

#Return in JSON format if needed
if ($in{'returned_format'} eq "json") {
		my %sort;
		$sort{'id'} = undef;
		$sort{'folder'} = $in{'folder'};
		$sort{'field'} = $in{'field'};
		$sort{'dir'} = $in{'dir'};
		$sort{'start'} = $in{'start'};
		if (defined($in{'searched'})) {
			$sort{'searched'} = $in{'searched'};
			$sort{'searched_folder_index'} = $in{'searched_folder_index'};
			$sort{'searched_folder_name'} = $in{'searched_folder_name'};
			$sort{'searched_folder_id'} = $in{'searched_folder_id'};
			$sort{'searched_folder_file'} = $in{'searched_folder_file'};
			}
		print_json(\%sort);
	}
	else {
		# Redirect to it
		&redirect("index.cgi?folder=$in{'folder'}&start=$in{'start'}");
		}
