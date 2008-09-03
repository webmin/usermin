#!/usr/local/bin/perl
# edit_key.cgi
# Display the details of a key, including the exported format

require './gnupg-lib.pl';
&ReadParse();
@keys = &list_keys();
if ($in{'key'}) {
	($key) = grep { $_->{'key'} eq $in{'key'} } @keys;
	$in{'idx'} = &indexof($key, @keys);
	}
else {
	$key = $keys[$in{'idx'}];
	}

&ui_print_header(undef, $text{'key_title'}, "");

# Form start
print "$text{'key_desc'}<p>\n";
print &ui_form_start("save_key.cgi");
print &ui_hidden("idx", $in{'idx'});
print &ui_table_start($text{'key_header'}, "width=100%", 4);

# Key ID
print &ui_table_row($text{'key_id'}, "<tt>$key->{'key'}</tt>");

# Creation date
print &ui_table_row($text{'key_date'}, $key->{'date'});

# Table of owner emails
@table = ( );
@names = @{$key->{'name'}};
for($i=0; $i<@names; $i++) {
	push(@table, [ $key->{'name'}->[$i],
		       $key->{'email'}->[$i],
		       !$key->{'secret'} ? ( ) :
		       @names == 1 ? ( "" ) :
			( &ui_submit($text{'delete'}, 'delete_'.$i) ) ]);
	}
if ($key->{'secret'}) {
	# Fields to add
	push(@table, [ &ui_textbox("name", undef, 30),
		       &ui_textbox("email", undef, 30),
		       &ui_submit($text{'key_addowner'}, 'add') ]);
	}
print &ui_table_row($text{'key_owner'},
	&ui_columns_table([ $text{'key_oname'}, $text{'key_oemail'},
			    $key->{'secret'} ? ( "" ) : ( ) ],
			  100, \@table, undef, 1), 3);

# Fingerprint
print &ui_table_row($text{'key_finger'},
	"<tt>".&key_fingerprint($key)."</tt>");

if ($key->{'secret'}) {
	# Offer to change usermin's passphrase
	$pass = &get_passphrase($key);
	print &ui_table_row(defined($pass) ? $text{'key_changepass'}
					   : $text{'key_setpass'},
		&ui_password("pass", undef, 20)."<br>".
		(defined($pass) ? $text{'key_passdesc2'}
				: $text{'key_passdesc'}), 3);
	}
else {
	# Offer to set trust level
	$tr = &get_trust_level($key);
	print &ui_table_row($text{'key_trust'},
		&ui_select("trust", $tr,
			[ map { [ $_, $text{"key_trust_".$_} ] } (0..4) ],
			1, 0, 1));
	}

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'save'} ] ]);

print &ui_hr();
print &ui_buttons_start();
# XXX

# Export key form
print &ui_buttons_row("edit_export.cgi", $text{'key_exportform'},
		      $text{'key_exportformdesc'},
		      &ui_hidden("idx", $key->{'index'}));

# Send to keyserver
print &ui_buttons_row("send.cgi", $text{'key_send'},
		      $text{'key_senddesc'},
		      &ui_hidden("idx", $key->{'index'}));

# Sign key
print &ui_buttons_row("signkey.cgi", $text{'key_sign'},
		      $text{'key_signdesc'},
		      &ui_hidden("idx", $key->{'index'}));

# Delete key
print &ui_buttons_row("delkey.cgi", $text{'key_del'},
		      $text{'key_deldesc'},
		      &ui_hidden("idx", $key->{'index'}));

print &ui_buttons_end();

&ui_print_footer("list_keys.cgi", $text{'keys_return'},
	"", $text{'index_return'});

