#!/usr/local/bin/perl
# recv.cgi
# Fetch a key from the keyserver

require './gnupg-lib.pl';
&ReadParse();
&ui_print_header(undef, $text{'recv_title'}, "");

$in{'id'} =~ s/^0x//i;
print "<p>",&text('recv_desc', $in{'id'},
		  "<tt>$config{'keyserver'}</tt>"),"<p>\n";

($ok, $msg) = &fetch_gpg_key($in{'id'});
if ($ok == 1 || $ok == 3) {
	print "<p>",&text('recv_failed', "<pre>$msg</pre>"),"<p>\n";
	}
elsif ($ok == 2) {
	print "<p>",&text('recv_same', $msg->{'name'}->[0]),"<p>\n";
	}
else {
	print "<p>",&text('recv_success', $msg->{'name'}->[0]),"<p>\n";
	}

if ($in{'return'}) {
	&ui_print_footer($in{'return'}, $in{'returnmsg'});
	}
else {
	&ui_print_footer("list_keys.cgi", $text{'keys_return'},
			 "", $text{'index_return'});
	}

