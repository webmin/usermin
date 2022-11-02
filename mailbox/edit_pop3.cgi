#!/usr/local/bin/perl
# edit_pop3.cgi
# Display a form for creating or editing a POP3 folder
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in);
our $pop3_port;

require './mailbox-lib.pl';
&ReadParse();

my $mode;
my @folders;
my $folder;
if ($in{'new'}) {
	&ui_print_header(undef, $text{'edit_title1'}, "");
	$mode = $in{'mode'};
	}
else {
	&ui_print_header(undef, $text{'edit_title2'}, "");
	@folders = &list_folders();
	$folder = $folders[$in{'idx'}];
	$mode = $folder->{'mode'};
	}

# Form and table start
print &ui_form_start("save_pop3.cgi");
print &ui_hidden("idx", $in{'idx'});
print &ui_hidden("new", $in{'new'});
print &ui_hidden("mode", $mode);
print &ui_table_start($text{'edit_header'}, undef, 2);

# Folder type
print &ui_table_row($text{'edit_mode'}, $text{'edit_pop3'});

# Folder name
print &ui_table_row($text{'edit_name'},
	&ui_textbox("name", $folder->{'name'}, 40));

# POP3 server
print &ui_table_row($text{'edit_server'},
	&ui_textbox("server", $folder->{'server'}, 40));

# POP3 port
print &ui_table_row($text{'edit_port'},
	&ui_opt_textbox("port", $folder->{'port'}, 6,
			$text{'default'}." ($pop3_port)"));

# Login and password
print &ui_table_row($text{'edit_user'},
	&ui_opt_textbox("user", $folder->{'user'} eq '*' ? undef :
			$folder->{'user'}, 20, $text{'edit_usersame'}));
print &ui_table_row($text{'edit_pass'},
	&ui_password("pass", $folder->{'pass'}, 20));

&show_folder_options($folder);

print &ui_table_end();
if ($in{'new'}) {
	print &ui_form_end([ [ undef, $text{'create'} ] ]);
	}
else {
	print &ui_form_end([ [ undef, $text{'save'} ],
			     [ 'delete', $text{'delete'} ] ]);
	}

&ui_print_footer("list_folders.cgi", $text{'folders_return'});
