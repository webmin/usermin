#!/usr/local/bin/perl
# edit_folder.cgi
# Display a form for creating or editing a folder of some kind
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in, %userconfig);
our $folders_dir;
our @remote_user_info;

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
print &ui_form_start("save_folder.cgi");
print &ui_hidden("idx", $in{'idx'});
print &ui_hidden("new", $in{'new'});
print &ui_hidden("mode", $mode);
print &ui_table_start($text{'edit_header'}, undef, 2);

# Folder type
print &ui_table_row($text{'edit_mode'},
	&text("edit_mode$mode", "<tt>$folders_dir</tt>"));

if ($mode == 0) {
	# Adding/editing a new file or directory to ~/mail
	print &ui_table_row($text{'edit_name'},
		&ui_textbox("name", $folder->{'name'}, 40));

	if ($in{'new'} && $folders_dir eq "$remote_user_info[7]/Maildir") {
		# A new folder, but under a Maildir .. so it must be maildir too
		print &ui_table_row($text{'edit_type'},
			$text{'edit_type1'});
		print &ui_hidden("type", 1),"\n";
		}
	elsif ($in{'new'}) {
		# Can choose the type of a new folder
		print &ui_table_row($text{'edit_type'},
			&ui_radio("type", 0,
				[ [ 0, $text{'edit_type0'} ],
				  [ 1, $text{'edit_type1'} ],
				  $userconfig{'mailbox_recur'} ?
					( [ 3, $text{'edit_type3'} ] ) : ( )
				]));
		}
	else {
		# Show type of existing folder
		print &ui_table_row($text{'edit_type'},
			$text{'edit_type'.$folder->{'type'}});
		}
	}
elsif ($mode == 1) {
	# Adding/editing an external file or directory
	print &ui_table_row($text{'edit_name'},
		&ui_textbox("name", $folder->{'name'}, 40));

	print &ui_table_row($text{'edit_file'},
		&ui_textbox("file", $folder->{'file'}, 40)." ".
		&file_chooser_button("file"));
	}
elsif ($mode == 2) {
	# Selecting the sent mail folder
	my $sf = "$folders_dir/sentmail";
	print &ui_table_row($text{'edit_sent'},
		&ui_radio("sent_def", $folder->{'file'} eq $sf ? 1 : 0,
			  [ [ 1, $text{'edit_sent1'} ],
			    [ 0, $text{'edit_sent0'} ] ])." ".
		&ui_textbox("sent", $folder->{'file'} eq $sf ? "" :
					$folder->{'file'}, 40)." ".
		&file_chooser_button("sent"));
	}

&show_folder_options($folder, $mode);

print &ui_table_end();
if ($in{'new'}) {
	print &ui_form_end([ [ undef, $text{'create'} ] ]);
	}
else {
	print &ui_form_end([ [ undef, $text{'save'} ],
			     $mode == 2 ? ( ) :
				( [ 'delete', $text{'delete'} ] ) ]);
	}

&ui_print_footer("list_folders.cgi", $text{'folders_return'});
