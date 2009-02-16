#!/usr/local/bin/perl
# Offer to setup razor, if the user hasn't already

require './spam-lib.pl';
&ui_print_header(undef, $text{'razor_title'}, "");

if (!&has_command($config{'razor_admin'})) {
	# Not installed
	print &text('razor_ecmd', "<tt>$config{'razor_admin'}</tt>"),"<p>\n";
	}
else {
	# Show form
	print "$text{'razor_desc'}<p>\n";
	print &ui_form_start("setup_razor.cgi", "post");
	print &ui_table_start(undef, undef, 2);

	# Username for Razor account
	print &ui_table_row($text{'razor_user'},
		&ui_opt_textbox("user", undef, 25, $text{'razor_auto'},
				$text{'razor_enter'}));

	# Password for Razor account
	print &ui_table_row($text{'razor_pass'},
		&ui_opt_textbox("pass", undef, 25, $text{'razor_auto'},
				$text{'razor_enter'}));

	print &ui_table_end();
	print &ui_form_end([ [ undef, $text{'razor_ok'} ] ]);
	}

&ui_print_footer("", $text{'index_return'});

