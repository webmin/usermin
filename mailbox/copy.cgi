#!/usr/local/bin/perl
# Copy (or move) all messages from one folder to another

require './mailbox-lib.pl';
&ReadParse();
@folders = &list_folders();
$folder = $folders[$in{'idx'}];
$dest = $folders[$in{'dest'}];

&ui_print_unbuffered_header(undef, $text{'copy_title'}, "");

print &text('copy_doing', $folder->{'name'}, $dest->{'name'}),"<p>\n";
&mailbox_copy_folder($folder, $dest);
print $text{'copy_done'},"<p>\n";

if ($in{'move'}) {
	print &text('copy_deleting', $folder->{'name'}),"<p>\n";
	&mailbox_empty_folder($folder);
	print $text{'copy_done'},"<p>\n";
	}

&ui_print_footer($config{'mail_system'} == 4 ? "list_ifolders.cgi"
					     : "list_folders.cgi",
		 $text{'folders_return'});
