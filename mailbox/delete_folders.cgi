#!/usr/local/bin/perl
# Delete a bunch of folders
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in, %config);

require './mailbox-lib.pl';
&ReadParse();
&error_setup($text{'fdelete_err'});

# Get the folders
my @folders = &list_folders();
my @d = split(/\0/, $in{'d'});
@d || &error($text{'fdelete_enone'});
my @dfolders;
foreach my $d (@d) {
	push(@dfolders, $folders[$d]);
	}
my $redir = $config{'mail_system'} == 4 ? "list_ifolders.cgi"
				     : "list_folders.cgi";

if ($in{'confirm'}) {
	# Do the deletion
	foreach my $f (@dfolders) {
		&delete_folder($f);
		}
	&redirect($redir."?refresh=".&urlize($dfolders[0]->{'name'}));
	}
else {
	# Ask the user if he is sure
	&ui_print_header(undef, $text{'fdelete_title'}, "");

	# Get the total folder size, where mail will actually be lost
	my $sz = 0;
	foreach my $f (@dfolders) {
		if ($f->{'type'} == 0) {
			$sz += &folder_size($f);
			}
		}

	print &ui_form_start("delete_folders.cgi");
	foreach my $d (@d) {
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
