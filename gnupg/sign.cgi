#!/usr/local/bin/perl
# sign.cgi
# Sign a file and output the result

require './gnupg-lib.pl';
&ReadParseMime();

# Get the data to sign
if ($in{'mode'} == 0) {
	# Uploaded file
	$in{'upload'} || &error($text{'sign_eupload'});
	$data = $in{'upload'};
	}
elsif ($in{'mode'} == 1) {
	# Local file
	$in{'local'} || &error($text{'sign_eupload'});
	-r $in{'local'} || &error($text{'sign_elocal'});
	$data = &read_file_contents($in{'local'});
	}
elsif ($in{'mode'} == 2) {
	# Text box
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

$rv = &sign_data($data, \$signed, $key, $in{'sep'} ? 2 :
					$in{'ascii'} ? 1 : 0);

if ($rv) {
	&error(&text('sign_egpg', "<pre>$rv</pre>"));
	}

if ($in{'ascii'}) {
	print "Content-type: text/plain\n\n";
	}
else {
	print "Content-type: application/octet-stream\n\n";
	}
print $signed;


