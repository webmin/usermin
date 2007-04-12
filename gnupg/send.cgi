#!/usr/local/bin/perl
# send.cgi
# Send a key to the keyserver

require './gnupg-lib.pl';
&ReadParse();
&ui_print_header(undef, $text{'send_title'}, "");

@keys = &list_keys();
$key = $keys[$in{'idx'}];
print &text('send_desc', $key->{'name'}->[0],
		  "<tt>$config{'keyserver'}</tt>"),"<p>\n";

$cmd = "$gpgpath --keyserver '$config{'keyserver'}' --send-key '$key->{'name'}->[0]'";
$out = `$cmd 2>&1`;
if ($?) {
	print "<p>",&text('send_failed', "<pre>$out</pre>"),"<p>\n";
	}
else {
	print "<p>$text{'send_success'}<p>\n";
	}

&ui_print_footer("list_keys.cgi", $text{'keys_return'},
	"", $text{'index_return'});

