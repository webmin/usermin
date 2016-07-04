#!/usr/local/bin/perl
# Show a form for copying or moving all email to another folder
use strict;
use warnings;
our (%text, %in, %config);

require './mailbox-lib.pl';
&ReadParse();
my @folders = &list_folders();
my $folder = $folders[$in{'idx'}];

&ui_print_header(undef, $text{'copy_title'}, "");

print &ui_form_start("copy.cgi");
print &ui_hidden("idx", $in{'idx'});
print &ui_table_start($text{'copy_header'}, undef, 2, [ "width=30%" ]);

# Source folder
print &ui_table_row($text{'copy_source'}, $folder->{'name'});

# Destination folder
my @dfolders = grep { !$_->{'nowrite'} && $_->{'index'} != $folder->{'index'} }
		 &list_folders_sorted();
print &ui_table_row($text{'copy_dest'},
	    &ui_select("dest", undef,
		       [ map { [ $_->{'index'}, $_->{'name'} ] } @dfolders ]));

# Move or copy
print &ui_table_row($text{'copy_move'},
		    &ui_yesno_radio("move", 0));

print &ui_table_end();
print &ui_form_end([ [ "copy", $text{'copy_ok'} ] ]);

&ui_print_footer($config{'mail_system'} == 4 ? "list_ifolders.cgi"
					     : "list_folders.cgi",
		 $text{'folders_return'});
