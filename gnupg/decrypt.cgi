#!/usr/local/bin/perl
# decrypt.cgi
# Decrypt and output a file

require './gnupg-lib.pl';
&ReadParseMime();

if ($in{'mode'} == 0) {
	# Uploaded file
	$in{'upload'} || &error($text{'decrypt_eupload'});
	$data = $in{'upload'};
	}
elsif ($in{'mode'} == 1) {
	# File on server
	$in{'local'} || &error($text{'decrypt_eupload'});
	-r $in{'local'} || &error($text{'decrypt_elocal'});
	$data = &read_file_contents($in{'local'});
	}
elsif ($in{'mode'} == 2) {
	# Pasted text
	$data = $in{'text'};
	$data =~ s/\r//g;
	}

@keys = &list_keys();
$key = $keys[$in{'idx'}];
$pass = &get_passphrase($key);
if (!defined($pass)) {
	&error($text{'sign_epass'}.". ".
	  &text('gnupg_canset', "/gnupg/edit_key.cgi?idx=$in{'idx'}").".");
	}

$rv = &decrypt_data($data, \$plain, $key);
if ($rv) {
	&error(&text('decrypt_egpg', $rv));
	}

local $temp = &transname();
&write_file_contents($temp, $plain);
$type = &backquote_command("file ".quotemeta($temp)." 2>/dev/null");
unlink($temp);
if ($type =~ /text$/) {
	print "Content-type: text/plain\n\n";
	}
else {
	print "Content-type: application/octet-stream\n\n";
	}
print $plain;

