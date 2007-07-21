#!/usr/local/bin/perl
# Delete a bunch of folders

require './mailbox-lib.pl';
&ReadParse();
&error_setup($text{'fdelete_err'});

# Get the folders
@folders = &list_folders();
@d = split(/\0/, $in{'d'});
@d || &error($text{'fdelete_enone'});
foreach $d (@d) {
	push(@dfolders, $folders[$d]);
	}
$redir = $config{'mail_system'} == 4 ? "list_ifolders.cgi"
				     : "list_folders.cgi";

if ($in{'confirm'}) {
	# Do the deletion
	foreach $f (@dfolders) {
		&delete_folder($f);
		}
	&redirect($redir);
	}
else {
	# Ask the user if he is sure
	&ui_print_header(undef, $text{'fdelete_title'}, "");

	# Get the total folder size, where mail will actually be lost
	local $sz = 0;
	foreach $f (@dfolders) {
		if ($d->{'type'} == 0) {
			$sz += &folder_size($f);
			}
		}

	print &ui_form_start("delete_folders.cgi");
	foreach $d (@d) {
		print &ui_hidden("d", $d),"\n";
		}
	print "<center><b>",
	      &text($sz ? 'fdelete_rusure' : 'fdelete_rusure2',
		    scalar(@dfolders), &nice_size($sz)),"</b></center><p>\n";
	print "<center>",&ui_submit($text{'fdelete_delete'}, "confirm"),
	      "</center>\n";
	print &ui_form_end();

	&ui_print_footer($redir, $text{'folders_return'});
	}

