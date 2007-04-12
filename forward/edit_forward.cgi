#!/usr/local/bin/perl
# edit_forward.cgi
# Display a form for editing the .forward file manually

require './forward-lib.pl';
&ui_print_header(undef, $text{'edit_title'}, "");

print &text('edit_desc', "<tt>.forward</tt>"),"<p>\n";
print "<form action=save_forward.cgi method=post enctype=multipart/form-data>\n";
print "<textarea name=forward rows=10 cols=70>\n";
open(FORWARD, $forward_file);
while(<FORWARD>) {
	print &html_escape($_);
	}
close(FORWARD);
print "</textarea><br>\n";
print "<input type=submit value='$text{'save'}'></form>\n";

&ui_print_footer("index.cgi?simple=0", $text{'index_return'});

