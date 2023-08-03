#!/usr/local/bin/perl
# edit_ffile.cgi
# Allow editing of a filter config file

require './forward-lib.pl';
&ReadParse();

&ui_print_header(undef, $text{'ffile_title'}, "");
$in{'vfile'} = &make_absolute($in{'vfile'});
open(FILE, $in{'vfile'});
while(<FILE>) {
	s/\r|\n//g;
	if (/^(\S+)\s+(\S+)\s+(\S+)\s+(.*)$/) {
		push(@filter, [ $1, $2, $3, $4 ]);
		}
	elsif (/^(2)\s+(\S+)$/) {
		$other = $2;
		}
	}
close(FILE);

print "<b>",&text('ffile_desc', "<tt>@{[&html_escape($in{'vfile'})]}</tt>"),"</b><p>\n";

print "<form action=save_ffile.cgi method=post enctype=multipart/form-data>\n";
print &ui_hidden("file", $in{'file'}),"\n";
print &ui_hidden("num", $in{'num'}),"\n";
print &ui_hidden("vfile", $in{'vfile'}),"\n";

$i = 0;
foreach $f (@filter, [ 1, '', '', '' ]) {
	$field = "<select name=field_$i>\n";
	foreach $ft ('', 'from', 'to', 'subject', 'cc', 'body') {
		$field .= sprintf "<option value='%s' %s>%s\n",
			$ft, $f->[2] eq $ft ? "selected" : "",
			$ft ? $text{"ffile_$ft"} : "&nbsp";
		}
	$field .= "</select>\n";

	$what = "<select name=what_$i>\n";
	$what .= sprintf "<option value=0 %s>%s\n",
		$f->[0] == 0 ? "selected" : "", $text{"ffile_what0"};
	$what .= sprintf "<option value=1 %s>%s\n",
		$f->[0] == 1 ? "selected" : "", $text{"ffile_what1"};
	$what .= "</select>\n";

	$match = "<input name=match_$i size=20 value='$f->[3]'>\n";

	$action = "<input name=action_$i size=20 value='$f->[1]'>\n";

	print &text('ffile_line', $field, $what, $match, $action),"<br>\n";
	$i++;
	}
print &text('ffile_other',
	    "<input name=other size=30 value='$other'>"),"<br>\n";

print "<input type=submit value=\"$text{'save'}\">\n";
print "</form>\n";

&ui_print_footer("edit_alias.cgi?num=$in{'num'}&file=@{[&urlize($in{'file'})]}",
		 $text{'aform_return'});

