#!/usr/local/bin/perl
# index.cgi
# Display main menu of GNUPG options

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'index_title'}, undef, undef, 0, 1);

if (!&has_command($gpgpath)) {
	print &text('index_egpg', "<tt>$gpgpath</tt>"),"<p>\n";
	&ui_print_footer("/", $text{'index'});
	exit;
	}

@keys = &list_keys();
if (!@keys) {
	# Offer to setup GNUPG
	print "$text{'index_setupdesc'}<br>\n";
	print &ui_form_start("secret.cgi", "post");
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
	print &ui_form_end([ [ undef, $text{'index_setup'} ] ]);
	}
else {
	# Show table of options
	@links = ( "list_keys.cgi", "edit_encrypt.cgi", "edit_decrypt.cgi",
		   "edit_sign.cgi", "edit_verify.cgi", "edit_secret.cgi" );
	@titles = ( $text{'keys_title'}, $text{'encrypt_title'},
		    $text{'decrypt_title'}, $text{'sign_title'},
		    $text{'verify_title'}, $text{'secret_title'} );
	@icons = ( "images/keys.gif", "images/encrypt.gif", "images/decrypt.gif",
		   "images/sign.gif", "images/verify.gif", "images/secret.gif" );
	&icons_table(\@links, \@titles, \@icons, scalar(@links));
	}

&ui_print_footer("/", $text{'index'});

