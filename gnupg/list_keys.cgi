#!/usr/local/bin/perl
# list_keys.cgi
# Display all keys in your keyring

require './gnupg-lib.pl';
&ui_print_header(undef, $text{'keys_title'}, "");

@keys = &list_keys();
print "$text{'keys_desc'}<p>\n";

# List of existing keys
print &ui_form_start("delete_keys.cgi", "post");
@links = ( &select_all_link("d"),
	   &select_invert_link("d") );
print &ui_links_row(\@links);
@tds = ( "width=5" );
print &ui_columns_start([ "",
			  $text{'keys_id'},
			  $text{'keys_secret'},
			  $text{'keys_date'},
			  $text{'keys_name'},
			  $text{'keys_email'} ], 100);
foreach $k (@keys) {
	local @cols;
	push(@cols, "<a href='edit_key.cgi?idx=$k->{'index'}'>$k->{'key'}</a>");
	push(@cols, $k->{'secret'} ? "<b>$text{'yes'}</b>"
				   : $text{'no'});
	push(@cols, $k->{'date'});
	push(@cols, join("<br>", map { &html_escape($_) } @{$k->{'name'}}));
	push(@cols, join("<br>", map { &html_escape($_) } @{$k->{'email'}}));
	if ($k->{'secret'}) {
		# Cannot delete secret keys this way
		print &ui_columns_row([ "", @cols ], \@tds);
		}
	else {
		print &ui_checked_columns_row(\@cols, \@tds, "d",$k->{'index'});
		}
	}
print &ui_columns_end();
print &ui_links_row(\@links);
print &ui_form_end([ [ "delete", $text{'keys_delete'} ] ]);

# Form for adding a key
print "<hr>\n";
print "$text{'keys_importdesc'}<p>\n";
print "<form action=import.cgi method=post enctype=multipart/form-data>\n";
print "<table>\n";

print "<tr> <td valign=top><b>$text{'keys_from'}</b></td>\n";
print "<td><input type=radio name=mode value=0 checked> $text{'keys_mode0'}\n";
print "<input type=file name=key><br>\n";

print "<input type=radio name=mode value=1> $text{'keys_mode1'}\n";
print "<input name=file size=35> ",&file_chooser_button("to"),"</td> </tr>\n";

print "</table>\n";
print "<input type=submit value='$text{'keys_import'}'></form>\n";

print "<hr>\n";
print &text('keys_recvdesc', "<tt>$config{'keyserver'}</tt>"),"<p>\n";
print "<form action=recv.cgi>\n";
print "<input type=submit value='$text{'keys_recv'}'>\n";
print "<input name=id size=10></form>\n";

&ui_print_footer("", $text{'index_return'});

