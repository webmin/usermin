#!/usr/local/bin/perl
# edit_auth.cgi
# Edit or create an authorized key

require './ssh-lib.pl';
&ReadParse();
if ($in{'new'}) {
	&ui_print_header(undef, $text{'auth_create'}, "");
	$msg = $text{'auth_desc1'};
	$auth = { 'keytype' => 'ssh-dss',
		  'type' => $in{'type'} || 1 };
	}
else {
	&ui_print_header(undef, $text{'auth_edit'}, "");
	@auths = &list_auths();
	$auth = $auths[$in{'idx'}];
	}

# Show main key details
print "$msg<p>\n" if ($msg);
print &ui_form_start("save_auth.cgi", "post");
print &ui_hidden("idx", $in{'idx'}),"\n";
print &ui_hidden("new", $in{'new'}),"\n";
print &ui_hidden("type", $auth->{'type'}),"\n";
print &ui_table_start($text{'auth_header'.$auth->{'type'}}, "width=100%", 4);

print &ui_table_row($text{'auth_name'},
		&ui_textbox("name", $auth->{'name'}, 40), 3);

if ($auth->{'type'} == 1) {
	# Only SSH 1 has bits and exponent
	print &ui_table_row($text{'auth_bits'},
			    &ui_textbox("bits", $auth->{'bits'}, 5), 3);

	print &ui_table_row($text{'auth_exp'},
			    &ui_textbox("exp", $auth->{'exp'}, 5), 3);
	}
else {
	# Only SSH 2 has key type
	print &ui_table_row($text{'auth_keytype'},
			&ui_select("keytype", $auth->{'keytype'},
				[ [ "ssh-dss", $text{'auth_dss'} ],
				  [ "ssh-rsa", $text{'auth_rsa'} ] ],
				1, 0, 1));
	}

print &ui_table_row($text{'auth_key'},
	&ui_textarea("key", $auth->{'key'}, 10, 50, "on"), 3);

# Show key options
&parse_options($auth->{'opts'}, \%opts);
print &ui_table_hr();

print &ui_table_row($text{'auth_from'},
	&ui_radio("from_def", $opts{'from'} ? 0 : 1,
		  [ [ 1, $text{'auth_from_all'} ],
		    [ 0, $text{'auth_from_sel'} ] ])."<br>".
	&ui_textarea("from", join(" ", split(/,/, $opts{'from'}->[0])),
		     3, 50, "on"), 3);

print &ui_table_row($text{'auth_command'},
	&ui_textbox("command", $opts{'command'}->[0], 50), 3);

print &ui_table_row($text{'auth_noport'},
	&ui_radio("noport", $opts{'no-port-forwarding'} ? 1 : 0,
		  [ [ 0, $text{'yes'} ], [ 1, $text{'no'} ] ]));

print &ui_table_row($text{'auth_nox11'},
	&ui_radio("nox11", $opts{'no-x11-forwarding'} ? 1 : 0,
		  [ [ 0, $text{'yes'} ], [ 1, $text{'no'} ] ]));

print &ui_table_row($text{'auth_noagent'},
	&ui_radio("noagent", $opts{'no-agent-forwarding'} ? 1 : 0,
		  [ [ 0, $text{'yes'} ], [ 1, $text{'no'} ] ]));

print &ui_table_row($text{'auth_nopty'},
	&ui_radio("nopty", $opts{'no-pty'} ? 1 : 0,
		  [ [ 0, $text{'yes'} ], [ 1, $text{'no'} ] ]));

print &ui_table_end();
if ($in{'new'}) {
	print &ui_form_end([ [ "create", $text{'create'} ] ]);
	}
else {
	print &ui_form_end([ [ "save", $text{'save'} ],
			     [ "delete", $text{'delete'} ] ]);
	}

&ui_print_footer("list_auths.cgi", $text{'auths_return'},
	"", $text{'index_return'});


