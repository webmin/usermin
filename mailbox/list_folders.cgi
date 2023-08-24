#!/usr/local/bin/perl
# list_folders.cgi
# Display a list of all folders and allows additional and deletion
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in);
our %folder_types;
our $remote_user;

require './mailbox-lib.pl';
&ui_print_header(undef, $text{'folders_title'}, "");
&ReadParse();

# Help text
print &ui_hidden_start($text{'folders_instr'}, "instr", $in{'instr'},
		       "list_folders.cgi");
print "$text{'folders_desc2'}<br>\n";
print "<ul>\n";
foreach my $ft ('sys', 'local', 'ext', 'pop3', 'imap', 'comp', 'virt') {
	print "<li>",$text{'folders_desc'.$ft},"\n"
		if ($ft eq "sys" || $folder_types{$ft});
	}
print "</ul>\n";
print &ui_hidden_end("instr");

print &ui_form_start("delete_folders.cgi", "post");
my @tds = ( "width=5" );
my @folders = &list_folders_sorted();
foreach my $folder (@folders) {
	$folder->{'file'} = &html_escape($folder->{'file'})
		if ($folder->{'file'});
	}
print &ui_columns_start([ "",
			  $text{'folders_name'},
			  $text{'folders_path'},
			  $text{'folders_type'},
			  $text{'folders_size'},
			  $text{'folders_action'} ], undef, 0, \@tds);
			#   var_dump(\@folders);
foreach my $f (@folders) {
	my @cols;
	my $deletable = 0;
	if ($f->{'inbox'} || $f->{'drafts'} || $f->{'spam'}) {
		# Inbox, drafs or spam folder which cannot be edited
		push(@cols, &html_escape($f->{'name'}));
		}
	elsif ($f->{'type'} == 2) {
		# Link for editing POP3 folder
		push(@cols, &ui_link("edit_pop3.cgi?idx=$f->{'index'}",
				     &html_escape($f->{'name'})));
		$deletable = 1;
		}
	elsif ($f->{'type'} == 4) {
		# Link for editing IMAP folder
		push(@cols, &ui_link("edit_imap.cgi?idx=$f->{'index'}",
				     &html_escape($f->{'name'})));
		$deletable = 1;
		}
	elsif ($f->{'mode'} == 2 && !$folder_types{'ext'}) {
		# Sent mail folder can only be changed if external folders
		# are allowed
		push(@cols, &html_escape($f->{'name'}));
		}
	elsif ($f->{'type'} == 5) {
		# Link for editing composite folder
		push(@cols, &ui_link("edit_comp.cgi?idx=$f->{'index'}",
				     &html_escape($f->{'name'})));
		$deletable = 1;
		}
	elsif ($f->{'type'} == 6) {
		# Link for editing virtual folder
		push(@cols, &ui_link("edit_virt.cgi?idx=$f->{'index'}",
				     &html_escape($f->{'name'})));
		$deletable = 1;
		}
	else {
		# Link for editing local or external folder
		push(@cols, &ui_link("edit_folder.cgi?idx=$f->{'index'}",
				     &html_escape($f->{'name'})));
		$deletable = 1;
		}
	if ($f->{'type'} == 2 || $f->{'type'} == 4) {
		# Show mail server
		my $user = $f->{'user'} eq '*' ? $remote_user : $f->{'user'};
		push(@cols, &text(
			$f->{'port'} ? 'folders_servp' : 'folders_serv',
			"<tt>$user</tt>", "<tt>$f->{'server'}</tt>",
			"<tt>$f->{'port'}</tt>"));
		push(@cols, $f->{'type'} == 2 ? "POP3" : "IMAP");
		push(@cols, undef);
		}
	elsif ($f->{'type'} == 5) {
		# Show number of sub-folders and total size
		push(@cols, &text('folders_num',
				   scalar(@{$f->{'subfolders'}}),
				   &mailbox_folder_size($f, 1)));
		push(@cols, $text{'folders_comp'});
		push(@cols, &nice_size(&folder_size($f)));
		}
	elsif ($f->{'type'} == 6) {
		# Show number of messages
		push(@cols, &text('folders_vnum', &mailbox_folder_size($f, 1)));
		push(@cols, $text{'folders_virt'});
		push(@cols, undef);
		}
	else {
		# Show folder directory and size
		my $mf = &folder_file($f);
		push(@cols, $mf);
		push(@cols, $f->{'type'} == 1 ? $text{'folders_maildir'} :
			    $f->{'type'} == 3 ? $text{'folders_mhdir'} :
					        $text{'folders_mbox'});
		push(@cols, &nice_size(&folder_size($f)));
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
print &ui_form_end([ [ "delete", $text{'folders_delete'} ] ]);

# Show form for adding a folder
print &ui_form_start("newfolder.cgi");
my @folder_progs = ( [ "edit_folder.cgi?new=1&mode=0", "local" ],
		  [ "edit_folder.cgi?new=1&mode=1", "ext" ],
		  [ "edit_pop3.cgi?new=1", "pop3" ],
		  [ "edit_imap.cgi?new=1", "imap" ],
		  [ "edit_comp.cgi?new=1", "comp" ],
		  [ "edit_virt.cgi?new=1", "virt" ] );
my @can_folder_progs = grep { $folder_types{$_->[1]} } @folder_progs;
if (@can_folder_progs) {
	print &ui_submit($text{'folders_newfolder'}),"\n";
	print &ui_select("prog", $can_folder_progs[0]->[0],
			 [ map { [ $_->[0], $text{'folders_type_'.$_->[1]} ] }
			       @can_folder_progs ]),"\n";
	print "<br>\n";
	}
print &ui_form_end();

# Refresh left frame if needed
if ($in{'refresh'}) {
	my ($folder) = grep { $_->{'name'} eq $in{'refresh'} } @folders;
	if (defined(&theme_post_save_folder)) {
		&theme_post_save_folder($folder, 'modify');
		}
	}

&ui_print_footer("", $text{'index'});
