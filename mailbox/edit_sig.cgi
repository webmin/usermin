#!/usr/local/bin/perl
# edit_sig.cgi
# Display the user's .signature file for editing

require './mailbox-lib.pl';
$sf = &get_signature_file();
$sf || &error($text{'sig_enone'});
&ui_print_header(undef, $text{'sig_title'}, "");

print &text('sig_desc', "<tt>$sf</tt>"),"<p>\n";
print "<form action=save_sig.cgi method=post enctype=multipart/form-data>\n";
print "<textarea name=sig rows=5 cols=80>\n",
	&get_signature(),"</textarea><br>\n";
print "<input type=submit value='$text{'save'}'>\n";
print "<input type=reset value='$text{'sig_undo'}'>\n";
print "</form>\n";

&ui_print_footer("", $text{'mail_return'});


