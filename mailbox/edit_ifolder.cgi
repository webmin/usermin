#!/usr/local/bin/perl
# Display a form for creating or editing an IMAP folder
use strict;
use warnings;
our (%text, %in);

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
	}

print &ui_form_start("save_ifolder.cgi");
print &ui_hidden("new", $in{'new'}),"\n";
print &ui_hidden("idx", $in{'idx'}),"\n";
print &ui_table_start($text{'edit_header'}, undef, 2);

# IMAP folder name
print &ui_table_row($text{'edit_name'},
		    &ui_textbox("name", $folder->{'name'}, 40));

&show_folder_options($folder, $folder->{'mode'});

print &ui_table_end();
if ($in{'new'}) {
	print &ui_form_end([ [ "create", $text{'create'} ] ]);
	}
else {
	print &ui_form_end([ [ "save", $text{'save'} ],
			     [ "delete", $text{'delete'} ] ]);
	}

&ui_print_footer("list_ifolders.cgi", $text{'folders_return'});
