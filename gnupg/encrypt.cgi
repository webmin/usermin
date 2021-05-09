#!/usr/local/bin/perl
# encrypt.cgi
# Encrypt and output a file

require './gnupg-lib.pl';
&ReadParseMime();

if ($in{'mode'} == 0) {
	# Uploaded file
	$in{'upload'} || &error($text{'encrypt_eupload'});
	$data = $in{'upload'};
	}
elsif ($in{'mode'} == 1) {
	# File on server
	$in{'local'} || &error($text{'encrypt_eupload'});
	-r $in{'local'} || &error($text{'encrypt_elocal'});
	$data = &read_file_contents($in{'local'});
	}
elsif ($in{'mode'} == 2) {
	# Pasted text
	$data = $in{'text'};
	$data =~ s/\r//g;
	}

@keys = &list_keys();
@keys = map { $keys[$_] } split(/\0/, $in{'idx'});
$rv = &encrypt_data($data, \$crypt, \@keys, $in{'ascii'});
if ($rv) {
	&error(&text('encrypt_egpg', "<pre>$rv</pre>"));
	}

if ($in{'ascii'}) {
	print "Content-type: text/plain\n\n";
	}
else {
	print "Content-type: application/octet-stream\n\n";
	}
print $crypt;

