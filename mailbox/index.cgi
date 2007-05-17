#!/usr/local/bin/perl
# index.cgi
# List the mail messages for the user

require './mailbox-lib.pl';
&ReadParse();

&open_read_hash();
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
	print "<center>\n";
	print &ui_form_start("inbox_login.cgi", "post");
	print &ui_hidden("folder", $folder->{'index'}),"\n";
	print &ui_table_start(
	      $folder->{'type'} == 2 ? $text{'mail_loginheader'}
				     : $text{'mail_loginheader2'}, undef, 2);
	print "<tr $cb> <td align=middle colspan=2>",&text('mail_logindesc',
			"<tt>$folder->{'server'}</tt>"),"</td> </tr>\n";

	print &ui_table_row($text{'mail_loginuser'},
			    &ui_textbox("user", $remote_user, 30));
	print &ui_table_row($text{'mail_loginpass'},
			    &ui_password("pass", $remote_pass, 30));

	#if ($folder->{'type'} == 4) {
	#	print "<tr> <td valign=top><b>$text{'mail_loginmailbox'}",
	#	      "</b></td> <td>\n";
	#	printf"<input type=radio name=mailbox_def value=1 %s> %s<br>\n",
	#		"checked", $text{'edit_imapinbox'};
	#	printf"<input type=radio name=mailbox_def value=0> %s\n",
	#		$text{'edit_imapother'};
	#	print "<input name=mailbox size=20></td> </tr>\n";
	#	}

	print &ui_table_end();
	print &ui_form_end([ [ "login", $text{'mail_login'} ] ]);
	print "</center>\n";

	&ui_print_footer("/", $text{'index'});
	exit;
	}

# Get folder-selection HTML
$sel = &folder_select(\@folders, $folder, "id", undef, 1);

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

print "<form action=delete_mail.cgi method=post>\n";
print "<input type=hidden name=folder value='$folder->{'index'}'>\n";
print "<input type=hidden name=mod value=",&modification_time($folder),">\n";
print "<input type=hidden name=start value='$in{'start'}'>\n";
if ($userconfig{'top_buttons'} && @mail) {
	&show_mailbox_buttons(1, \@folders, $folder, \@mail);
	@links = ( &select_all_link("d", 1),
		   &select_invert_link("d", 1) );
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
		push(@tds, $showto ? "nowrap width=15%"
				   : "nowrap width=30%");
		}
	if ($showto) {
		push(@cols, &field_sort_link($text{'mail_to'}, "to",
					     $folder, $in{'start'}));
		push(@tds, $showfrom ? "nowrap width=15%"
				     : "nowrap width=30%");
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

# Show the actual email
for($i=int($in{'start'}); $i<@mail && $i<$in{'start'}+$perpage; $i++) {
	local ($bs, $be);
	$m = $mail[$i];
	$mid = $m->{'header'}->{'message-id'};
	if ($read{$mid} == 2) {
		# Special
		($bs, $be) = ("<b><i>", "</i></b>");
		}
	elsif ($read{$mid} == 0) {
		# Unread
		($bs, $be) = ("<b>", "</b>");
		}
	&notes_decode($m, $folder);
	local $idx = $m->{'idx'};
	local @cols;

	# From and To columns, with links
	if ($showfrom) {
		push(@cols, $bs.&view_mail_link($folder, $i, $in{'start'},
				      $m->{'header'}->{'from'}, $mid).$be);
		}
	if ($showto) {
		push(@cols, $bs.&view_mail_link($folder, $i, $in{'start'},
		      $m->{'header'}->{'to'}, $mid).$be);
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
	local @icons = &message_icons($m, $folder->{'sent'});
	push(@cols, $bs.&simplify_subject($m->{'header'}->{'subject'}).
		    " ".join("&nbsp;", @icons).$be);

	if (&editable_mail($m)) {
		print &ui_checked_columns_row(\@cols, \@tds, "d", "$i/$mid");
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

&show_mailbox_buttons(2, \@folders, $folder, \@mail);
print "</form>\n";
if ($userconfig{'arrows'}) {
	# Show page flipping arrows
	print "<br>\n";
	&show_arrows();
	}

# Show search form
print "<hr>\n";
print "<table width=100%>\n";

if (@mail) {
	print "<tr>\n";
	if ($folder->{'searchable'}) {
		# Simple search
		print "<form action=mail_search.cgi><td width=33%>\n";
		print "<input type=hidden name=folder value='$folder->{'index'}'>\n";
		print "<input type=hidden name=simple value=1>\n";
		print "<input type=submit value='$text{'mail_search2'}'>\n";
		print "<input name=search size=20></td></form>\n";

		# Advanced search
		$jumpform = (@mail > $perpage);
		print "<form action=search_form.cgi>\n";
		print "<input type=hidden name=folder value='$folder->{'index'}'>\n";
		print "<td width=33% align=center><input type=submit name=advanced ",
		      "value='$text{'mail_advanced'}'></td>\n";
		print "</form>\n";
		}

	if ($folder->{'spam'}) {
		# Spam level search
		print "<form action=mail_search.cgi><td width=33% align=right>\n";
		print "<input type=hidden name=folder value='$folder->{'index'}'>\n";
		print "<input type=hidden name=spam value=1>\n";
		print "<input type=submit value='$text{'mail_search3'}'>\n";
		print "<input name=score size=5></td></form>\n";
		}
	elsif ($jumpform) {
		# Show page jump form
		print "<form action=index.cgi>\n";
		print "<input type=hidden name=folder value='$folder->{'index'}'>\n";
		print "<td width=33% align=right>\n";
		print "<input type=submit value='$text{'mail_jump'}'>\n";
		printf "<input name=jump size=3 value='%s'> %s %s\n",
			int($in{'start'} / $perpage)+1, $text{'mail_of'},
			int(@mail / $perpage)+1;
		print "</td></form>\n";
		}
	else {
		print "<td width=33% align=right></td>\n";
		}
	print "</tr>\n";
	}

# Show various buttons for the address book, folders, sig and searches
print "<tr>\n";

print "<form action=list_addresses.cgi>\n";
print "<td align=left width=33%><input type=submit value='$text{'mail_addresses'}'></td>\n";
print "</form>\n";

if ($config{'mail_system'} == 4) {
	print "<form action=list_ifolders.cgi>\n";
	}
else {
	print "<form action=list_folders.cgi>\n";
	}
print "<td align=",($bc == 2 ? "right" : "center"),
      " width=33%><input type=submit value='$text{'mail_folders'}'></td>\n";
print "</form>\n";

if (&get_signature_file()) {
	print "<form action=edit_sig.cgi>\n";
	print "<td width=33% align=right>",
	      "<input type=submit value='$text{'mail_sig'}'></td>\n";
	print "</form>\n";
	}
else {
	print "<td width=33% align=right></td>\n";
	}
print "</tr>\n";

print "<tr>\n";
if (@mail && ($folder->{'trash'} || $userconfig{'show_delall'})) {
	# Show button to delete all mail in folder
	print "<form action=delete_mail.cgi>\n";
	print "<input type=hidden name=folder value='$folder->{'index'}'>\n";
	print "<input type=hidden name=all value=1>\n";
	print "<td width=33%><input type=submit name=delete value='",
		($folder->{'trash'} ? $text{'mail_deltrash'}
				    : $text{'mail_delall'}),"'></td>\n";
	print "</form>\n";
	}
else {
	print "<td width=33%></td>\n";
	}

print "<td align=center width=33%></td>\n";

print "</tr>\n";

print "</table>\n";

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

