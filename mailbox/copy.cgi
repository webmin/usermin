#!/usr/local/bin/perl
# Copy (or move) all messages from one folder to another
use strict;
use warnings;
our (%text, %in, %config);

require './mailbox-lib.pl';
&ReadParse();
my @folders = &list_folders();
my $folder = $folders[$in{'idx'}];
my $dest = $folders[$in{'dest'}];

&ui_print_unbuffered_header(undef, $text{'copy_title'}, "");

print &text('copy_doing', &html_escape($folder->{'name'}), &html_escape($dest->{'name'})),"<p>\n";
&mailbox_copy_folder($folder, $dest);
print $text{'copy_done'},"<p>\n";

if ($in{'move'}) {
	print &text('copy_deleting', &html_escape($folder->{'name'})),"<p>\n";
	&mailbox_empty_folder($folder);
	print $text{'copy_done'},"<p>\n";
	}

&ui_print_footer($config{'mail_system'} == 4 ? "list_ifolders.cgi"
					     : "list_folders.cgi",
		 $text{'folders_return'});
