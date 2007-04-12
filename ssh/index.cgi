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

if (!-d $ssh_directory) {
	# Offer to setup SSH
	print "<center><form action=setup.cgi method=post>\n";
	print "$text{'index_setup'}<p>\n";
	print "<input type=submit value='$text{'index_sok'}'>\n";
	print "<input type=password name=pass size=25><p>\n";
	if (&get_ssh_version() >= 2) {
		print $text{'index_type'},"\n";
		print &ui_select("type", "",
			[ [ "rsa1", $text{'index_rsa1'} ],
			  [ "rsa", $text{'index_rsa'} ],
			  [ "dsa", $text{'index_dsa'} ] ]),"\n";
		}
	print "</form></center>\n";
	}
else {
	# Show table of options
	@links = ( "list_auths.cgi", "list_knowns.cgi",
		   "edit_keys.cgi", "list_hosts.cgi" );
	@titles = ( $text{'auths_title'}, $text{'knowns_title'},
		    $text{'keys_title'}, $text{'hosts_title'} );
	@icons = ( "images/auths.gif", "images/knowns.gif",
		   "images/keys.gif", "images/hosts.gif" );
	&icons_table(\@links, \@titles, \@icons);
	}

&ui_print_footer("/", $text{'index'});

