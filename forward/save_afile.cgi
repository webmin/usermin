#!/usr/local/bin/perl
# save_afile.cgi
# Save an addresses file

require './forward-lib.pl';
&ReadParseMime();

$in{'text'} =~ s/\r//g;
$in{'text'} =~ s/\n*$/\n/;
&open_tempfile(FILE, ">$in{'vfile'}", 1) || &error(&text('afile_ewrite', $!));
&print_tempfile(FILE, $in{'text'});
&close_tempfile(FILE);

&redirect("edit_alias.cgi?num=$in{'num'}&file=@{[&urlize($in{'file'})]}");

