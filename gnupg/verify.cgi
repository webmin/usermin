#!/usr/local/bin/perl
# verify.cgi
# Verify the signature on a file

require './gnupg-lib.pl';
&ReadParseMime();

# Get file data
if ($in{'mode'} == 0) {
	$in{'upload'} || &error($text{'verify_eupload'});
	$data = $in{'upload'};
	}
else {
	$in{'local'} || &error($text{'verify_eupload'});
	-r $in{'local'} || &error($text{'verify_elocal'});
	$data = &read_entire_file($in{'local'});
	}

# Get signature data
if ($in{'sigmode'} == 0) {
	$in{'sigupload'} || &error($text{'verify_esigupload'});
	$sigdata = $in{'sigupload'};
	}
elsif ($in{'sigmode'} == 1) {
	$in{'siglocal'} || &error($text{'verify_esigupload'});
	-r $in{'siglocal'} || &error($text{'verify_esiglocal'});
	$sigdata = &read_entire_file($in{'siglocal'});
	}
else {
	$sigdata = undef;
	}

($code, $message) = &verify_data($data, $sigdata);

&ui_print_header(undef, $text{'verify_title'}, "");

$red = "<font color=#ff0000>";
$end = "</font>";
if ($code == 0 || $code == 1) {
	print &text('verify_good', &html_escape($message)),"<p>\n";
	if ($code == 1) {
		print "<b>$red$text{'verify_warning'}$end</b><p>\n";
		}
	}
elsif ($code == 2) {
	print "$red",&text('verify_bad', &html_escape($message)),"$end<p>\n";
	}
elsif ($code == 3) {
	print "$red",&text('verify_noid', &html_escape($message)),"$end<p>\n";
	}
else {
	print "$red",&text('verify_failed', "<pre>$message</pre>"),"$end<p>\n";
	}

&ui_print_footer("", $text{'index_return'});

