#!/usr/local/bin/perl
# decrypt.cgi
# Decrypt and output a file

require './gnupg-lib.pl';
&ReadParseMime();

if ($in{'mode'} == 0) {
	$in{'upload'} || &error($text{'decrypt_eupload'});
	$data = $in{'upload'};
	}
else {
	$in{'local'} || &error($text{'decrypt_eupload'});
	-r $in{'local'} || &error($text{'decrypt_elocal'});
	$data = &read_entire_file($in{'local'});
	}

$rv = &decrypt_data($data, \$plain);
if ($rv) {
	&error(&text('decrypt_egpg', $rv));
	}

local $temp = &transname();
&write_entire_file($temp, $plain);
$type = `file $temp`;
unlink($temp);
if ($type =~ /text$/) {
	print "Content-type: text/plain\n\n";
	}
else {
	print "Content-type: application/octet-stream\n\n";
	}
print $plain;

