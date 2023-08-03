#!/usr/local/bin/perl
# edit_vfile.cgi
# Display the contents of a vacation autoreply file

require './forward-lib.pl';
&ReadParse();

&ui_print_header(undef, $text{'vfile_title'}, "");

$in{'vfile'} = &make_absolute($in{'vfile'});
open(FILE, $in{'vfile'});
while(<FILE>) {
	if (/^Subject:\s*(.*)/) {
		$subject = $1;
		}
	elsif (/^From:\s*(.*)/) {
		$from = $1;
		}
	else {
		push(@lines, $_);
		}
	}
close(FILE);
if (!-r $in{'vfile'}) {
	($froms, $doms) = &mailbox::list_from_addresses();
	$from = $froms->[0];
	}

print &text('vfile_desc', "<tt>@{[&html_escape($in{'vfile'})]}</tt>"),"<p>\n";

print "<form action=save_vfile.cgi method=post enctype=multipart/form-data>\n";
print &ui_hidden("file", $in{'file'}),"\n";
print &ui_hidden("num", $in{'num'}),"\n";
print &ui_hidden("vfile", $in{'vfile'}),"\n";
print &ui_hidden("idx", $in{'idx'}),"\n";
print "<textarea name=text rows=20 cols=80>",
	join("", @lines),"</textarea><p>\n";

print "<table>\n";

# Show From: address option
print "<tr> <td>$text{'rfile_from'}</td>\n";
print "<td>",&ui_radio("from_def", $from ? 0 : 1,
		       [ [ 1, $text{'default'} ],
			 [ 0, " " ] ]),"\n",
	     &ui_textbox("from", $from, 50),"</td> </tr>\n";

# Show Subject: line option
print "<tr> <td>$text{'vfile_subject'}</td>\n";
print "<td>",&ui_radio("subject_def", $subject ? 0 : 1,
		       [ [ 1, $text{'default'} ],
			 [ 0, " " ] ]),"\n",
	     &ui_textbox("subject", $subject, 50),"</td> </tr>\n";

print "</table>\n";

print "<input type=submit value=\"$text{'save'}\"> ",
      "<input type=reset value=\"$text{'rfile_undo'}\">\n";
print "</form>\n";

&ui_print_footer(defined($in{'idx'}) ?
		 ( "edit_vacation.cgi?num=$in{'num'}&file=@{[&urlize($in{'file'})]}&idx=$in{'idx'}", $text{'vacation_return'} ) : ( ),
		 "edit_alias.cgi?num=$in{'num'}&file=@{[&urlize($in{'file'})]}",
		 $text{'aform_return'});

