#!/usr/local/bin/perl
# search_form.cgi
# Display a form for searching a mailbox

require './mailbox-lib.pl';
&ReadParse();
@folders = &list_folders_sorted();
($folder) = grep { $_->{'index'} == $in{'folder'} } @folders;
&set_module_index($in{'folder'});
&ui_print_header(undef, $text{'sform_title'}, "");

print "<form action=mail_search.cgi>\n";
print "<input type=radio name=and value=1 checked> $text{'sform_and'}\n";
print "<input type=radio name=and value=0> $text{'sform_or'}<p>\n";

print "<table>\n";
#print "<tr> <td><b>$text{'sform_field'}</b></td> ",
#      "<td><b>$text{'sform_mode'}</b></td> ",
#      "<td><b>$text{'sform_for'}</b></td> </tr>\n";
for($i=0; $i<=9; $i++) {
	print "<tr>\n";
	print "<td>$text{'sform_where'}</td>\n";
	print "<td><select name=field_$i>\n";
	print "<option value=''>&nbsp;\n";
	foreach $f ('from', 'subject', 'to', 'cc', 'date', 'body', 'headers', 'all', 'size') {
		print "<option value=$f>",$text{"sform_$f"},"\n";
		}
	print "</select></td>\n";

	print "<td><select name=neg_$i>\n";
	print "<option value=0 checked>$text{'sform_neg0'}\n";
	print "<option value=1>$text{'sform_neg1'}\n";
	print "</select></td>\n";

	print "<td>$text{'sform_text'}</td>\n";
	print "<td><input name=what_$i size=30></td>\n";
	print "</tr>\n";
	}
print "</table>\n";

# Status to find
print "<table>\n";
print "<tr> <td>$text{'search_status'}</td>\n";
print "<td>",&ui_radio("status_def", 1,
		[ [ 1, $text{'search_allstatus'} ],
		  [ 0, $text{'search_onestatus'} ] ]),"\n",
		&ui_select("status", 2,
			   [ [ 0, $text{'view_mark0'} ],
			     [ 1, $text{'view_mark1'} ],
			     [ 2, $text{'view_mark2'} ] ]),"</td> </tr>\n";

# Limit on number of messages to search
print "<tr> <td>$text{'search_latest'}</td>\n";
print "<td>",&ui_opt_textbox("limit", $userconfig{'search_latest'}, 10,
			     $text{'search_nolatest'}, $text{'search_latestnum'}),"</td> </tr>\n";

# Destination for search
print "<tr> <td>$text{'search_dest'}</td>\n";
print "<td>",&ui_opt_textbox("dest", undef, 30, $text{'search_dest1'}, $text{'search_dest0'}),"</td> </tr>\n";

print "</table>\n";

$extra = <<EOF;
<option value=-1>$text{'sform_all'}
<option value=-2>$text{'sform_local'}
EOF
print "<input type=submit value='$text{'sform_ok'}'>\n";
@sfolders = grep { $_->{'id'} != $search_folder_id } @folders;
print " $text{'sform_folder'} ",&folder_select(\@sfolders, $folder, "folder",
					       $extra);
print "</form>\n";

&ui_print_footer("index.cgi?folder=$in{'folder'}", $text{'mail_return'});

