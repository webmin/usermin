#!/usr/local/bin/perl
# index.cgi
# List the mail messages for the user

require './mailbox-lib.pl';
&ReadParse();

&open_dsn_hash();

@folders = &list_folders_sorted();
if (defined($in{'id'})) {
	# Folder ID specified .. convert to index
	$idf = &find_named_folder($in{'id'}, \@folders);
	$in{'folder'} = $idf->{'index'} if ($idf);
	}
elsif (!defined($in{'folder'}) && $userconfig{'default_folder'}) {
	# No folder specified .. find the default by preferences
	$df = &find_named_folder($userconfig{'default_folder'}, \@folders);
	$in{'folder'} = $df->{'index'} if ($df);
	}
# Get the folder by index
($folder) = grep { $_->{'index'} == $in{'folder'} } @folders;

# Show page header
print "Refresh: $userconfig{'refresh'}\r\n"
	if ($userconfig{'refresh'});
($qtotal, $qcount, $totalquota, $countquota) = &get_user_quota();
if ($totalquota) {
	push(@topright, &text('mail_quota', &nice_size($qtotal),
				     &nice_size($totalquota)));
	}
if (($folder->{'type'} == 2 || $folder->{'type'} == 4) &&
    $folder->{'mode'} == 3 && defined($folder->{'user'}) &&
    !$folder->{'autouser'}) {
	push(@topright, "<a href='inbox_logout.cgi?folder=$folder->{'index'}'>".
			($folder->{'type'} == 2 ? $text{'mail_logout'}
						: $text{'mail_logout2'}).
			"</a>");
	}
&ui_print_header(undef, &text('index_title', $folder->{'name'}), "", undef,
		 1, 1, 0, join("<br>", @topright));
print &check_clicks_function();

# Check if this is a POP3 or IMAP inbox with no login set
if (($folder->{'type'} == 2 || $folder->{'type'} == 4) &&
    $folder->{'mode'} == 3 && !$folder->{'autouser'} && !$folder->{'user'}) {
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

# Get folder-selection HTML
$sel = &folder_select(\@folders, $folder, "id", undef, 1, 1);

# Work out start from jump page
$perpage = $folder->{'perpage'} || $userconfig{'perpage'} || 20;
if ($in{'jump'} =~ /^\d+$/ && $in{'jump'} > 0) {
	$in{'start'} = ($in{'jump'}-1)*$perpage;
	}

# View mail in sort order
@mail = &mailbox_list_mails_sorted(
		int($in{'start'}), int($in{'start'})+$perpage-1,
	        $folder, 1, \@error);
if ($in{'start'} >= @mail && $in{'jump'}) {
	# Jumped too far!
	$in{'start'} = @mail - $perpage;
	@mail = &mailbox_list_mails_sorted(int($in{'start'}),
					   int($in{'start'})+$perpage-1,
					   $folder, 1, \@error);
	}

# Show page flipping arrows
&show_arrows();

# Work out displayed range
$start = int($in{'start'});
$end = $in{'start'}+$perpage-1;
$end = scalar(@mail)-1 if ($end >= scalar(@mail));

# Start of form
print &ui_form_start("delete_mail.cgi", "post");
print &ui_hidden("folder", $folder->{'index'});
print &ui_hidden("mod", &modification_time($folder));
print &ui_hidden("start", $in{'start'});

# Buttons at top
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
	($sortfield, $sortdir) = &get_sort_field($folder);
	if ($sortfield) {
		# Show un-sort link
		push(@links, "<a href='sort.cgi?folder=$folder->{'index'}&start=$start'>$text{'mail_nosort'}</a>");
		}
	print &ui_links_row(\@links);
	}

# Generate mail list headers
$showto = $folder->{'show_to'};
$showfrom = $folder->{'show_from'};
if (@mail) {
	@cols = ( "" );
	@tds = ( "width=5" );
	if ($showfrom) {
		push(@cols, &field_sort_link($text{'mail_from'}, "from",
					     $folder, $in{'start'}));
		push(@tds, $showto ? "width=15%" : "width=30%");
		}
	if ($showto) {
		push(@cols, &field_sort_link($text{'mail_to'}, "to",
					     $folder, $in{'start'}));
		push(@tds, $showfrom ? "width=15%" : "width=30%");
		}
	push(@cols, &field_sort_link($text{'mail_date'}, "date",
                                      $folder, $in{'start'}));
	push(@tds, "nowrap width=15%");
	push(@cols, &field_sort_link($text{'mail_size'}, "size",
                                      $folder, $in{'start'}));
	push(@tds, "nowrap width=10%");
	if ($folder->{'spam'}) {
		push(@cols, &field_sort_link($text{'mail_level'}, "x-spam-status",
					      $folder, $in{'start'}));
		push(@tds, "width=2%");
		}
	push(@cols, &field_sort_link($text{'mail_subject'}, "subject",
                                      $folder, $in{'start'}));
	push(@tds, "width=50%");
	print &ui_columns_start(\@cols, "100", 0, \@tds);
	}
if (@error) {
	print "<center><b><font color=#ff0000>\n";
	print &text('mail_err', $error[0] == 0 ? $error[1] :
			      &text('save_elogin', $error[1])),"\n";
	print "</font></b></center>\n";
	}

# Pre-check for attachments for the whole list
&mail_has_attachments([ map { $mail[$_] } ($start .. $end) ], $folder);

# Show the actual email
for(my $i=$start; $i<=$end; $i++) {
	local ($bs, $be);
	$m = $mail[$i];
	$mid = $m->{'header'}->{'message-id'};
	$r = &get_mail_read($folder, $m);
	if ($r&2) {
		# Special
		($bs, $be) = ("<b><i>", "</i></b>");
		}
	elsif (($r&1) == 0) {
		# Unread
		($bs, $be) = ("<b>", "</b>");
		}
	&notes_decode($m, $folder);
	local $idx = $m->{'idx'};
	local $id = $m->{'id'};
	local @cols;

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
	push(@cols, $bs.&simplify_date($m->{'header'}->{'date'}).$be);
	push(@cols, $bs.&nice_size($m->{'size'}, 1024).$be);

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
	local @icons = &message_icons($m, $folder->{'sent'}, $folder);
	push(@cols, $bs.&simplify_subject($m->{'header'}->{'subject'}).
		    " ".join("&nbsp;", @icons).$be);

	# Detect IMAP deleted mail
	if ($m->{'deleted'}) {
		foreach my $c (@cols) {
			$c = "<strike>$c</strike>";
			}
		}

	if (&editable_mail($m)) {
		print &ui_checked_columns_row(\@cols, \@tds, "d", $id);
		}
	else {
		print &ui_columns_row([ "", @cols ], \@tds);
		}
	&update_delivery_notification($mail[$i], $folder);

	# Show part of the body too
	if ($userconfig{'show_body'}) {
		&parse_mail($m);
		local $data = &mail_preview($m);
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
@grid = ( );
print "<table width=100%>\n";

if (@mail) {
	$jumpform = (@mail > $perpage);
	if ($folder->{'searchable'}) {
		# Simple search
		$ssform = &ui_form_start("mail_search.cgi");
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
			    &ui_textbox("jump", int($in{'start'} / $perpage)+1,
					3)." $text{'mail_of'} ".
					   (int(@mail / $perpage)+1).
			    &ui_form_end());
		}
	}


# Address book button
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

# Sig editor
if (&get_signature_file()) {
	push(@grid, &ui_form_start("edit_sig.cgi").
		    &ui_submit($text{'mail_sig'}).
		    &ui_form_end());
	}

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

&ui_print_footer("/", $text{'index'});
&pop3_logout();

# show_arrows()
# Prints HTML for previous/next page arrows
sub show_arrows
{
print "<center>\n";
print "<form action=index.cgi><font size=+1>\n";

# Show left arrow to go to start of folder
if ($in{'start'}) {
	printf "<a href='index.cgi?start=%d&folder=%d'>%s</a>\n",
		0, $in{'folder'},
		'<img src=../images/first.gif border=0 align=middle>';
	}
else {
	print "<img src=../images/first-grey.gif align=middle>\n";
	}

# Show left arrow to decrease start
if ($in{'start'}) {
	printf "<a href='index.cgi?start=%d&folder=%d'>%s</a>\n",
		$in{'start'}-$perpage, $in{'folder'},
		'<img src=../images/left.gif border=0 align=middle>';
	}
else {
	print "<img src=../images/left-grey.gif align=middle>\n";
	}

local $s = $in{'start'}+1;
local $e = $in{'start'}+$perpage;
$e = scalar(@mail) if ($e > @mail);
if (@mail) {
	print &text('mail_pos', $s, $e, scalar(@mail), $sel);
	}
else {
	print &text('mail_none', $sel);
	}
print "</font><input type=submit value='$text{'mail_fchange'}'>\n";

# Show right arrow to increase start
if ($in{'start'}+$perpage < @mail) {
	printf "<a href='index.cgi?start=%d&folder=%d'>%s</a>\n",
		$in{'start'}+$perpage, $in{'folder'},
		'<img src=../images/right.gif border=0 align=middle>';
	}
else {
	print "<img src=../images/right-grey.gif align=middle>\n";
	}

# Show right arrow to go to end
if ($in{'start'}+$perpage < @mail) {
	printf "<a href='index.cgi?start=%d&folder=%d'>%s</a>\n",
		int((scalar(@mail)-$perpage-1)/$perpage + 1)*$perpage, $in{'folder'},
		'<img src=../images/last.gif border=0 align=middle>';
	}
else {
	print "<img src=../images/last-grey.gif align=middle>\n";
	}

if ($folder->{'msg'}) {
	print "<br>$folder->{'msg'}\n";
	}
print "</form></center>\n";
}

