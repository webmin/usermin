#!/usr/local/bin/perl
# index.cgi
# List the mail messages for the user
use strict;
use warnings;
our (%text, %in, %userconfig, %config);
our ($remote_user, $remote_pass);
our $special_folder_id;
our $plen;
our ($cb); # XXX
our $search_folder_id;

require './mailbox-lib.pl';
&ReadParse();

&open_dsn_hash();

my @folders = &list_folders_sorted();
if (defined($in{'id'})) {
	# Folder ID specified .. convert to index
	my $idf = &find_named_folder($in{'id'}, \@folders);
	$in{'folder'} = $idf->{'index'} if ($idf);
	}
elsif (!defined($in{'folder'}) && $userconfig{'default_folder'}) {
	# No folder specified .. find the default by preferences
	my $df = &find_named_folder($userconfig{'default_folder'}, \@folders);
	$in{'folder'} = $df->{'index'} if ($df);
	}
# Get the folder by index
my ($folder) = grep { $_->{'index'} == $in{'folder'} } @folders;

# Show page header
print "Refresh: $userconfig{'refresh'}\r\n"
	if ($userconfig{'refresh'});
my ($qtotal, $qcount, $totalquota, $countquota) = &get_user_quota();
my @topright;
if ($totalquota) {
	push(@topright, &text('mail_quota', &nice_size($qtotal),
				     &nice_size($totalquota)));
	}
if (($folder->{'type'} == 2 || $folder->{'type'} == 4) &&
    $folder->{'mode'} == 3 && defined($folder->{'user'}) &&
    !$folder->{'autouser'} && !$folder->{'nologout'}) {
	push(@topright, "<a href='inbox_logout.cgi?folder=$folder->{'index'}'>".
			($folder->{'type'} == 2 ? $text{'mail_logout'}
						: $text{'mail_logout2'}).
			"</a>");
	}


# Check if this is a POP3 or IMAP inbox with no login set
if (($folder->{'type'} == 2 || $folder->{'type'} == 4) &&
    $folder->{'mode'} == 3 && !$folder->{'autouser'} && !$folder->{'user'}) {
	&ui_print_header(undef, &text('index_title', $folder->{'name'}), "",
			 undef, 1, 1, 0, join("<br>", @topright));
	print &ui_form_start("inbox_login.cgi", "post");
	print &ui_hidden("folder", $folder->{'index'}),"\n";
	print &ui_table_start(
	      $folder->{'type'} == 2 ? $text{'mail_loginheader'}
				     : $text{'mail_loginheader2'}, undef, 2);
	print &ui_table_row(undef, &text('mail_logindesc',
					 "<tt>$folder->{'server'}</tt>"), 2);

	print &ui_table_row($text{'mail_loginuser'},
			    &ui_textbox("user", $remote_user, 30));
	print &ui_table_row($text{'mail_loginpass'},
			    &ui_password("pass", $remote_pass, 30));

	print &ui_table_end();
	print &ui_form_end([ [ "login", $text{'mail_login'} ] ]);

	&ui_print_footer("/", $text{'index'});
	exit;
	}

# Work out start from jump page
my $perpage = $folder->{'perpage'} || $userconfig{'perpage'} || 20;
if ($in{'jump'} =~ /^\d+$/ && $in{'jump'} > 0) {
	$in{'start'} = ($in{'jump'}-1)*$perpage;
	}

# Get email to show, in order
my @error;
my @mail = &mailbox_list_mails_sorted(
		int($in{'start'}), int($in{'start'})+$perpage-1,
	        $folder, !$userconfig{'show_body'}, \@error);
if ($in{'start'} >= @mail && $in{'jump'}) {
	# Jumped too far!
	$in{'start'} = @mail - $perpage;
	@mail = &mailbox_list_mails_sorted(int($in{'start'}),
					   int($in{'start'})+$perpage-1,
					   $folder, !$userconfig{'show_body'},
					   \@error);
	}

# Show page title
&ui_print_header(undef, &text('index_title', $folder->{'name'}), "", undef,
		 1, 1, 0, join("<br>", @topright));

# Get folder-selection HTML
my $sel = &folder_select(\@folders, $folder, "id", undef, 1, 1);

# Show page flipping arrows
&show_arrows();

# If this is the search results folder, check if a search is in progress
if ($folder->{'id'} eq $search_folder_id) {
	my ($pid, $action) = &test_lock_folder($folder);
	if ($pid) {
		if ($action && $action->{'search'}) {
			print "<b>",&text('index_searching',
				"<i>".&html_escape($action->{'search'})."</i>"),
			      "</b><p>\n";
			}
		else {
			print "<b>",&text('index_searching2'),"</b><p>\n";
			}
		}
	}

# Work out displayed range
my $start = int($in{'start'});
my $end = $in{'start'}+$perpage-1;
$end = scalar(@mail)-1 if ($end >= scalar(@mail));

# Start of form
print &ui_form_start("delete_mail.cgi", "post");
print &ui_hidden("folder", $folder->{'index'});
print &ui_hidden("mod", &modification_time($folder));
print &ui_hidden("start", $in{'start'});

if (@error) {
	print "<center><b><font color=#ff0000>\n";
	print &text('mail_err', $error[0] == 0 ? $error[1] :
			      &text('save_elogin', $error[1])),"\n";
	print "</font></b></center>\n";
	}

# Buttons at top
my @links;
if ($userconfig{'top_buttons'} && @mail) {
	&show_mailbox_buttons(1, \@folders, $folder, \@mail);
	@links = ( &select_all_link("d", 1),
		   &select_invert_link("d", 1),
		   &select_status_link("d", 1, $folder, \@mail, $start, $end,
				       1, $text{'mail_selread'}),
		   &select_status_link("d", 1, $folder, \@mail, $start, $end,
				       0, $text{'mail_selunread'}),
		   &select_status_link("d", 1, $folder, \@mail, $start, $end,
				       2, $text{'mail_selspecial'}),
		 );
	my ($sortfield, $sortdir) = &get_sort_field($folder);
	if ($sortfield) {
		# Show un-sort link
		push(@links, "<a href='sort.cgi?folder=$folder->{'index'}&start=$start'>$text{'mail_nosort'}</a>");
		}
	print &ui_links_row(\@links);
	}

# Generate mail list headers
my $showto = $folder->{'show_to'};
my $showfrom = $folder->{'show_from'};
my @tds;
if (@mail) {
	my @cols = ( "" );
	@tds = ( "width=15" );
	if ($showfrom) {
		push(@cols, &field_sort_link($text{'mail_from'}, "from",
					     $folder, $in{'start'}));
		push(@tds, "");
		}
	if ($showto) {
		push(@cols, &field_sort_link($text{'mail_to'}, "to",
					     $folder, $in{'start'}));
		push(@tds, "");
		}
	push(@cols, &field_sort_link($text{'mail_date'}, "date",
                                      $folder, $in{'start'}));
	push(@tds, "nowrap");
	push(@cols, &field_sort_link($text{'mail_size'}, "size",
                                      $folder, $in{'start'}));
	push(@tds, "nowrap");
	if ($folder->{'spam'}) {
		push(@cols, &field_sort_link($text{'mail_level'},
				"x-spam-status", $folder, $in{'start'}));
		push(@tds, "");
		}
	push(@cols, &field_sort_link($text{'mail_subject'}, "subject",
                                      $folder, $in{'start'}));
	push(@tds, "");
	print &ui_columns_start(\@cols, 100, 0, \@tds);
	}

# Pre-check for attachments for the whole list
&mail_has_attachments([ map { $mail[$_] } ($start .. $end) ], $folder);

# Show the actual email
for(my $i=$start; $i<=$end; $i++) {
	my ($bs, $be);
	my @rowtds = @tds;
	my $m = $mail[$i];
	my $mid = $m->{'header'}->{'message-id'};
	my $r = &get_mail_read($folder, $m);
	if ($r&2) {
		# Special
		($bs, $be) = ("<b><i>", "</i></b>");
		}
	elsif (($r&1) == 0) {
		# Unread
		($bs, $be) = ("<b>", "</b>");
		}
	else {
		$bs = $be = "";
		}
	my $idx = $m->{'idx'};
	my $id = $m->{'id'};
	my @cols;

	# From and To columns, with links
	if ($showfrom) {
		push(@cols, $bs.&view_mail_link($folder, $id, $in{'start'},
				      $m->{'header'}->{'from'}).$be);
		}
	if ($showto) {
		push(@cols, $bs.&view_mail_link($folder, $id, $in{'start'},
		      $m->{'header'}->{'to'}).$be);
		}

	# Date and size columns
	push(@cols, $bs.&eucconv_and_escape(&simplify_date($m->{'header'}->{'date'})).$be);
	push(@cols, $bs.&nice_size($m->{'size'}, 1024).$be);
	$rowtds[$#cols] .= " data-sort=".$m->{'size'};

	# Spam score
	if ($folder->{'spam'}) {
		if ($m->{'header'}->{'x-spam-status'} =~ /(hits|score)=([0-9\.]+)/) {
			push(@cols, $bs.$2.$be);
			}
		else {
			push(@cols, "");
			}
		}

	# Subject column, with read/special icons
	my @icons = &message_icons($m, $folder->{'sent'}, $folder);
	push(@cols, $bs.&simplify_subject($m->{'header'}->{'subject'}).
		    " ".join("&nbsp;", @icons).$be);

	# Detect IMAP deleted mail
	if ($m->{'deleted'}) {
		foreach my $c (@cols) {
			$c = "<strike>$c</strike>";
			}
		}

	if (&editable_mail($m)) {
		print &ui_checked_columns_row(\@cols, \@rowtds, "d", $id);
		}
	else {
		print &ui_columns_row([ "", @cols ], \@rowtds);
		}
	&update_delivery_notification($mail[$i], $folder);

	# Show part of the body too
	if ($userconfig{'show_body'}) {
		$plen = $in{'show_body_len'} || $userconfig{'show_body_len'};
		&parse_mail($m);
		my $data = &mail_preview($m, $plen);
                if ($data) {
                        print "<tr $cb> <td colspan=",(scalar(@cols)+1),"><tt>",
                                &html_escape($data),"</tt></td> </tr>\n";
                        }
		}
	}
if (@mail) {
	print &ui_columns_end();
	print &ui_links_row(\@links);
	}

# Buttons at end of form
&show_mailbox_buttons(2, \@folders, $folder, \@mail);
print &ui_form_end();

if ($userconfig{'arrows'}) {
	# Show page flipping arrows
	print "<br>\n";
	&show_arrows();
	}

# Start section for end of page buttons, in a 3-wide grid
print "<hr>\n";
my @grid;
print "<table width=100%>\n";

if (@mail) {
	my $jumpform = (@mail > $perpage);
	if ($folder->{'searchable'}) {
		# Simple search
		my $ssform = &ui_form_start("mail_search.cgi");
		$ssform .= &ui_hidden("folder", $folder->{'index'});
		$ssform .= &ui_hidden("simple", 1);
		$ssform .= &ui_submit($text{'mail_search2'});
		$ssform .= &ui_textbox("search", undef, 20);
		$ssform .= &ui_form_end();
		push(@grid, $ssform);

		# Advanced search
		push(@grid, &ui_form_start("search_form.cgi").
			    &ui_hidden("folder", $folder->{'index'}).
			    &ui_submit($text{'mail_advanced'}, "advanced").
			    &ui_form_end());
		}

	if ($folder->{'spam'} && $folder->{'searchable'}) {
		# Spam level search
		push(@grid, &ui_form_start("mail_search.cgi").
			    &ui_hidden("folder", $folder->{'index'}).
			    &ui_hidden("spam", 1).
			    &ui_submit($text{'mail_search3'}).
			    &ui_textbox("score", undef, 5).
			    &ui_form_end());
		}
	if ($jumpform) {
		# Show page jump form
		push(@grid, &ui_form_start("index.cgi").
			    &ui_hidden("folder", $folder->{'index'}).
			    &ui_submit($text{'mail_jump'}).
			    &ui_textbox("jump",
					int(int($in{'start'}) / $perpage)+1,
					3)." $text{'mail_of'} ".
					   (int(@mail / $perpage)+1).
			    &ui_form_end());
		}
	}


# Address book button
no warnings "once";
if (!$main::mailbox_no_addressbook_button) {
	push(@grid, &ui_form_start("list_addresses.cgi").
		    &ui_submit($text{'mail_addresses'}).
		    &ui_form_end());
	}

# Folder management button
if (!$main::mailbox_no_folder_button) {
	push(@grid, &ui_form_start($config{'mail_system'} == 4 ?
				"list_ifolders.cgi" : "list_folders.cgi").
		    &ui_submit($text{'mail_folders'}).
		    &ui_form_end());
	}
	use warnings "once";

# Sig editor
push(@grid, &ui_form_start("edit_sig.cgi").
	    &ui_submit($text{'mail_sig'}).
	    &ui_form_end());

# Show button to delete all mail in folder
if (@mail && ($folder->{'trash'} || $userconfig{'show_delall'})) {
	push(@grid, &ui_form_start("delete_mail.cgi").
		    &ui_hidden("folder", $folder->{'index'}).
		    &ui_hidden("all", 1).
		    &ui_submit($folder->{'trash'} ? $text{'mail_deltrash'}
						  : $text{'mail_delall'},
			       "delete").
		    &ui_form_end());
	}

# Show special sync button
if ($folder->{'type'} == 6 && $folder->{'id'} == $special_folder_id) {
	push(@grid, &ui_form_start("specialsync.cgi").
		    &ui_submit($text{'mail_specialsync'}).
		    &ui_form_end());
	}

print &ui_grid_table(\@grid, 3, 100,
  [ "align=left width=33%", "align=center width=33%", "align=right width=33%" ],
  "cellpadding=0 cellspacing=0");

if ($in{'refresh'}) {
	# Previous CGI has asked for a theme refresh, due to read counts
	# possibly changing or a folder being added
	if (defined(&theme_post_save_folder)) {
		&theme_post_save_folder($folder,
			$in{'refresh'} == 2 ? 'create' : 'read');
		}
	}

&save_last_folder_id($folder);
&ui_print_footer("/", $text{'index'});
&pop3_logout();

# show_arrows()
# Prints HTML for previous/next page arrows
sub show_arrows
{
my $link = "index.cgi?folder=".$in{'folder'};
my $left = $in{'start'} ?
           $link."&start=".($in{'start'}-$perpage) : undef;
my $right = int($in{'start'})+$perpage < @mail ?
            $link."&start=".($in{'start'}+$perpage) : undef;
my $first = $in{'start'} ?
            $link."&start=0" : undef;
my $last = int($in{'start'})+$perpage < @mail ?
           $link."&start=".(int((scalar(@mail)-$perpage-1)/$perpage + 1)*$perpage) : undef;
my $s = @mail-$in{'start'};
my $e = @mail-$in{'start'}-$perpage+1;
print &ui_page_flipper(
	@mail ? &text('mail_pos', $e < 1 ? 1 : $e, $s, scalar(@mail), $sel)
	      : &text('mail_none', $sel),
	&ui_submit($text{'mail_fchange'}).&ui_hidden("user", $in{'user'}),
	"index.cgi",
	$left,
	$right,
	$first,
	$last,
	$folder->{'msg'},
	);
}
