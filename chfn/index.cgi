#!/usr/local/bin/perl
# index.cgi
# Display a form for changing user details

require './chfn-lib.pl';
&switch_to_remote_user();
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

if ($config{'change_shell'}) {
	print "$text{'index_desc'}<p>\n";
	}
else {
	print "$text{'index_desc2'}<p>\n";
	}

print &ui_form_start("save.cgi", "post");
print &ui_table_start($text{'index_header'}, undef, 2, [ "width=30%" ]);

@uinfo = split(/,/, $remote_user_info[6]);
if ($config{'change_real'}) {
	print &ui_table_row($text{'index_real'},
		&ui_textbox("real", $uinfo[0], 40));
	}

if ($config{'change_office'}) {
	print &ui_table_row($text{'index_office'},
		&ui_textbox("office", $uinfo[1], 40));
	}

if ($config{'change_ophone'}) {
	print &ui_table_row($text{'index_ophone'},
		&ui_textbox("ophone", $uinfo[2], 40));
	}

if ($config{'change_hphone'}) {
	print &ui_table_row($text{'index_hphone'},
		&ui_textbox("hphone", $uinfo[3], 40));
	}

if ($config{'change_shell'}) {
	open(SHELL, $config{'shells'} || "/etc/shells");
	while($s = <SHELL>) {
		$s =~ s/\r|\n//g;
		$s =~ s/#.*$//;
		next if ($s !~ /\S/);
		push(@opts, $s);
		}
	close(SHELL);
	print &ui_table_row($text{'index_shell'},
		&ui_select("shell", $remote_user_info[8], \@opts, 1, 0, 1));
	}

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'save'} ] ]);

&ui_print_footer("/", $text{'index'});

