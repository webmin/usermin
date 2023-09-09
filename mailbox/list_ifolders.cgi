#!/usr/local/bin/perl
# Display a list of IMAP folders, and allow addition and deletion
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in);

require './mailbox-lib.pl';
&ui_print_header(undef, $text{'folders_title'}, "");

print &ui_form_start("delete_folders.cgi", "post");
my @tds = ( "width=5" );
my @folders = &list_folders_sorted();
foreach my $folder (@folders) {
	$folder->{'file'} = &html_escape($folder->{'file'})
		if ($folder->{'file'});
	}
my @adders = ( "<a href='edit_ifolder.cgi?new=1'>$text{'folders_addimap'}</a>",
	    "<a href='edit_comp.cgi?new=1'>$text{'folders_addcomp'}</a>",
	    "<a href='edit_virt.cgi?new=1'>$text{'folders_addvirt'}</a>" );
print &ui_links_row(\@adders);
print &ui_columns_start([ "",
			  $text{'folders_name'},
			  $text{'folders_type'},
			  $text{'folders_size'},
			  $text{'folders_action'} ], undef, 0, \@tds);
foreach my $f (@folders) {
	my @cols;
	my $deletable = 0;
	if ($f->{'inbox'} || $f->{'drafts'} || $f->{'spam'}) {
		# Inbox, drafs or spam folder which cannot be edited
		push(@cols, &html_escape($f->{'name'}));
		push(@cols, "IMAP");
		push(@cols, &nice_size(&folder_size($f)));
		}
	elsif ($f->{'type'} == 5) {
		# Link for editing composite folder
		push(@cols, &ui_link("edit_comp.cgi?idx=$f->{'index'}",
				     &html_escape($f->{'name'})));
		push(@cols, $text{'folders_comp'});
		push(@cols, &nice_size(&folder_size($f)));
		$deletable = 1;
		}
	elsif ($f->{'type'} == 6) {
		# Link for editing virtual folder
		push(@cols, &ui_link("edit_virt.cgi?idx=$f->{'index'}",
				     &html_escape($f->{'name'})));
		push(@cols, $text{'folders_virt'});
		push(@cols, undef);
		$deletable = 1;
		}
	else {
		# Edit an IMAP folder
		push(@cols, &ui_link("edit_ifolder.cgi?idx=$f->{'index'}",
			    	     &html_escape($f->{'name'})));
		push(@cols, "IMAP");
		push(@cols, &nice_size(&folder_size($f)));
		$deletable = 1;
		}
	if ($f->{'inbox'} || $f->{'sent'} || $f->{'drafts'}) {
		$cols[0] = "<b>".$cols[0]."</b>";
		}

	# Action links
	my @acts;
	push(@acts, "<a href='index.cgi?folder=$f->{'index'}'>".
		    "$text{'folders_view'}</a>");
	if (!$f->{'nowrite'}) {
		my ($is, $ie);
		my $auto = &get_auto_schedule($f);
		if ($auto && $auto->{'enabled'}) {
			($is, $ie) = ("<b>", "</b>");
			}
		push(@acts, $is."<a href='edit_auto.cgi?idx=$f->{'index'}'>".
			    "$text{'folders_auto'}</a>".$ie);
		}
	push(@acts, "<a href='copy_form.cgi?idx=$f->{'index'}'>".
		    "$text{'folders_copy'}</a>");
	push(@cols, join(" | ", @acts));
	if ($deletable) {
		print &ui_checked_columns_row(\@cols, \@tds,
					      "d", $f->{'index'});
		}
	else {
		print &ui_columns_row([ "", @cols ], \@tds);
		}
	}
print &ui_columns_end();
print &ui_links_row(\@adders);
print &ui_form_end([ [ "delete", $text{'folders_delete'} ] ]);

# Refresh left frame if needed
if ($in{'refresh'}) {
	my ($folder) = grep { $_->{'name'} eq $in{'refresh'} } @folders;
	if (defined(&theme_post_save_folder)) {
		&theme_post_save_folder($folder, 'modify');
		}
	}

&ui_print_footer("", $text{'index'});
