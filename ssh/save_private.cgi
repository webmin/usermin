#!/usr/local/bin/perl
# save_private.cgi
# Upload or download the private key file

require './ssh-lib.pl';
&ReadParseMime();
if ($in{'download'}) {
	# Force a browser download of the file
	print "Content-type: application/octet-stream\n\n";
	open(PRIVATE, "$ssh_directory/id_dsa") ||
	  open(PRIVATE, "$ssh_directory/identity");
	while(<PRIVATE>) { print; }
	close(PRIVATE);
	}
else {
	# Save the new key file
	&error_setup($text{'keys_err'});
	$in{'private'} || &error($text{'keys_eprivate'});
	$in{'private'} =~ /^SSH\s+PRIVATE\s+KEY/i || &error($text{'keys_eformat'});
	if (-r "$ssh_directory/id_dsa") {
		&open_tempfile(PRIVATE, ">$ssh_directory/id_dsa", 1) ||
			&error(&text('keys_epriwrite', $!));
		}
	else {
		&open_tempfile(PRIVATE, ">$ssh_directory/identity", 1) ||
			&error(&text('keys_epriwrite', $!));
		}
	&print_tempfile(PRIVATE, $in{'private'});
	&close_tempfile(PRIVATE);
	&redirect("edit_keys.cgi");
	}

