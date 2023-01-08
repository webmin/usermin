#!/usr/local/bin/perl
# save_sig.cgi
# Update the user's signature file
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in, %userconfig);

require './mailbox-lib.pl';
if ($userconfig{'sig_file'} eq '*') {
	# Switch to ~/.signature
	$userconfig{'sig_file'} = '.signature';
	&save_user_module_config();
	}
my $sf = &get_signature_file();
$sf || &error($text{'sig_enone'});
&ReadParseMime();

$in{'sig'} =~ s/\r//g;
$in{'sig'} =~ s/\n*$/\n/;
no strict "subs";
&open_tempfile(SIG, ">$sf") || &error(&text('sig_eopen', $!));
&print_tempfile(SIG, $in{'sig'});
&close_tempfile(SIG);
use strict "subs";
&redirect("");
