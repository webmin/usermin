#!/usr/local/bin/perl
# edit_encrypt.cgi
# Display a form for choosing a file to encrypt and a key to use

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'encrypt_title'}, "");

print "$text{'encrypt_desc'}<p>\n";
print &ui_form_start("encrypt.cgi/output.gpg", "form-data");
print &ui_table_start(undef, undef, 2);

# Plain file source
print &ui_table_row($text{'encrypt_mode'},
	&ui_radio_table("mode", 0,
		[ [ 0, $text{'encrypt_mode0'},
		       &ui_upload("upload", 40) ],
		  [ 1, $text{'encrypt_mode1'},
		       &ui_filebox("local", undef, 40) ],
		  [ 2, $text{'encrypt_mode2'},
		       &ui_textarea("text", undef, 5, 40) ] ]));

# Encrypt with keys
@keys = &list_keys_sorted();
print &ui_table_row($text{'encrypt_key'},
	&ui_select("idx", undef,
		   [ map { [ $_->{'index'}, $_->{'name'}->[0] ] } @keys ],
		   5, 1));

# ASCII armour
print &ui_table_row($text{'encrypt_ascii'},
	&ui_yesno_radio("ascii", 0));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'encrypt_ok'} ] ]);

&ui_print_footer("", $text{'index_return'});

