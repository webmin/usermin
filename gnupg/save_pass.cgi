#!/usr/local/bin/perl
# save_pass.cgi
# Sets the passphrase for some key

require './gnupg-lib.pl';
&ReadParse();
@keys = &list_keys();
&put_passphrase($in{'pass'}, $keys[$in{'idx'}]);
&redirect("list_keys.cgi");

