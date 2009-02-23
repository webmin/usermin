#!/usr/local/bin/perl
# Show details of one key

require './ssh-lib.pl';
&ReadParse();
@keys = &list_ssh_keys();
($key) = grep { $_->{'private_file'} eq $in{'file'} } @keys;
$key || &error($text{'ekey_egone'});

&ui_print_header(undef, $text{'ekey_title'}, "");

print &ui_form_start("save_key.cgi", "form-data");
print &ui_hidden("file", $in{'file'});
print &ui_table_start($text{'ekey_header'}, undef, 2);

# Private key
if ($key->{'type'} eq 'rsa1') {
	# Old format is binary .. offer to download and upload
	$short = $key->{'private_file'};
	$short =~ s/^.*\///;
	print &ui_table_row($text{'ekey_private1'},
		"<a href='download_key.cgi/$short?file=".
		&urlize($key->{'private_file'})."'>$text{'ekey_down'}</a>");

	print &ui_table_row($text{'ekey_private2'},
		&ui_upload("private"));
	}
else {
	# New format is test
	print &ui_table_row($text{'ekey_private'},
		&ui_textarea("private",
			     &read_file_contents($key->{'private_file'}),
			     10, 80));
	}

# Public key
print &ui_table_row($text{'ekey_public'},
	&ui_textarea("public", &read_file_contents($key->{'public_file'}),
		     10, 80, undef, 0, "readonly=true"));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'ekey_save'} ] ]);

&ui_print_footer("list_keys.cgi", $text{'lkeys_return'});
