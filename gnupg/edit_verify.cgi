#!/usr/local/bin/perl
# edit_verify.cgi
# Display a form for choosing a file to verify

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'verify_title'}, "");

# Form start
print &text('verify_desc', 'edit_decrypt.cgi'),"<p>\n";
print &ui_form_start("verify.cgi", "form-data");
print &ui_table_start(undef, undef, 2);

# Source for original data
print &ui_table_row($text{'verify_mode'},
	&ui_radio_table("mode", 0,
		[ [ 0, $text{'verify_mode0'},
		       &ui_upload("file", 40) ],
		  [ 1, $text{'verify_mode1'},
		       &ui_filebox("local", undef, 40) ],
		  [ 3, $text{'verify_mode3'},
		       &ui_textarea("text", undef, 5, 40) ] ]));

# Source for signature
print &ui_table_row($text{'verify_sig'},
	&ui_radio_table("sigmode", 2,
		[ [ 2, $text{'verify_mode2'} ],
		  [ 0, $text{'verify_mode0'},
		       &ui_upload("sigfile", 40) ],
		  [ 1, $text{'verify_mode1'},
		       &ui_filebox("siglocal", undef, 40) ],
		  [ 3, $text{'verify_mode3'},
		       &ui_textarea("sigtext", undef, 5, 40) ] ]));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'verify_ok'} ] ]);

&ui_print_footer("", $text{'index_return'});

