#!/usr/local/bin/perl
# edit_sign.cgi
# Display a form for choosing a file to sign

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'sign_title'}, "");

print "$text{'sign_desc'}<p>\n";
print "<form action=sign.cgi/signed.txt method=post enctype=multipart/form-data>\n";
print "<table>\n";
print "<tr> <td valign=top><b>$text{'sign_mode'}</b></td>\n";
print "<td><input type=radio name=mode value=0 checked> $text{'sign_mode0'}\n";
print "<input type=file name=upload><br>\n";
print "<input type=radio name=mode value=1> $text{'sign_mode1'}\n";
print "<input name=local size=35> ",&file_chooser_button("local"),"</td> </tr>\n";

@keys = &list_secret_keys();
print "<tr> <td><b>$text{'sign_key'}</b></td>\n";
print "<td><select name=idx>\n";
foreach $k (@keys) {
	print "<option value=$k->{'index'}>$k->{'name'}->[0]\n";
	}
print "</select></td> </tr>\n";

print "<tr> <td><b>$text{'sign_ascii'}</b></td>\n";
print "<td><input type=radio name=ascii value=1 checked> $text{'yes'}\n";
print "<input type=radio name=ascii value=0> $text{'no'}</td> </tr>\n";

print "<tr> <td><b>$text{'sign_sep'}</b></td>\n";
print "<td><input type=radio name=sep value=1> $text{'yes'}\n";
print "<input type=radio name=sep value=0 checked> $text{'no'}</td> </tr>\n";

print "</table>\n";
print "<input type=submit value='$text{'sign_ok'}'></form>\n";

&ui_print_footer("", $text{'index_return'});

