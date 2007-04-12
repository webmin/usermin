#!/usr/local/bin/perl
# index.cgi
# Display a form for choosing a new password

require './changepass-lib.pl';
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

print "$text{'index_desc1'}<br>\n";
print "$text{'index_desc2'}<br>\n" if (&has_command($config{'smbpasswd'}));

print "<form action=changepass.cgi method=post>\n";
print "<table>\n";

print "<tr> <td><b>$text{'index_for'}</b></td>\n";
print "<td><tt>$remote_user</tt>\n";
if ($remote_user_info[6]) {
	print " ($remote_user_info[6])\n";
	}
print "</td> </tr>\n";

print "<tr> <td><b>$text{'index_old'}</b></td>\n";
print "<td><input name=old type=password size=20></td> </tr>\n";

print "<tr> <td><b>$text{'index_new1'}</b></td>\n";
print "<td><input name=new1 type=password size=20></td> </tr>\n";

print "<tr> <td><b>$text{'index_new2'}</b></td>\n";
print "<td><input name=new2 type=password size=20></td> </tr>\n";

print "</table><br>\n";
print "<input type=submit value='$text{'index_change'}'></form>\n";

&ui_print_footer("/", $text{'index'});

