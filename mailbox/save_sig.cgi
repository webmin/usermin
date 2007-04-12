#!/usr/local/bin/perl
# save_sig.cgi
# Update the user's signature file

require './mailbox-lib.pl';
$sf = &get_signature_file();
$sf || &error($text{'sig_enone'});
&ReadParseMime();

$in{'sig'} =~ s/\r//g;
$in{'sig'} =~ s/\n*$/\n/;
&open_tempfile(SIG, ">$sf") || &error(&text('sig_eopen', $!));
&print_tempfile(SIG, $in{'sig'});
&close_tempfile(SIG);
&redirect("");

