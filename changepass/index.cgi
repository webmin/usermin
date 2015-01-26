#!/usr/local/bin/perl
# index.cgi
# Display a form for choosing a new password

require './changepass-lib.pl';
&ReadParse();
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

# Start of tabs
my @tabs = ( [ 'pass', $text{'index_passtab'} ],
	     [ 'recovery', $text{'index_recoverytab'} ] );
print ui_tabs_start(\@tabs, 'mode', $in{'mode'} || 'pass', 1);

# Password change form
print &ui_tabs_start_tab("mode", "pass");
print "$text{'index_desc1a'}<br>\n";
print "$text{'index_desc2'}<br>\n" if (&has_command($config{'smbpasswd'}));
print "<p>\n";

print &ui_form_start("changepass.cgi", "post");
print &ui_table_start(undef, undef, 2);

# Username and real name
print &ui_table_row($text{'index_for'},
	"<tt>$remote_user</tt>".
	($remote_user_info[6] ? " ($remote_user_info[6])" : ""));

# Old password
print &ui_table_row($text{'index_old'},
	&ui_password("old", undef, 20));

# New password twice
print &ui_table_row($text{'index_new1'},
	&ui_password("new1", undef, 20));
print &ui_table_row($text{'index_new2'},
	&ui_password("new2", undef, 20));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'index_change'} ] ]);
print &ui_tabs_end_tab("mode", "pass");

# Start of recovery address form
print &ui_tabs_start_tab("mode", "recovery");

print "$text{'index_desc3'}<p>\n";
print &ui_form_start("save_recovery.cgi", "post");
print &ui_table_start(undef, undef, 2);

$recovery = &get_recovery_address();
print &ui_table_row($text{'index_recovery'},
	&ui_radio("recovery_def", $recovery ? 0 : 1,
		  [ [ 1, $text{'index_recoverydef'} ],
		    [ 0, $text{'index_recoverysel'}." ".
			 &ui_textbox("recovery", $recovery, 60) ] ]));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'save'} ] ]);
print &ui_tabs_end_tab("mode", "recovery");

print ui_tabs_end(1);

&ui_print_footer("/", $text{'index'});

