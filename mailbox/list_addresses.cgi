#!/usr/local/bin/perl
# Display contents of the user's address book, and allowed and denied addresses

require './mailbox-lib.pl';
&ReadParse();
&ui_print_header(undef, $text{'address_title'}, "");

# Build tabs
$prog = "list_addresses.cgi?mode=";
@tabs = ( [ "users", $text{'address_users'}, $prog."users" ],
	  [ "groups", $text{'address_groups'}, $prog."groups" ] );
if (&foreign_installed("spam")) {
	if (!$userconfig{'white_rec'}) {
		push(@tabs, [ "allow", $text{'address_allow'}, $prog."allow" ]);
		}
	push(@tabs, [ "deny", $text{'address_deny'}, $prog."deny" ]);
	}
push(@tabs, [ "import", $text{'address_import'}, $prog."import" ]);

# Start tabs for users and groups, and maybe spam addresses
print &ui_tabs_start(\@tabs, "mode", $in{'mode'} || "users", 1);

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
		&from_sel() if ($config{'edit_from'});
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
		print "<form action=save_group.cgi ",
		      "method=post enctype=multipart/form-data>\n";
		print "<input type=hidden name=gadd value='$in{'gadd'}'>\n";
		print "<input type=hidden name=gedit value='$in{'gedit'}'>\n";
		}
	print "<table width=100%>\n";
	print "<tr> <td colspan=2 width=10%></td> ",
	      "<td width=20%><b>$text{'address_group'}</b></td> ",
	      "<td width=70%><b>$text{'address_members'}</b></td> ",
	      "</tr>\n";
	foreach $a (@gaddrs) {
		print "<tr> <td width=5% valign=top>\n";
		if ($in{'gedit'} ne $a->[2]) {
			print "<a href='list_addresses.cgi?mode=groups&",
			      "gedit=$a->[2]#editing'>",
			      "$text{'address_edit'}</a>\n";
			}
		else {
			print "<a href=list_addresses.cgi?mode=groups>",
			      "$text{'cancel'}</a>\n";
			}
		print "</td> <td width=5% valign=top>\n";
		print "<a href='save_group.cgi?gdelete=$a->[2]'>",
		      "$text{'address_delete'}</a></td>\n";

		if ($in{'gedit'} eq $a->[2]) {
			# Editing a group
			print "<td width=20% valign=top>",
			      &ui_textbox("group", $a->[0], 20),"</td>\n";
			print "<td width=70% valign=top>",
			      &ui_textarea("members", $a->[1], 5, 60),
			      " ",&address_button("members", 0, 0, 0, 1)," ",
			      &ui_submit($text{'save'}),"</td>\n";
			}
		else {
			# Just show group
			print "<td width=20% valign=top>",
			      &html_escape($a->[0]),"</td>\n";
			print "<td width=70% valign=top>",
			      &html_escape($a->[1]),"</td>\n";
			}
		print "</tr>\n";
		}
	if ($in{'gadd'}) {
		# Adding a group
		print "<tr> <td width=5% valign=top>",
		      "<a href='list_addresses.cgi?mode=groups'>",
		      "$text{'cancel'}</a></td>\n";
		print "<td width=5% valign=top><a name=adding></td>\n";
		print "<td width=20% valign=top>",
		      &ui_textbox("group", undef, 20),
		      "</td>\n";
		print "<td width=70% valign=top>",
		      &ui_textarea("members", undef, 5, 60),
		      " ",&address_button("members", 0, 0, 0, 1)," ",
		      &ui_submit($text{'save'}),"</td>\n";
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

# Show allowed / denied addresses tabs
if (&foreign_installed("spam")) {
	&foreign_require("spam", "spam-lib.pl");
	local $conf = &spam::get_config();

	foreach $m ($userconfig{'white_rec'} ? ( ) :
			( [ "allow", "whitelist_from" ] ),
	 	    [ "deny", "blacklist_from" ]) {
		($mode, $opt) = @$m;

		print &ui_tabs_start_tab("mode", $mode);
		print $text{'address_'.$mode.'desc'},"<p>\n";
		print &ui_form_start("save_allow.cgi", "post");
		print &ui_hidden("mode", $mode);

		@addrs = map { @{$_->{'words'}} } &spam::find($opt, $conf);
		print &ui_textarea("addrs", join("\n", @addrs)."\n", 20, 80,
				   undef, 0, "style='width:90%'");

		print &ui_form_end([ [ undef, $text{'save'} ] ]);
		print &ui_tabs_end_tab();
		}
	}

# Show import tab
print &ui_tabs_start_tab("mode", "import");

print $text{'address_importdesc'},"<p>\n";
print &ui_form_start("import.cgi", "form-data");
print &ui_table_start(undef, undef, 2);

# Import source
print &ui_table_row($text{'address_importsrc'},
	&ui_radio_table("src", 0,
		[ [ 0, $text{'address_importsrc0'}, &ui_upload("upload") ],
		  [ 1, $text{'address_importsrc1'},
		    &ui_textarea("paste", undef, 5, 60) ] ])."<br>\n".
	$text{'address_importformat'});

# Import format
print &ui_table_row($text{'address_importfmt'},
	&ui_radio("fmt", "csv", [ [ 'csv', $text{'address_importcsv'} ],
				  [ 'vcard', $text{'address_importvcard'} ] ]));

# Duplicate handling
print &ui_table_row($text{'address_importdup'},
	&ui_radio("dup", 0, [ [ 0, $text{'address_importdup0'} ],
			      [ 1, $text{'address_importdup1'} ] ]));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'address_importok'} ] ]);

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

