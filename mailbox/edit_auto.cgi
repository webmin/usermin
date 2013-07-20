#!/usr/local/bin/perl
# Show a form for setting up scheduled folder clearing

require './mailbox-lib.pl';
&ReadParse();
@folders = &list_folders();
$folder = $folders[$in{'idx'}];

&ui_print_header(undef, $text{'auto_title'}, "");

print &ui_form_start("save_auto.cgi");
print &ui_hidden("idx", $in{'idx'});
print &ui_table_start($text{'auto_header'}, undef, 2);

# Folder name
print &ui_table_row($text{'auto_name'}, $folder->{'name'});

# Auto-clearing enabled
$auto = &get_auto_schedule($folder);
$auto ||= { 'enabled' => 0, 'mode' => 0, 'days' => 30 };
print &ui_table_row($text{'auto_enabled'},
		    &ui_yesno_radio("enabled", int($auto->{'enabled'})));

# Deletion criteria
print &ui_table_row($text{'auto_mode'},
    &ui_radio("mode", int($auto->{'mode'}),
	[ [ 0, &text('auto_days',
		     &ui_textbox("days", $auto->{'days'}, 5))."<br>".
	       ("&nbsp;" x 4).&ui_checkbox("invalid", 1, $text{'auto_invalid'},
			    $auto->{'invalid'})."<br>" ],
	  [ 1, &text('auto_size',
		     &ui_bytesbox("size", $auto->{'size'}, 5)) ] ]));

# Delete whole mailbox, or just infringing mails, or move to another folder
@fopts = map { [ &folder_name($_), $_->{'name'} ] }
	     grep { &folder_name($_) ne &folder_name($folder) }
		  @folders;
print &ui_table_row($text{'auto_action'},
		    &ui_radio("all", int($auto->{'all'}),
			      [ [ 0, $text{'auto_action0'}."<br>" ],
				[ 1, $text{'auto_action1'}."<br>" ],
				[ 2, &text('auto_action2',
					&ui_select("dest", $auto->{'dest'},
						   \@fopts)) ] ]));

print &ui_table_end();
print &ui_form_end([ [ "save", $text{'save'} ] ]);

&ui_print_footer($config{'mail_system'} == 4 ? "list_ifolders.cgi"
					     : "list_folders.cgi",
		 $text{'folders_return'});
