#!/usr/local/bin/perl
# edit_sign.cgi
# Display a form for choosing a file to sign

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'sign_title'}, "");

# Start of signing form
print "$text{'sign_desc'}<p>\n";
print &ui_form_start("sign.cgi/signed.txt", "form-data");
print &ui_table_start(undef, undef, 2);

# Source for data to sign
print &ui_table_row($text{'sign_mode'},
	&ui_radio_table("mode", 0, 
		[ [ 0, $text{'sign_mode0'},
		       &ui_upload("upload", 40) ],
		  [ 1, $text{'sign_mode1'},
		       &ui_filebox("local", undef, 40) ],
		  [ 2, $text{'sign_mode2'},
		       &ui_textarea("text", undef, 5, 40) ] ]));

# Secret key to use
@keys = &list_secret_keys();
print &ui_table_row($text{'sign_key'},
	&ui_select("idx", undef,
		[ map { [ $_->{'index'}, $_->{'name'}->[0] ] } @keys ]));

# Ascii encode?
print &ui_table_row($text{'sign_ascii'},
	&ui_yesno_radio("ascii", 1));

# Separate signature>
print &ui_table_row($text{'sign_sep'},
	&ui_yesno_radio("sep", 0));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'sign_ok'} ] ]);

&ui_print_footer("", $text{'index_return'});

