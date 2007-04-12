#!/usr/local/bin/perl
# edit_encrypt.cgi
# Display a form for choosing a file to encrypt and a key to use

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'encrypt_title'}, "");

print "$text{'encrypt_desc'}<p>\n";
print "<form action=encrypt.cgi/output.gpg method=post enctype=multipart/form-data>\n";
print "<table>\n";
print "<tr> <td valign=top><b>$text{'encrypt_mode'}</b></td>\n";
print "<td><input type=radio name=mode value=0 checked> $text{'encrypt_mode0'}\n";
print "<input type=file name=upload><br>\n";
print "<input type=radio name=mode value=1> $text{'encrypt_mode1'}\n";
print "<input name=local size=35> ",&file_chooser_button("local"),"</td> </tr>\n";

@keys = &list_keys();
print "<tr> <td valign=top><b>$text{'encrypt_key'}</b></td>\n";
print "<td><select name=idx size=5 multiple>\n";
foreach $k (@keys) {
	print "<option value=$k->{'index'}>$k->{'name'}->[0]\n";
	}
print "</select></td> </tr>\n";

print "<tr> <td><b>$text{'encrypt_ascii'}</b></td>\n";
print "<td><input type=radio name=ascii value=1> $text{'yes'}\n";
print "<input type=radio name=ascii value=0 checked> $text{'no'}</td> </tr>\n";

print "</table>\n";
print "<input type=submit value='$text{'encrypt_ok'}'></form>\n";

&ui_print_footer("", $text{'index_return'});

