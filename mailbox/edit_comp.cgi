#!/usr/local/bin/perl
# edit_comp.cgi
# Display a form for creating or editing a composite folder
use strict;
use warnings;
our (%text, %in, %config);

require './mailbox-lib.pl';
&ReadParse();

my @folders = &list_folders();
my $folder;
if ($in{'new'}) {
	&ui_print_header(undef, $text{'edit_title1'}, "");
	}
else {
	&ui_print_header(undef, $text{'edit_title2'}, "");
	$folder = $folders[$in{'idx'}];
	}

# Form and table start
print &ui_form_start("save_comp.cgi");
print &ui_hidden("idx", $in{'idx'});
print &ui_hidden("new", $in{'new'});
print &ui_table_start($text{'edit_header'}, undef, 2);

# Folder type
print &ui_table_row($text{'edit_mode'}, $text{'edit_comp'});

# Folder name
print &ui_table_row($text{'edit_name'},
	&ui_textbox("name", $folder->{'name'}, 40));

# Composite folders
my @names = split(/\t+/, $folder->{'subfoldernames'});
my $ctable = "";
for(my $i=0; $i<10; $i++) {
	$ctable .= &ui_select("comp_$i",
			$names[$i],
			[ [ "", "&nbsp;" ],
			  map { [ $_->{'id'} || $_->{'file'} || $_->{'name'},
				  $_->{'name'} ] }
			  grep { $_->{'type'} != 5 &&
				 !$_->{'file'} || -e $_->{'file'} } @folders ]).
		   "<br>\n";
	}
print &ui_table_row($text{'edit_comps'}, $ctable);

&show_folder_options($folder);

print &ui_table_end();
if ($in{'new'}) {
	print &ui_form_end([ [ undef, $text{'create'} ] ]);
	}
else {
	print &ui_form_end([ [ undef, $text{'save'} ],
			     [ 'delete', $text{'delete'} ] ]);
	}

&ui_print_footer($config{'mail_system'} == 4 ? "list_ifolders.cgi"
					     : "list_folders.cgi",
		 $text{'folders_return'});
