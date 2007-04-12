#!/usr/local/bin/perl
# edit_folder.cgi
# Display a form for creating or editing a folder of some kind

require './mailbox-lib.pl';
&ReadParse();

if ($in{'new'}) {
	&ui_print_header(undef, $text{'edit_title1'}, "");
	$mode = $in{'mode'};
	}
else {
	&ui_print_header(undef, $text{'edit_title2'}, "");
	@folders = &list_folders();
	$folder = $folders[$in{'idx'}];
	$mode = $folder->{'mode'};
	}

print "<form action=save_folder.cgi>\n";
print "<input type=hidden name=idx value='$in{'idx'}'>\n";
print "<input type=hidden name=new value='$in{'new'}'>\n";
print "<input type=hidden name=mode value='$mode'>\n";
print "<table border>\n";
print "<tr $tb> <td><b>$text{'edit_header'}</b></td> </tr>\n";
print "<tr $cb> <td><table>\n";

print "<tr> <td><b>$text{'edit_mode'}</b></td>\n";
print "<td>",&text("edit_mode$mode", "<tt>$folders_dir</tt>"),"</td> </tr>\n";

if ($mode == 0) {
	# Adding/editing a new file or directory to ~/mail
	print "<tr> <td><b>$text{'edit_name'}</b></td>\n";
	printf "<td><input name=name size=40 value='%s'></td> </tr>\n",
		$folder->{'name'};

	print "<tr> <td><b>$text{'edit_type'}</b></td>\n";
	if ($in{'new'} && $folders_dir eq "$remote_user_info[7]/Maildir") {
		# A new folder, but under a Maildir .. so it must be maildir too
		print "<td>",$text{'edit_type1'},"</td> </tr>\n";
		print &ui_hidden("type", 1),"\n";
		}
	elsif ($in{'new'}) {
		# Can choose the type of a new folder
		print "<td><input type=radio name=type value=0 checked> ",
		      "$text{'edit_type0'}\n"; 
		print "<input type=radio name=type value=1> ",
		      "$text{'edit_type1'}\n";
		print "<input type=radio name=type value=3> ",
		      "$text{'edit_type3'}\n" if ($userconfig{'mailbox_recur'});
		print "</td> </tr>\n";
		}
	else {
		# Show type of existing folder
		print "<td>",$text{'edit_type'.$folder->{'type'}},
		      "</td> </tr>\n";
		}
	}
elsif ($mode == 1) {
	# Adding/editing an external file or directory
	print "<tr> <td><b>$text{'edit_name'}</b></td>\n";
	printf "<td><input name=name size=40 value='%s'></td> </tr>\n",
		$folder->{'name'};

	print "<tr> <td><b>$text{'edit_file'}</b></td>\n";
	printf "<td><input name=file size=40 value='%s'> %s</td> </tr>\n",
		$folder->{'file'}, &file_chooser_button("file");
	}
elsif ($mode == 2) {
	# Selecting the sent mail folder
	local $sf = "$folders_dir/sentmail";
	print "<tr> <td valign=top><b>$text{'edit_sent'}</b></td> <td>\n";
	printf "<input type=radio name=sent_def value=1 %s> %s<br>\n",
		$folder->{'file'} eq $sf ? "checked" : "", $text{'edit_sent1'};
	printf "<input type=radio name=sent_def value=0 %s> %s\n",
		$folder->{'file'} eq $sf ? "" : "checked", $text{'edit_sent0'};
	printf "<input name=sent size=40 value='%s'> %s</td> </tr>\n",
		$folder->{'file'} eq $sf ? "" : $folder->{'file'},
		&file_chooser_button("sent");
	}

&show_folder_options($folder, $mode);

print "</table></td></tr></table>\n";
if ($in{'new'}) {
	print "<input type=submit value='$text{'create'}'>\n";
	}
else {
	print "<input type=submit value='$text{'save'}'>\n";
	print "<input type=submit name=delete value='$text{'delete'}'>\n"
		if ($mode != 2);
	}
print "</form>\n";

&ui_print_footer("list_folders.cgi", $text{'folders_return'});

