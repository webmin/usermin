#!/usr/local/bin/perl
# index.cgi
# Display a form for changing user details

require './chfn-lib.pl';
&switch_to_remote_user();
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

if ($config{'change_shell'}) {
	print "$text{'index_desc'}<p>\n";
	}
else {
	print "$text{'index_desc2'}<p>\n";
	}

print "<form action=save.cgi method=post>\n";
print "<table border>\n";
print "<tr $tb> <td><b>$text{'index_header'}</b></td> </tr>\n";
print "<tr $cb> <td><table>\n";

@uinfo = split(/,/, $remote_user_info[6]);
if ($config{'change_real'}) {
	print "<tr> <td><b>$text{'index_real'}</b></td>\n";
	print "<td><input name=real size=20 value='$uinfo[0]'></td>\n";
	}

if ($config{'change_office'}) {
	print "<td><b>$text{'index_office'}</b></td>\n";
	print "<td><input name=office size=20 value='$uinfo[1]'></td> </tr>\n";
	}

if ($config{'change_ophone'}) {
	print "<tr> <td><b>$text{'index_ophone'}</b></td>\n";
	print "<td><input name=ophone size=20 value='$uinfo[2]'></td>\n";
	}

if ($config{'change_hphone'}) {
	print "<td><b>$text{'index_hphone'}</b></td>\n";
	print "<td><input name=hphone size=20 value='$uinfo[3]'></td> </tr>\n";
	}

if ($config{'change_shell'}) {
	print "<tr> <td><b>$text{'index_shell'}</b></td>\n";
	print "<td><select name=shell>\n";
	open(SHELL, $config{'shells'} || "/etc/shells");
	while($s = <SHELL>) {
		$s =~ s/\r|\n//g;
		$s =~ s/#.*$//;
		next if ($s !~ /\S/);
		printf "<option %s>%s\n",
			$remote_user_info[8] eq $s ? "selected" : "", $s;
		$found++ if ($remote_user_info[8] eq $s);
		}
	close(SHELL);
	print "<option selected>$remote_user_info[8]\n" if (!$found);
	print "</select></td> </tr>\n";
	}

print "</table></td></tr></table>\n";
print "<input type=submit value='$text{'save'}'></form>\n";

&ui_print_footer("/", $text{'index'});

