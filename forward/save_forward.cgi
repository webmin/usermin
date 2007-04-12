#!/usr/local/bin/perl
# save_forward.cgi
# Save the manually edited .forward file

require './forward-lib.pl';
&ReadParseMime();
$in{'forward'} =~ s/\r//g;
&open_tempfile(FORWARD, ">$forward_file");
&print_tempfile(FORWARD, $in{'forward'});
&close_tempfile(FORWARD);
&set_forward_perms();
&redirect("");

