#!/usr/local/bin/perl
# edit_comp.cgi
# Display a form for creating or editing a composite folder

require './mailbox-lib.pl';
&ReadParse();

@folders = &list_folders();
if ($in{'new'}) {
	&ui_print_header(undef, $text{'edit_title1'}, "");
	}
else {
	&ui_print_header(undef, $text{'edit_title2'}, "");
	$folder = $folders[$in{'idx'}];
	}

print "<form action=save_comp.cgi>\n";
print "<input type=hidden name=idx value='$in{'idx'}'>\n";
print "<input type=hidden name=new value='$in{'new'}'>\n";
print "<table border>\n";
print "<tr $tb> <td><b>$text{'edit_header'}</b></td> </tr>\n";
print "<tr $cb> <td><table>\n";

print "<tr> <td><b>$text{'edit_mode'}</b></td>\n";
print "<td>$text{'edit_comp'}</td> </tr>\n";

print "<tr> <td><b>$text{'edit_name'}</b></td>\n";
print "<td>",&ui_textbox("name", $folder->{'name'}, 40),"</td> </tr>\n";

print "<tr> <td valign=top><b>$text{'edit_comps'}</b></td>\n";
@names = split(/\t+/, $folder->{'subfoldernames'});
print "<td>\n";
for($i=0; $i<10; $i++) {
	print &ui_select("comp_$i",
		$names[$i],
		[ [ "", "&nbsp;" ],
		  map { [ $_->{'id'} || $_->{'file'} || $_->{'name'},
			  $_->{'name'} ] }
		  grep { $_->{'type'} != 5 &&
			 !$_->{'file'} || -e $_->{'file'} } @folders ]),"<br>\n";
	}
print "</td> </tr>\n";

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

&ui_print_footer($config{'mail_system'} == 4 ? "list_ifolders.cgi"
					     : "list_folders.cgi",
		 $text{'folders_return'});

