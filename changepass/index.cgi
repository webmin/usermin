#!/usr/local/bin/perl
# index.cgi
# Display a form for choosing a new password

require './changepass-lib.pl';
&ui_print_header(undef, $text{'index_title'}, "", undef, 0, 1);

print "$text{'index_desc1'}<br>\n";
print "$text{'index_desc2'}<br>\n" if (&has_command($config{'smbpasswd'}));

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

&ui_print_footer("/", $text{'index'});

