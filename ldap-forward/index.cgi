#!/usr/local/bin/perl
# Show the current forwarding address

require './ldap-forward-lib.pl';
&ui_print_header(undef, $module_info{'desc'}, "", undef, 0, 1);

$uinfo = &mailbox::get_user_ldap();
print &ui_form_start("save.cgi");
print &ui_table_start($text{'index_header'});

@fwd = $uinfo->get_value("mailForwardingAddress");
print &ui_table_row($text{'index_fwd'},
	&ui_opt_textbox("fwd", join(" ", @fwd), 40,
			$text{'index_none'}."<br>",
			$text{'index_to'}));

print &ui_table_end();
print &ui_form_end([ [ "save", $text{'index_save'} ] ]);

&ui_print_footer("/", $text{'index'});

