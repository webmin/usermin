#!/usr/local/bin/perl
# edit_imap.cgi
# Display a form for creating or editing an IMAP folder
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in);
our $imap_port;

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
print &ui_form_start("save_imap.cgi");
print &ui_hidden("idx", $in{'idx'});
print &ui_hidden("new", $in{'new'});
print &ui_hidden("mode", $mode);
print &ui_table_start($text{'edit_header'}, undef, 2);

# Folder type
print &ui_table_row($text{'edit_mode'}, $text{'edit_imap'});

# Folder name
print &ui_table_row($text{'edit_name'},
	&ui_textbox("name", $folder->{'name'}, 40));

# IMAP server
print &ui_table_row($text{'edit_iserver'},
	&ui_textbox("server", $folder->{'server'}, 40));

# IMAP port
print &ui_table_row($text{'edit_port'},
	&ui_opt_textbox("port", $folder->{'port'}, 6,
			$text{'default'}." ($imap_port)"));

# Login and password
print &ui_table_row($text{'edit_user'},
	&ui_opt_textbox("user", $folder->{'user'} eq '*' ? undef :
			$folder->{'user'}, 20, $text{'edit_usersame'}));
print &ui_table_row($text{'edit_pass'},
	&ui_password("pass", $folder->{'pass'}, 20));

# Remote mailbox
print &ui_table_row($text{'edit_mailbox'},
	&ui_opt_textbox("mailbox", $folder->{'mailbox'}, 20,
			$text{'edit_imapinbox'}, $text{'edit_imapother'}));

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
