#!/usr/local/bin/perl
# Display a list of IMAP folders, and allow addition and deletion

require './mailbox-lib.pl';
&ui_print_header(undef, $text{'folders_title'}, "");

print &ui_form_start("delete_folders.cgi", "post");
@tds = ( "width=5" );
@folders = &list_folders_sorted();
$adders = "<a href='edit_ifolder.cgi?new=1'>$text{'folders_addimap'}</a>\n".
	  "<a href='edit_comp.cgi?new=1'>$text{'folders_addcomp'}</a>\n".
	  "<a href='edit_virt.cgi?new=1'>$text{'folders_addvirt'}</a>\n";
print $adders;
print &ui_columns_start([ "",
			  $text{'folders_name'},
			  $text{'folders_type'},
			  $text{'folders_size'},
			  $text{'folders_action'} ], undef, 0, \@tds);
foreach $f (@folders) {
	local @cols;
	local $deletable = 0;
	if ($f->{'inbox'} || $f->{'drafts'} || $f->{'spam'}) {
		# Inbox, drafs or spam folder which cannot be edited
		push(@cols, $f->{'name'});
		push(@cols, "IMAP");
		push(@cols, &nice_size(&folder_size($f)));
		}
	elsif ($f->{'type'} == 5) {
		# Link for editing composite folder
		push(@cols, "<a href='edit_comp.cgi?idx=$f->{'index'}'>".
			    "$f->{'name'}</a>");
		push(@cols, $text{'folders_comp'});
		push(@cols, &nice_size(&folder_size($f)));
		$deletable = 1;
		}
	elsif ($f->{'type'} == 6) {
		# Link for editing virtual folder
		push(@cols, "<a href='edit_virt.cgi?idx=$f->{'index'}'>".
			    "$f->{'name'}</a>");
		push(@cols, $text{'folders_virt'});
		push(@cols, undef);
		$deletable = 1;
		}
	else {
		# Edit an IMAP folder
		push(@cols, "<a href='edit_ifolder.cgi?idx=$f->{'index'}'>".
			    "$f->{'name'}</a>");
		push(@cols, "IMAP");
		push(@cols, &nice_size(&folder_size($f)));
		$deletable = 1;
		}

	# Action links
	local @acts;
	push(@acts, "<a href='index.cgi?folder=$f->{'index'}'>".
		    "$text{'folders_view'}</a>");
	if (!$f->{'nowrite'}) {
		local ($is, $ie);
		$auto = &get_auto_schedule($f);
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
print $adders;
print &ui_form_end([ [ "delete", $text{'folders_delete'} ] ]);

&ui_print_footer("", $text{'index'});

