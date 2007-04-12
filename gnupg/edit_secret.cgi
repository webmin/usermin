#!/usr/local/bin/perl
# edit_secret.cgi
# Display a form for adding an additional secret key

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'secret_title'}, "");

print "$text{'secret_desc'}<br>\n";
print "<form action=secret.cgi method=post>\n";
print "<input type=hidden name=newkey value=1>\n";
print "<table>\n";
print "<tr> <td><b>$text{'secret_name'}</b></td>\n";
print "<td><input name=name size=30 value=''></td> </tr>\n";
print "<tr> <td><b>$text{'index_email'}</b></td>\n";
print "<td><input name=email size=30></td> </tr>\n";
print "<tr> <td><b>$text{'index_comment'}</b></td>\n";
print "<td><input name=comment size=30></td> </tr>\n";
print "<tr> <td><b>$text{'index_size'}</b></td>\n";
print "<td><select name=size>\n";
print "<option selected value=''>$text{'default'}\n";
foreach $s (768, 1024, 2048, 4096, 8192) {
	print "<option>$s\n";
	}
print "</select></td> </tr>\n";
print "<tr> <td><b>$text{'index_pass'}</b></td>\n";
print "<td><input name=pass type=password size=20></td> </tr>\n";
print "</table>\n";
print "<input type=submit value='$text{'secret_setup'}'></form>\n";

&ui_print_footer("", $text{'index_return'});

