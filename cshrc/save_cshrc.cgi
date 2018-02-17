#!/usr/local/bin/perl
# save_cshrc.cgi
# Save the user's login script

require './cshrc-lib.pl';
&ReadParseMime();

$in{'cshrc'} =~ s/\r//g;
&open_tempfile(CSHRC, ">".$cshrc_files[$in{'idx'}]);
&print_tempfile(CSHRC, $in{'cshrc'});
&close_tempfile(CSHRC);
&redirect("");

