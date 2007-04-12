#!/usr/local/bin/perl
# delkey.cgi
# Delete a key, perhaps after asking for confirmation

require './gnupg-lib.pl';
&ReadParse();

@keys = &list_keys();
$key = $keys[$in{'idx'}];
if ($key->{'secret'} && !$in{'confirm'}) {
	# For a secret key, ask the user if he is sure
	&ui_print_header(undef, $text{'delkey_title'}, "");

	print "<form action=delkey.cgi><center>\n";
	print "<input type=hidden name=idx value='$in{'idx'}'>\n";
	print &text('delkey_rusure', $key->{'name'}->[0],
				     $key->{'email'}->[0]),"<p>\n";
	print "<input type=submit name=confirm value='$text{'delkey_ok'}'>\n";
	print "</center></form>\n";

	&ui_print_footer("list_keys.cgi", $text{'keys_return'},
		"", $text{'index_return'});
	}
else {
	# Just do it
	&delete_key($key);
	&redirect("list_keys.cgi");
	}


