#!/usr/local/bin/perl
# edit_pop3.cgi
# Display a form for creating or editing a POP3 folder

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

print "<form action=save_pop3.cgi>\n";
print "<input type=hidden name=idx value='$in{'idx'}'>\n";
print "<input type=hidden name=new value='$in{'new'}'>\n";
print "<input type=hidden name=mode value='$mode'>\n";
print "<table border>\n";
print "<tr $tb> <td><b>$text{'edit_header'}</b></td> </tr>\n";
print "<tr $cb> <td><table>\n";

print "<tr> <td><b>$text{'edit_mode'}</b></td>\n";
print "<td>$text{'edit_pop3'}</td> </tr>\n";

print "<tr> <td><b>$text{'edit_name'}</b></td>\n";
printf "<td><input name=name size=40 value='%s'></td> </tr>\n",
	$folder->{'name'};

print "<tr> <td><b>$text{'edit_server'}</b></td>\n";
printf "<td><input name=server size=30 value='%s'></td> </tr>\n",
	$folder->{'server'};

print "<tr> <td><b>$text{'edit_port'}</b></td> <td>\n";
printf "<input type=radio name=port_def value=1 %s> %s (%d)\n",
	$folder->{'port'} ? "" : "checked", $text{'default'}, $pop3_port;
printf "<input type=radio name=port_def value=0 %s>\n",
	$folder->{'port'} ? "checked" : "";
printf "<input name=port size=6 value='%s'></td> </tr>\n",
	$folder->{'port'};

print "<tr> <td><b>$text{'edit_user'}</b></td>\n";
printf "<td><input name=user size=20 value='%s'></td> </tr>\n",
	$folder->{'user'};

print "<tr> <td><b>$text{'edit_pass'}</b></td>\n";
printf "<td><input type=password name=pass size=20 value='%s'></td> </tr>\n",
	$folder->{'pass'};

&show_folder_options($folder);

print "</table></td></tr></table>\n";
if ($in{'new'}) {
	print "<input type=submit value='$text{'create'}'>\n";
	}
else {
	print "<input type=submit value='$text{'save'}'>\n";
	print "<input type=submit name=delete value='$text{'delete'}'>\n";
	}
print "</form>\n";

&ui_print_footer("list_folders.cgi", $text{'folders_return'});

