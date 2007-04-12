#!/usr/local/bin/perl
# edit_verify.cgi
# Display a form for choosing a file to verify

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'verify_title'}, "");

print &text('verify_desc', 'edit_decrypt.cgi'),"<p>\n";
print "<form action=verify.cgi method=post enctype=multipart/form-data>\n";
print "<table>\n";

print "<tr> <td valign=top><b>$text{'verify_mode'}</b></td> <td>\n";
print "<input type=radio name=mode value=0 checked> $text{'verify_mode0'}\n";
print "<input type=file name=upload><br>\n";
print "<input type=radio name=mode value=1> $text{'verify_mode1'}\n";
print "<input name=local size=35> ",&file_chooser_button("local"),"</td> </tr>\n";

print "<tr> <td valign=top><b>$text{'verify_sig'}</b></td> <td>\n";
print "<input type=radio name=sigmode value=2 checked> $text{'verify_mode2'}<br>\n";
print "<input type=radio name=sigmode value=0> $text{'verify_mode0'}\n";
print "<input type=file name=sigupload><br>\n";
print "<input type=radio name=sigmode value=1> $text{'verify_mode1'}\n";
print "<input name=siglocal size=35> ",&file_chooser_button("local"),"</td> </tr>\n";

print "</table>\n";
print "<input type=submit value='$text{'verify_ok'}'></form>\n";

&ui_print_footer("", $text{'index_return'});

