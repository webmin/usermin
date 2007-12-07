#!/usr/local/bin/perl
# search_form.cgi
# Display a form for searching a mailbox

require './mailbox-lib.pl';
&ReadParse();
@folders = &list_folders_sorted();
($folder) = grep { $_->{'index'} == $in{'folder'} } @folders;
&set_module_index($in{'folder'});
&ui_print_header(undef, $text{'sform_title'}, "");

print &ui_form_start("mail_search.cgi");
print &ui_table_start($text{'sform_header'}, "width=100%", 2);

# And/or mode
print &ui_table_row($text{'sform_andmode'},
		&ui_radio("and", 1, [ [ 1, $text{'sform_and'} ],
				      [ 0, $text{'sform_or'} ] ]));

# Criteria table
$ctable = &ui_columns_start([ ], 50, 1);

for($i=0; $i<=4; $i++) {
	local @cols;
	push(@cols, $text{'sform_where'});
	push(@cols, &ui_select("field_$i", undef,
			[ [ undef, "&nbsp;" ],
			  map { [ $_, $_ eq 'all' ? $text{'sform_allmsg'}
						  : $text{"sform_".$_} ] }
			      ( 'from', 'subject', 'to', 'cc', 'date',
				'body', 'headers', 'all', 'size') ]));

	push(@cols, &ui_select("neg_$i", 0,
			[ [ 0, $text{'sform_neg0'} ],
			  [ 1, $text{'sform_neg1'} ] ]));

	push(@cols, $text{'sform_text'});
	push(@cols, &ui_textbox("what_$i", undef, 30));
	$ctable .= &ui_columns_row(\@cols, [ map { "nowrap" } @cols ]);
	}
$ctable .= &ui_columns_end();
print &ui_table_row(" ", $ctable, 1);

# Status to find
print &ui_table_row($text{'search_status'},
      &ui_radio("status_def", 1,
		[ [ 1, $text{'search_allstatus'} ],
		  [ 0, $text{'search_onestatus'} ] ])." ".
		&ui_select("status", 2,
			   [ [ 0, $text{'view_mark0'} ],
			     [ 1, $text{'view_mark1'} ],
			     [ 2, $text{'view_mark2'} ] ]));

# Limit on number of messages to search
print &ui_table_row($text{'search_latest'},
	&ui_opt_textbox("limit", $userconfig{'search_latest'}, 10,
			$text{'search_nolatest'}, $text{'search_latestnum'}));

# Destination for search
print &ui_table_row($text{'search_dest'},
	&ui_opt_textbox("dest", undef, 30, $text{'search_dest1'}."<br>",
					   $text{'search_dest0'}));

# Folder to search
@sfolders = grep { $_->{'id'} != $search_folder_id } @folders;
print &ui_table_row($text{'sform_folder2'},
	&folder_select(\@sfolders, $folder, "folder",
		       [ [ -1, $text{'sform_all'} ],
			 [ -2, $text{'sform_local'} ] ]));
print &ui_table_end();
print &ui_form_end([ [ undef, $text{'sform_ok'} ] ]);

&ui_print_footer("index.cgi?folder=$in{'folder'}", $text{'mail_return'});

