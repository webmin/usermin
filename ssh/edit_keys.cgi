#!/usr/local/bin/perl
# edit_keys.cgi
# Display the user's private and public keys

require './ssh-lib.pl';
&ui_print_header(undef, $text{'keys_title'}, "");

print "$text{'keys_desc1'}<br>\n";

if (-r "$ssh_directory/id_rsa") {
	$keyfile = "id_rsa";
	}
else {
	if (-r "$ssh_directory/id_dsa") {
		$keyfile = "id_dsa";
		}
	else {
		$keyfile = "identity";
		}
	}

print "<form action=save_private.cgi/$keyfile method=post enctype=multipart/form-data>\n";
print "<table width=100%>\n";
print "<tr> <td><input type=submit name=download ",
      "value='$text{'keys_download'}'></td>\n";
print "<td>$text{'keys_downloadmsg'}</td> </tr>\n";

print "<tr> <td nowrap><input type=submit name=upload value='$text{'keys_upload'}'> ",
      "<input type=file name=private></td>\n";
print "<td>$text{'keys_uploadmsg'}</td> </tr>\n";
print "</table></form>\n";

print "<hr>\n";
print "<form action=save_public.cgi method=post>\n";
print "$text{'keys_desc2'}<br>\n";

print "<table border>\n";
print "<tr $tb> <td><b>$text{'keys_public'}</b></td> </tr>\n";
print "<tr $cb> <td><textarea name=public rows=15 cols=70 wrap=on>";
open(PRIVATE, "$ssh_directory/id_rsa.pub") ||
	open(PRIVATE, "$ssh_directory/id_dsa.pub") ||
	open(PRIVATE, "$ssh_directory/identity.pub");
while(<PRIVATE>) { print; }
close(PRIVATE);
print "</textarea></td></tr></table>\n";
#print $ssh_directory;
print "<input type=submit value='$text{'save'}'></form>\n";

&ui_print_footer("", $text{'index_return'});

