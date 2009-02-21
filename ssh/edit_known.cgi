#!/usr/local/bin/perl
# edit_known.cgi
# Edit or create a known host

require './ssh-lib.pl';
&ReadParse();
if ($in{'new'}) {
	&ui_print_header(undef, $text{'known_create'}, "");
	$msg = $text{'known_desc1'};
	}
else {
	&ui_print_header(undef, $text{'known_edit'}, "");
	@knowns = &list_knowns();
	$known = $knowns[$in{'idx'}];
	}

# Show main key details
print "$msg<p>\n" if ($msg);
print &ui_form_start("save_known.cgi", "post");
print &ui_hidden("idx", $in{'idx'});
print &ui_hidden("new", $in{'new'});
print &ui_table_start($text{'known_header'}, "width=100%", 2);

if (!$known->{'hash'}) {
	# Show actual hostnames
	print &ui_table_row($text{'known_hosts'},
		&ui_textarea("hosts", join("\n", @{$known->{'hosts'}}),
			     3, 50));
	}
else {
	# Show hashed hostname
	print &ui_table_row($text{'known_salt'},
		&ui_textbox("salt", $known->{'salt'}, 50, undef, undef,
			    "editable=false"));
	print &ui_table_row($text{'known_hash'},
		&ui_textbox("hash", $known->{'hash'}, 50, undef, undef,
			    "editable=false"));
	}

if (($known->{'type'} eq 'ssh-rsa1') or $in{'new'}) {
	# Bits and exponent
	print &ui_table_row($text{'known_bits'},
		&ui_textbox("bits", $known->{'bits'}, 5));
	print &ui_table_row($text{'known_exp'},
		&ui_textbox("exp", $known->{'exp'}, 5));
	}
	
# Key type
if ($known->{'type'} eq 'ssh-rsa1') {
	print &ui_hidden("type", $known->{'type'});
	}
elsif ($in{'new'}) {
	print &ui_table_row($text{'known_type'},
		&ui_select("type", "",
			[ [ "ssh-rsa1", $text{'index_rsa1'} ],
			  [ "ssh-rsa", $text{'index_rsa'} ],
			  [ "ssh-dsa", $text{'index_dsa'} ] ]));
	}
else {
	print &ui_table_row($text{'known_type'},
		&ui_textbox("type", $known->{'type'}, 7, undef, undef,
			    "editable=false"));
	}

# Key text
print &ui_table_row($text{'known_key'},
	&ui_textarea("key", $known->{'key'}, 5, 50, "on"));

# Comment on key
print &ui_table_row($text{'known_comment'},
	&ui_textbox("comment", $known->{'comment'}, 50));

print &ui_table_end();

if ($in{'new'}) {
	print &ui_form_end([ [ undef, $text{'create'} ] ]);
	}
else {
	print &ui_form_end([ [ undef, $text{'save'} ],
			     [ 'delete', $text{'delete'} ] ]);
	}

&ui_print_footer("list_knowns.cgi", $text{'knowns_return'},
	"", $text{'index_return'});

