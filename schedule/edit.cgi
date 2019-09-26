#!/usr/local/bin/perl
# Show a form to create or edit a scheduled email

require './schedule-lib.pl';
&ReadParse();
if ($in{'new'}) {
	&ui_print_header(undef, $text{'edit_title1'}, "");
	$sched = { 'enabled' => 1,
		   'delete_after' => 0,
		   'at' => time(),
		   'mins' => 0,
		   'hours' => 0,
		   'days' => '*',
		   'months' => '*',
		   'weekdays' => '*' };
	}
else {
	&ui_print_header(undef, $text{'edit_title2'}, "");
	$sched = &get_schedule($in{'id'});
	}

print &ui_form_start("save.cgi", "form-data");
print &ui_hidden("new", $in{'new'}),"\n";
print &ui_hidden("id", $in{'id'}),"\n";
print &ui_table_start($text{'edit_header'}, "width=100%", 2);

print &ui_table_row($text{'edit_subject'},
		    &ui_textbox("subject", $sched->{'subject'}, 50));

$myaddr = &my_email_address();
if ($mailbox::config{'edit_from'} == 1) {
	# From address field, if allowed
	print &ui_table_row($text{'edit_from'},
			    &ui_radio("from_def", $sched->{'from'} ? 0 : 1,
			      [ [ 1, &text('edit_self', $myaddr)."<br>" ],
				[ 0, $text{'edit_addr'} ] ])."\n".
			    &ui_textbox("from", $sched->{'from'}, 30)." ".
			    &mailbox::address_button("from", 0, 1));
	}

# To address
print &ui_table_row($text{'edit_to'},
		    &ui_radio("to_def", $sched->{'to'} ? 0 : 1,
			      [ [ 1, &text('edit_self', $myaddr)."<br>" ],
				[ 0, $text{'edit_addr'} ] ])."\n".
		    &ui_textbox("to", $sched->{'to'}, 60)." ".
		    &mailbox::address_button("to", 0));

# Cc and Bcc addresses
print &ui_table_row($text{'edit_cc'},
		    &ui_textbox("cc", $sched->{'cc'}, 60)." ".
		    &mailbox::address_button("cc", 0));
print &ui_table_row($text{'edit_bcc'},
		    &ui_textbox("bcc", $sched->{'bcc'}, 60)." ".
		    &mailbox::address_button("bcc", 0));


print &ui_table_row($text{'edit_mail'},
		    &ui_textarea("mail", $sched->{'mail'}, 12, 70)."<br>".
		    ($config{'attach'} ?
		      &ui_checkbox("mail_def", 1, $text{'edit_mailfile'},
				   $sched->{'mailfile'} ? 1 : 0)."\n".
		      &ui_textbox("mailfile", $sched->{'mailfile'}, 30)."\n".
		      &file_chooser_button("mailfile") ."<br>" : "") .
		    (ui_checkbox("is_html", 1, $text{'edit_html'},
				   $sched->{'is_html'} ? 1 : 0)));


if ($config{'upload'}) {
	
	print &ui_table_hr();
	
	# Attached files
	@files = &list_schedule_files($sched);
	if (@files) {
		$ftable = &ui_columns_start([
			$text{'delete'}, $text{'edit_file'}, $text{'edit_size'}, $text{'edit_type'} ]);
		foreach $f (@files) {
			$ftable .= &ui_columns_row([
				&ui_checkbox("d", $f->{'id'}),
				"<a href='view.cgi?sched=$sched->{'id'}&id=".&urlize($f->{'id'})."'>".&html_escape($f->{'id'})."</a>",
				$f->{'size'},
				!$f->{'type'} ? "<tt>$f->{'file'}</tt>"
					     : $text{'edit_uploaded'}
				]);
			}
		$ftable .= &ui_columns_end();
		print &ui_table_row($text{'edit_files'}, $ftable);
		}

	# Form to add a file
	print &ui_table_row($text{'edit_upload1'},
		&ui_upload("upload0", 60, undef, undef, 1));

	# Form to server attach a file
	print &ui_table_row($text{'edit_upload2'}, (&ui_textbox("upload1", undef, 30, 0). 
							&file_chooser_button("upload1")));
	}

print &ui_table_hr();

print &ui_table_row($text{'edit_delete'},
		    &ui_radio("delete_after", $sched->{'delete_after'},
			      [ [ 1, $text{'yes'} ], [ 0, $text{'no'} ] ]));

print &ui_table_row($text{'edit_enabled'},
		    &ui_radio("enabled", $sched->{'enabled'},
			      [ [ 1, $text{'yes'} ], [ 0, $text{'no'} ] ]));

@tm = $sched->{'at'} ? localtime($sched->{'at'}) : ( );
if (@tm) {
	$tm[1] = sprintf("%2.2d", $tm[1]);
	$tm[2] = sprintf("%2.2d", $tm[2]);
	$tm[3] = sprintf("%2.2d", $tm[3]);
	$tm[4] += 1;
	$tm[5] += 1900;
	}
print &ui_table_row($text{'edit_mode'},
		    &ui_oneradio("mode", 1, $text{'edit_at'},
				 $sched->{'at'} ? 1 : 0)."\n".
		     &ui_textbox("hour", $tm[2], 3).":".
		     &ui_textbox("min", $tm[1], 3)." &nbsp;&nbsp;&nbsp; ".
		     &ui_date_input($tm[3], $tm[4], $tm[5],
				    "day", "month", "year")." ".
		     &date_chooser_button("day", "month", "year")."<br>".
		    &ui_oneradio("mode", 0, $text{'edit_cron'},
				 $sched->{'at'} ? 0 : 1));

print "<tr> <td colspan=2><table border width=100%>\n";
&cron::show_times_input($sched);
print "</table></td> </tr>\n";

print &ui_table_end();
print &ui_form_end($in{'new'} ? [ [ "create", $text{'create'} ] ] :
				[ [ "save", $text{'save'} ],
				  [ "delete", $text{'delete'} ] ], "100%");

&ui_print_footer("", $text{'index_return'});
