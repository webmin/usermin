#!/usr/local/bin/perl
# edit_decrypt.cgi
# Display a form for choosing a file to decrypt

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'decrypt_title'}, "");

print "$text{'decrypt_desc'}<p>\n";
print &ui_form_start("decrypt.cgi/output.txt", "form-data");
print &ui_table_start(undef, undef, 2);

# Source of encrypted data
print &ui_table_row($text{'decrypt_mode'},
	&ui_radio_table("mode", 0,
		[ [ 0, $text{'decrypt_mode0'},
		    &ui_upload("upload", 40) ],
		  [ 1, $text{'decrypt_mode1'},
		    &ui_filebox("local", undef, 40) ],
		  [ 2, $text{'decrypt_mode2'},
		    &ui_textarea("text", undef, 5, 40) ] ]));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'decrypt_ok'} ] ]);

&ui_print_footer("", $text{'index_return'});

