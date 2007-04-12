#!/usr/local/bin/perl
# Delete several known hosts

require './ssh-lib.pl';
&ReadParse();
&error_setup($text{'dknown_err'});
@d = split(/\0/, $in{'d'});
@d || &error($text{'dknown_enone'});

# Delete each known host
@knowns = &list_knowns();
foreach $d (sort { $b <=> $a } @d) {
	$known = $knowns[$d];
	&delete_known($known);
	}

&redirect("list_knowns.cgi");

