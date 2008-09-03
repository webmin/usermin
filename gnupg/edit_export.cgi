#!/usr/local/bin/perl
# export_form.cgi
# Show a form for exporting a key

require './gnupg-lib.pl';
&ReadParse();
@keys = &list_keys();
$key = $keys[$in{'idx'}];

&ui_print_header(undef, $text{'export_title'}, "");

# Form start and header
print &text('export_desc', "<tt>$key->{'name'}->[0]</tt>",
	    $key->{'email'}->[0] ? "&lt;<tt>$key->{'email'}->[0]</tt>&gt;" : "",
	    ),"<p>\n";
print &ui_form_start("export.cgi");
print &ui_hidden("idx", $key->{'index'});
print &ui_table_start(undef, undef, 2);

# Export to browser or file
print &ui_table_row($text{'export_to'},
	&ui_radio_table("mode", 0,
		[ [ 0, $text{'export_mode0'} ],
		  [ 1, $text{'export_mode1'}, &ui_filebox("to", undef, 40) ]]));

# Key format
print &ui_table_row($text{'export_format'},
	&ui_radio("format", 0, [ [ 0, $text{'export_ascii'} ],
				 [ 1, $text{'export_binary'} ] ]));

# Include secret data?
if ($key->{'secret'}) {
	print &ui_table_row($text{'export_smode'},
		&ui_radio("smode", 0, [ [ 1, $text{'export_secret'} ],
					[ 0, $text{'export_public'} ] ]));
	}

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'export_ok'} ] ]);

&ui_print_footer("list_keys.cgi", $text{'keys_return'});

