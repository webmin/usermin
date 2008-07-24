#!/usr/local/bin/perl
# save_public.cgi
# Save the current public key

require './ssh-lib.pl';
&ReadParse();
&error_setup($text{'keys_perr'});
$in{'public'} =~ s/\r//g;
$in{'public'} =~ /^(.*)/;
$public = $1;
$public || &error($text{'keys_epublic'});
if (-r "$ssh_directory/id_rsa.pub") {
	&open_tempfile(PUBLIC, ">$ssh_directory/id_rsa.pub", 1) ||
		&error(&text('keys_epubwrite', $!));
	}
else {
	if (-r "$ssh_directory/id_dsa.pub") {
		&open_tempfile(PUBLIC, ">$ssh_directory/id_dsa.pub", 1) ||
			&error(&text('keys_epubwrite', $!));
		}
	else {
		&open_tempfile(PUBLIC, ">$ssh_directory/identity.pub", 1) ||
			&error(&text('keys_epubwrite', $!));
		}
	}
&print_tempfile(PUBLIC, $public,"\n");
&close_tempfile(PUBLIC);
&redirect("edit_keys.cgi");

