#!/usr/local/bin/perl
# edit_decrypt.cgi
# Display a form for choosing a file to decrypt

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'decrypt_title'}, "");

print "$text{'decrypt_desc'}<p>\n";
print "<form action=decrypt.cgi/output.txt method=post enctype=multipart/form-data>\n";
print "<table>\n";
print "<tr> <td valign=top><b>$text{'decrypt_mode'}</b></td>\n";
print "<td><input type=radio name=mode value=0 checked> $text{'decrypt_mode0'}\n";
print "<input type=file name=upload><br>\n";
print "<input type=radio name=mode value=1> $text{'decrypt_mode1'}\n";
print "<input name=local size=35> ",&file_chooser_button("local"),"</td> </tr>\n";

print "</table>\n";
print "<input type=submit value='$text{'decrypt_ok'}'></form>\n";

&ui_print_footer("", $text{'index_return'});

