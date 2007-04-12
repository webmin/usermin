#!/usr/local/bin/perl
# index.cgi
# Display user's vacation file

require './vacation-lib.pl';

# Display the edit form
&header($text{'index_title'}, "", undef, 0, 1);
print "<hr>\n";

# Open and parse an existing .vacation.msg file

if (-e $vacation_file) {
	open(VACATION, $vacation_file);
	while(<VACATION>) {
		chomp;
		$vacation_subject = &html_escape($1) if m/^Subject:\s(.*)/ ;
		$vacation_from = &html_escape($1) if m/^From:\s(.*)/ ;
		$vacation_body = $vacation_body.&html_escape($_)."\n" if !m/(^Subject:|^From)(.*)/ ;
	}
	close(VACATION);
} else {
	$vacation_subject = &html_escape($text{'subject_text'});
	$vacation_from = &html_escape(&get_from);
	$vacation_body = &html_escape($text{'body_text'});
}


print "<form action=save_vacation.cgi method=post enctype=multipart/form-data>\n";

print &text('index_desc'),"<br><br>\n";

print "<table>\n";

# Get the Subject of the vacation reply
print "<tr> <td><b>$text{'subject_desc'}</b></td>";
print "<td><input name=subject value=\"$vacation_subject\" size=80></td></tr>\n";

# Get the From line (default this if $vacation_from is null)
if ($mailbox_cfg{'edit_from'}) {
	print "<tr> <td><b>$text{'from_desc'}</b></td>";
	print "<td><input name=from value=\"$vacation_from\" size=80></td></tr>\n";
} else {
	print "<tr> <td><b>$text{'from_desc'}</b></td>";
	print "<td>$vacation_from</td></tr>\n";
}
print "</table>\n";

# Get the vacation message body
print "<b>$text{'body_desc'}</b><br>\n";
print "<textarea name=body rows=10 cols=70>\n";
print "$vacation_body";
print "</textarea><br>\n";
print "<br>\n<table border=0 width='600' ><tr><td align=left>";

if ($vacation_active) {
	print "<input name=stop_vacation type=hidden value=1>\n";
	print "<input type=submit value='$text{'vacation_disable'}'>";
} else {
	print "<input name=start_vacation type=hidden value=1>\n";
	print "<input type=submit value='$text{'vacation_enable'}'>";
}
print "</td><td align=right><input type=submit name=update value='$text{'vacation_update'}'></td></tr></table>";
print "\n</form>\n<hr>\n";
&footer("/", $text{'index'});

