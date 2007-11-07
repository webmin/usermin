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
	if (&foriegn_check("mailbox")) {
		&foreign_require("mailbox", "mailbox-lib.pl");
		($froms, $doms) = &mailbox::list_from_addresses();
		$email = @$froms ? $froms->[0] : $remote_user."\@".
						 &get_system_hostname();
		}
	print "$text{'index_setupdesc'}<br>\n";
	print "<form action=secret.cgi method=post>\n";
	print "<table>\n";
	print "<tr> <td><b>$text{'index_name'}</b></td>\n";
	$remote_user_info[6] =~ s/,.*$//;
	print "<td><input name=name size=30 value='$remote_user_info[6]'></td> </tr>\n";
	print "<tr> <td><b>$text{'index_email'}</b></td>\n";
	print "<td><input name=email size=30 value='$email'></td> </tr>\n";
	print "<tr> <td><b>$text{'index_comment'}</b></td>\n";
	print "<td><input name=comment size=30></td> </tr>\n";
	print "<tr> <td><b>$text{'index_size'}</b></td>\n";
	print "<td><select name=size>\n";
	print "<option selected value=''>$text{'default'}\n";
	foreach $s (768, 1024, 2048, 4096, 8192) {
		print "<option>$s\n";
		}
	print "</select></td> </tr>\n";
	print "<tr> <td><b>$text{'index_pass'}</b></td>\n";
	print "<td><input name=pass type=password size=20></td> </tr>\n";
	print "</table>\n";
	print "<input type=submit value='$text{'index_setup'}'></form>\n";
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

