#!/usr/local/bin/perl
# list_addresses.cgi
# Display contents of the user's address book

require './mailbox-lib.pl';
&ReadParse();
&ui_print_header(undef, $text{'address_title'}, "");

# Start tabs for users and groups
$prog = "list_addresses.cgi?mode=";
print &ui_tabs_start([ [ "users", $text{'address_users'}, $prog."users" ],
		       [ "groups", $text{'address_groups'}, $prog."groups" ] ],
		     "mode", $in{'mode'} || "users", 1);

print &ui_tabs_start_tab("mode", "users");
@addrs = &list_addresses();
print "$text{'address_desc'}<p>\n";
if (@addrs || $in{'add'}) {
	if ($in{'add'} || $in{'edit'} ne '') {
		print "<form action=save_address.cgi>\n";
		print "<input type=hidden name=add value='$in{'add'}'>\n";
		print "<input type=hidden name=edit value='$in{'edit'}'>\n";
		}
	print "<table width=100%>\n";
	print "<tr> <td colspan=2 width=10%></td> ",
	      "<td width=40%><b>$text{'address_addr'}</b></td> ",
	      "<td width=40%><b>$text{'address_name'}</b></td> ",
	      $config{'edit_from'} ? "<td width=10% nowrap><b>$text{'address_from'}</b></td> " : "",
	      "</tr>\n";
	foreach $a (@addrs) {
		next if (!defined($a->[2]));
		print "<tr> <td width=5%>\n";
		if ($in{'edit'} ne $a->[2]) {
			print "<a href='list_addresses.cgi?",
			      "mode=users&edit=$a->[2]#editing'>",
			      "$text{'address_edit'}</a>\n";
			}
		else {
			print "<a href=list_addresses.cgi?mode=users>",
			      "$text{'cancel'}</a>\n";
			}
		print "</td> <td width=5%>\n";
		print "<a href='save_address.cgi?delete=$a->[2]'>",
		      "$text{'address_delete'}</a></td>\n";

		if ($in{'edit'} eq $a->[2]) {
			# Editing this row
			print "<td width=40%><input name=addr size=30 value='",
				&html_escape($a->[0]),"'><a name=editing></td>\n";
			print "<td width=40%><input name=name size=30 value='",
				&html_escape($a->[1]),"'></td>\n";
			if ($config{'edit_from'}) {
				&from_sel($a->[3]);
				}
			else {
				print "<input type=hidden name=from value='$a->[3]'>\n";
				}
			print "<td><input type=submit value='$text{'save'}'></td>\n";
			}
		else {
			# Just showing this row
			print "<td width=40%>$a->[0]</td>\n";
			print "<td width=40%>",$a->[1] ? $a->[1] : "<br>","</td>\n";
			print "<td>",$a->[3] == 1 ? $text{'yes'} :
				     $a->[3] == 2 ? $text{'address_yd'} :
					     	    $text{'no'},"</td>\n"
				if ($config{'edit_from'});
			}
		print "</tr>\n";
		}
	if ($in{'add'}) {
		print "<tr> <td width=5%><a href='list_addresses.cgi?",
		      "mode=users'>$text{'cancel'}</a></td>\n";
		print "<td width=5%><a name=adding></td>\n";
		print "<td width=40%><input name=addr size=30></td>\n";
		print "<td width=40%><input name=name size=30></td>\n";
		print &from_sel() if ($config{'edit_from'});
		print "<td><input type=submit value='$text{'save'}'></td>\n";
		print "</tr>\n";
		}
	print "</table>\n";
	if ($in{'add'} || $in{'edit'} ne '') {
		print "</form>\n";
		}
	}
else {
	print "<b>$text{'address_none'}</b> <p>\n";
	}
print "<a href='list_addresses.cgi?mode=users&add=1#adding'>",
      "$text{'address_add'}</a> <br>\n"
	if (!$in{'add'});
print &ui_tabs_end_tab();

print &ui_tabs_start_tab("mode", "groups");
@gaddrs = grep { defined($_->[2]) } &list_address_groups();
print "$text{'address_gdesc'}<p>\n";
if (@gaddrs || $in{'gadd'}) {
	if ($in{'gadd'} || $in{'gedit'} ne '') {
		print "<form action=save_group.cgi>\n";
		print "<input type=hidden name=gadd value='$in{'gadd'}'>\n";
		print "<input type=hidden name=gedit value='$in{'gedit'}'>\n";
		}
	print "<table width=100%>\n";
	print "<tr> <td colspan=2 width=10%></td> ",
	      "<td width=20%><b>$text{'address_group'}</b></td> ",
	      "<td width=70%><b>$text{'address_members'}</b></td> ",
	      "</tr>\n";
	foreach $a (@gaddrs) {
		print "<tr> <td width=5%>\n";
		if ($in{'gedit'} ne $a->[2]) {
			print "<a href='list_addresses.cgi?mode=groups&",
			      "gedit=$a->[2]#editing'>",
			      "$text{'address_edit'}</a>\n";
			}
		else {
			print "<a href=list_addresses.cgi?mode=groups>",
			      "$text{'cancel'}</a>\n";
			}
		print "</td> <td width=5%>\n";
		print "<a href='save_group.cgi?gdelete=$a->[2]'>",
		      "$text{'address_delete'}</a></td>\n";

		if ($in{'gedit'} eq $a->[2]) {
			print "<td width=20%><input name=group size=15 value='",
				&html_escape($a->[0]),"'><a name=editing></td>\n";
			print "<td width=70%><input name=members size=60 value='",
				&html_escape($a->[1]),"'> ",
				&address_button("members", 0, 0, 0, 1),"\n";
			print "<input type=submit value='$text{'save'}'></td>\n";
			}
		else {
			print "<td width=20%>$a->[0]</td>\n";
			print "<td width=70%>",&html_escape($a->[1]),"</td>\n";
			}
		print "</tr>\n";
		}
	if ($in{'gadd'}) {
		print "<tr> <td width=5%><a href='list_addresses.cgi?",
		      "mode=groups'>$text{'cancel'}</a></td>\n";
		print "<td width=5%><a name=adding></td>\n";
		print "<td width=20%><input name=group size=20></td>\n";
		print "<td width=70%><input name=members size=60> ",
		      &address_button("members", 0, 0, 0, 1),"\n";
		print "<input type=submit value='$text{'save'}'></td>\n";
		print "</tr>\n";
		}
	print "</table>\n";
	if ($in{'gadd'} || $in{'gedit'} ne '') {
		print "</form>\n";
		}
	}
else {
	print "<b>$text{'address_gnone'}</b> <p>\n";
	}
print "<a href='list_addresses.cgi?mode=groups&gadd=1#adding'>",
      "$text{'address_gadd'}</a> <br>\n"
	if (!$in{'gadd'});
print &ui_tabs_end_tab();
print &ui_tabs_end(1);

&ui_print_footer("", $text{'mail_return'});

sub from_sel
{
print "<td><select name=from>\n";
printf "<option value=0 %s> %s\n",
	$_[0] == 0 ? "selected" : "", $text{'no'};
printf "<option value=1 %s> %s\n",
	$_[0] == 1 ? "selected" : "", $text{'yes'};
printf "<option value=2 %s> %s\n",
	$_[0] == 2 ? "selected" : "", $text{'address_yd'};
print "</select></td>\n";
}

