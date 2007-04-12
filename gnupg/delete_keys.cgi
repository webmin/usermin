#!/usr/local/bin/perl
# Delete a bunch of non-secret keys

require './gnupg-lib.pl';
&ReadParse();
&error_setup($text{'delkeys_err'});
@d = split(/\0/, $in{'d'});
@d || &error($text{'delkeys_enone'});

@keys = &list_keys();
foreach $d (sort { $b <=> $a } @d) {
	$key = $keys[$d];
	&delete_key($key);
	}
&redirect("list_keys.cgi");
