#!/usr/local/bin/perl
# Display all the user's private keys

require './ssh-lib.pl';
&ui_print_header(undef, $text{'lkeys_title'}, "");
@keys = &list_ssh_keys();

print "$text{'lkeys_desc'}<br>\n";

# Show a table of them
@table = ( );
foreach $k (@keys) {
	push(@table, [
		"<a href='edit_key.cgi?file=$k->{'private_file'}'>".
		$text{'index_'.$k->{'type'}}."</a>",
		&remove_homedir($k->{'private_file'}),
		&remove_homedir($k->{'public_file'}),
		]);
	$got{$k->{'type'}} = 1;
	}
print &ui_columns_table([ $text{'lkeys_type'},
			  $text{'lkeys_private'},
			  $text{'lkeys_public'} ], 100, \@table);

# Show form to generate, if any are missing
@missing_types = grep { !$got{$_} } @ssh_key_types;
if (@missing_types) {
	print &ui_hr();
	print $text{'lkeys_new'},"<p>\n";
	print &ui_form_start("setup.cgi", "post");
	print &ui_table_start(undef, undef, 2);

	# Key type
	print &ui_table_row($text{'index_type'},
		&ui_select("type", "dsa",
			[ map { [ $_, $text{'index_'.$_} ] }
			      @missing_types ]));

	# Passphrase
	print &ui_table_row($text{'index_pass'},
		&ui_password("pass", undef, 25));

	print &ui_table_end();
	print &ui_form_end([ [ undef, $text{'lkeys_sok2'} ] ]);
	}

&ui_print_footer("", $text{'index_return'});

sub remove_homedir
{
local ($f) = @_;
$f =~ s/^\Q$remote_user_info[7]\E/\~/;
return $f;
}

