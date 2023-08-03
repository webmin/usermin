#!/usr/local/bin/perl
# edit_rfile.cgi
# Display the contents of an autoreply file

require './forward-lib.pl';
&ReadParse();

&ui_print_header(undef, $text{'rfile_title'}, "");
$in{'vfile'} = &make_absolute($in{'vfile'});
open(FILE, $in{'vfile'});
while(<FILE>) {
	if (/^Reply-Tracking:\s*(.*)/) {
		$replies = $1;
		}
	elsif (/^Reply-Period:\s*(.*)/) {
		$period = $1;
		}
	elsif (/^No-Autoreply:\s*(.*)/) {
		$no_autoreply = $1;
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

print &text('rfile_desc', "<tt>@{[&html_escape($in{'vfile'})]}</tt>"),"<p>\n";
print "$text{'rfile_desc2'}<p>\n";

print "<form action=save_rfile.cgi method=post enctype=multipart/form-data>\n";
print &ui_hidden("file", $in{'file'}),"\n";
print &ui_hidden("num", $in{'num'}),"\n";
print &ui_hidden("vfile", $in{'vfile'}),"\n";
print "<textarea name=text rows=20 cols=80>",
	join("", @lines),"</textarea><p>\n";

print "<table>\n";

# Show From: address option
print "<tr> <td>$text{'rfile_from'}</td>\n";
printf "<td><input type=radio name=from_def value=1 %s> %s\n",
	$from eq '' ? "checked" : "", $text{'rfile_auto'};
printf "<input type=radio name=from_def value=0 %s>\n",
	$from eq '' ? "" :"checked";
printf "<input name=from size=30 value='%s'></td> </tr>\n",
	$from;
print "<tr> <td></td> <td><font size=-1>$text{'rfile_fromdesc'}</font></td> </tr>\n";

# Show reply-tracking option
printf "<tr> <td colspan=2><input type=checkbox name=replies value=1 %s> %s</td> </tr>\n",
	$replies ? "checked" : "", $text{'rfile_replies'};
print "<input type=hidden name=replies_file value='$replies'>\n";

# Show reply period input
print "<tr> <td>&nbsp;&nbsp;&nbsp;$text{'rfile_period'}</td>\n";
printf "<td><input type=radio name=period_def value=1 %s> %s\n",
	$period eq '' ? "checked" : "", $text{'rfile_default'};
printf "<input type=radio name=period_def value=0 %s>\n",
	$period eq '' ? "" :"checked";
printf "<input name=period size=5 value='%s'> %s</td> </tr>\n",
	$period, $text{'rfile_secs'};

# Show people to not autoreply to
print "<tr> <td>$text{'rfile_no_autoreply'}</td>\n";
printf "<td><input name=no_autoreply size=40 value='%s'></td> </tr>\n",
	$no_autoreply;

print "</table>\n";

print "<input type=submit value=\"$text{'save'}\"> ",
      "<input type=reset value=\"$text{'rfile_undo'}\">\n";
print "</form>\n";

&ui_print_footer("edit_alias.cgi?num=$in{'num'}&file=@{[&urlize($in{'file'})]}",
		 $text{'aform_return'});

