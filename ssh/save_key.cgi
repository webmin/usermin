#!/usr/local/bin/perl
# Update a private key

require './ssh-lib.pl';
&ReadParseMime();
&error_setup($text{'ekey_err'});
@keys = &list_ssh_keys();
($key) = grep { $_->{'private_file'} eq $in{'file'} } @keys;
$key || &error($text{'ekey_egone'});

# Validate inputs
$in{'private'} =~ /\S/ || &error($text{'ekey_eprivate'});

# Write out the file
&open_tempfile(PRIVATE, ">$key->{'private_file'}");
&print_tempfile(PRIVATE, $in{'private'});
&close_tempfile(PRIVATE);

# Re-generate public key
$cmd = "ssh-keygen -y -f ".quotemeta($key->{'private_file'});
$out = &backquote_command("$cmd </dev/null 2>&1");
if ($out =~ /((\d+)\s+(\d+)\s+(\d+))$/) {
	$public = $1;
	}
elsif ($out =~ /((\S+)\s+([A-Za-z0-9\/=\+]+))$/) {
	$public = $1;
	}
else {
	&error($text{'ekey_epublic'});
	}
&open_tempfile(PRIVATE, ">$key->{'public_file'}");
&print_tempfile(PRIVATE, $public);
&close_tempfile(PRIVATE);

&redirect("list_keys.cgi");
