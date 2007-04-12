#!/usr/local/bin/perl
# save_ffile.cgi
# Save a filter file

require './forward-lib.pl';
&ReadParseMime();
&error_setup($text{'ffile_err'});

for($i=0; defined($in{"field_$i"}); $i++) {
	next if (!$in{"field_$i"});
	$in{"match_$i"} || &error($text{'ffile_ematch'});
	$in{"action_$i"} || &error($text{'ffile_eaction'});
	push(@filter, $in{"what_$i"}." ".$in{"action_$i"}." ".
		      $in{"field_$i"}." ".$in{"match_$i"}."\n");
	}
push(@filter, "2 ".$in{'other'}."\n") if ($in{'other'});

&open_tempfile(FILE, ">$in{'vfile'}", 1) || &error(&text('ffile_ewrite', $!));
&print_tempfile(FILE, @filter);
&close_tempfile(FILE);
&redirect("edit_alias.cgi?num=$in{'num'}&file=$in{'file'}");

