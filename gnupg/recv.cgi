#!/usr/local/bin/perl
# recv.cgi
# Fetch a key from the keyserver

require './gnupg-lib.pl';
&ReadParse();
&ui_print_header(undef, $text{'recv_title'}, "");

$in{'id'} =~ s/^0x//i;
print "<p>",&text('recv_desc', $in{'id'},
		  "<tt>$config{'keyserver'}</tt>"),"<p>\n";

$cmd = "$gpgpath --keyserver '$config{'keyserver'}' --recv-key '$in{'id'}'";
$out = `$cmd 2>&1`;
if ($?) {
	print "<p>",&text('recv_failed', "<pre>$out</pre>"),"<p>\n";
	}
else {
	@keys = &list_keys();
	($key) = grep { lc($_->{'key'}) eq lc($in{'id'}) } @keys;
	if (!$key) {
		print "<p>",&text('recv_failed', "<pre>$out</pre>"),"<p>\n";
		}
	elsif ($out =~ /not changed/i) {
		print "<p>",&text('recv_same', $key->{'name'}->[0]),"<p>\n";
		}
	else {
		print "<p>",&text('recv_success', $key->{'name'}->[0]),"<p>\n";
		}
	}

if ($in{'return'}) {
	&ui_print_footer($in{'return'}, $in{'returnmsg'});
	}
else {
	&ui_print_footer("list_keys.cgi", $text{'keys_return'},
		"", $text{'index_return'});
	}

