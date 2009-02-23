#!/usr/local/bin/perl
# index.cgi
# Display main menu of SSH client/login option types

require './ssh-lib.pl';
&ui_print_header(undef, $text{'index_title'}, undef, undef, 0, 1);

if (!&has_command("ssh")) {
	print &text('index_essh', "<tt>ssh</tt>"),"<p>\n";
	&ui_print_footer("/", $text{'index'});
	exit;
	}

if (!-d $ssh_directory || !&list_ssh_keys()) {
	# Offer to setup SSH
	print &ui_form_start("setup.cgi", "post");
	print "$text{'index_setup'}<p>\n";
	print &ui_table_start(undef, undef, 2);

	# Key type
	if (&get_ssh_version() >= 2) {
		print &ui_table_row($text{'index_type'},
			&ui_select("type", "dsa",
				[ map { [ $_, $text{'index_'.$_} ] }
				      @ssh_key_types ]));
		}

	# Passphrase
	print &ui_table_row($text{'index_pass'},
		&ui_password("pass", undef, 25));

	print &ui_table_end();
	print &ui_form_end([ [ undef, $text{'index_sok2'} ] ]);
	}
else {
	# Show table of options
	@links = ( "list_auths.cgi", "list_knowns.cgi",
		   "list_keys.cgi", "list_hosts.cgi" );
	@titles = ( $text{'auths_title'}, $text{'knowns_title'},
		    $text{'lkeys_title'}, $text{'hosts_title'} );
	@icons = ( "images/auths.gif", "images/knowns.gif",
		   "images/keys.gif", "images/hosts.gif" );
	&icons_table(\@links, \@titles, \@icons);
	}

&ui_print_footer("/", $text{'index'});

