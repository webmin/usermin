#!/usr/local/bin/perl
# edit_secret.cgi
# Display a form for adding an additional secret key

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'secret_title'}, "");

print "$text{'secret_desc'}<br>\n";
print &ui_form_start("secret.cgi", "post");
print &ui_hidden("newkey", 1);
print &ui_table_start(undef, undef, 2);

$remote_user_info[6] =~ s/,*$//;
print &ui_table_row($text{'index_name'},
	&ui_textbox("name", $remote_user_info[6], 40));

print &ui_table_row($text{'index_email'},
	&ui_textbox("email", &default_email_address(), 40));

print &ui_table_row($text{'index_comment'},
	&ui_textbox("comment", undef, 40));

print &ui_table_row($text{'index_size'},
	&ui_select("size", undef,
		[ [ '', $text{'default'} ],
		  768, 1024, 2048, 4096, 8192 ]));

print &ui_table_row($text{'index_pass'},
	&ui_password("pass", undef, 20));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'secret_setup'} ] ]);

&ui_print_footer("", $text{'index_return'});

