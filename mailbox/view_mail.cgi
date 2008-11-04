#!/usr/local/bin/perl
# view_mail.cgi
# View a single email message 

## kabe 2007/02/19:
##  fixed display of ISO-2022-JP encoded From: display 

require './mailbox-lib.pl';

&ReadParse();
foreach $a (&list_addresses()) {
	$inbook{lc($a->[0])}++;
	}

# Get the actual email being viewed, even if is a sub-message
@folders = &list_folders_sorted();
($folder) = grep { $_->{'index'} == $in{'folder'} } @folders;
$qid = &urlize($in{'id'});
$mail = &mailbox_get_mail($folder, $in{'id'}, 0);
$mail || &error($text{'view_egone'});
&notes_decode($mail, $folder);
&parse_mail($mail, undef, $in{'raw'});
@sub = split(/\0/, $in{'sub'});
$subs = join("", map { "&sub=$_" } @sub);
foreach $s (@sub) {
        # We are looking at a mail within a mail ..
	&decrypt_attachments($mail);
        local $amail = &extract_mail($mail->{'attach'}->[$s]->{'data'});
        &parse_mail($amail, undef, $in{'raw'});
        $mail = $amail;
        }

# Work out base URL for self links
$baseurl = "$gconfig{'webprefix'}/$module_name/view_mail.cgi?id=$qid&folder=$in{'folder'}&start=$in{'start'}$subs";

# Check if we can create email filters
$can_create_filter = 0;
if (&foreign_available("filter")) {
	&foreign_require("filter", "filter-lib.pl");
	$can_create_filter = !&filter::no_user_procmailrc();
	}

# Mark this mail as read
$mid = $mail->{'header'}->{'message-id'};
if ($userconfig{'auto_mark'}) {
	$wasread = &get_mail_read($folder, $mail);
	if (($wasread&1) == 0) {
		&set_mail_read($folder, $mail, $wasread+1);
		$refresh = 1;
		}
	}

# Possibly send a DSN, or check if one is needed
$dsn_req = &requires_delivery_notification($mail);
if (!@sub && $dsn_req && !$folder->{'sent'} && !$folder->{'drafts'}) {
	dbmopen(%dsn, "$user_module_config_directory/dsn", 0600);
	if ($userconfig{'send_dsn'} == 1 && !$dsn{$mid}) {
		# Send a DSN for this mail now
		local $dsnaddr = &send_delivery_notification($mail, undef, 0);
		if ($dsnaddr) {
			$dsn{$mid} = time()." ".$dsnaddr;
			$sent_dsn = 1;
			}
		}
	elsif ($userconfig{'send_dsn'} == 2 && !$dsn{$mid}) {
		# User may want to send one
		$send_dsn_button = 1;
		}
	($sent_dsn_at, $sent_dsn_to) = split(/\s+/, $dsn{$mid}, 2);
	dbmclose(%dsn);
	}

# Check if we have gotten back a DSN for *this* email
&update_delivery_notification($mail, $folder);
&open_dsn_hash();
if (defined($dsnreplies{$mid}) && $dsnreplies{$mid} != 1) {
	($got_dsn, $got_dsn_from) = split(/\s+/, $dsnreplies{$mid}, 2);
	}
if (defined($delreplies{$mid}) && $delreplies{$mid} != 1) {
	local @del = split(/\s+/, $delreplies{$mid});
	local $i;
	for($i=0; $i<@del; $i+=2) {
		local $tm = localtime($del[$i]);
		if ($del[$i+1] =~ /^\!(.*)$/) {
			push(@delmsgs, &text('view_delfailed', "$1", $tm));
			}
		else {
			push(@delmsgs, &text('view_delok', $del[$i+1], $tm));
			}
		}
	}

if ($in{'raw'}) {
	# Special mode - viewing whole raw message
	print "Content-type: text/plain\n\n";
	if ($mail->{'fromline'}) {
		print $mail->{'fromline'},"\n";
		}
	if (defined($mail->{'rawheaders'})) {
		#$mail->{'rawheaders'} =~ s/(\S)\t/$1\n\t/g;
		print $mail->{'rawheaders'};
		}
	else {
		foreach $h (@{$mail->{'headers'}}) {
			#$h->[1] =~ s/(\S)\t/$1\n\t/g;
			print "$h->[0]: $h->[1]\n";
			}
		}
	print "\n";
	print $mail->{'body'};
	exit;
	}

# Check for encryption
($deccode, $decmessage) = &decrypt_attachments($mail);
@attach = @{$mail->{'attach'}};

# Find body attachment and type
($textbody, $htmlbody, $body) = &find_body($mail, $userconfig{'view_html'});
$body = $htmlbody if ($in{'body'} == 2);
$body = $textbody if ($in{'body'} == 1);

# Show pre-body HTML
if ($body && $body eq $htmlbody && $userconfig{'head_html'}) {
	$headstuff = &head_html($body->{'data'});
	}

# Get the character set
if ($body) {
	$ctype = $body->{'header'}->{'content-type'} ||
		 $mail->{'header'}->{'content-type'};
	if ($ctype =~ /charset="([a-z0-9\-]+)"/i ||
	    $ctype =~ /charset='([a-z0-9\-]+)'/i ||
	    $ctype =~ /charset=([a-z0-9\-]+)/i) {
		$charset = $1;
		}
	}
## Special handling of HTML header charset ($force_charset):
## For japanese text(ISO-2022-JP/EUC=JP/SJIS), the HTML output and
## text contents ($bodycontents) are already converted to EUC,
## so overriding HTML charset to that in the mail header ($charset)
## is generally wrong. (cf. mailbox/boxes-lib.pl:eucconv())
if ( &get_charset() =~ /^EUC/i ) {	# EUC-JP,EUC-KR
	# use default charset output for HTML
} else {
	$force_charset = $charset;
}

&set_module_index($in{'folder'});
&mail_page_header($text{'view_title'}, $headstuff);
print &check_clicks_function();
&show_arrows();
print "<br>\n";

# Start of form
print &ui_form_start("reply_mail.cgi");
print &ui_hidden("id", $in{'id'}),"\n";
print &ui_hidden("folder", $in{'folder'}),"\n";
print &ui_hidden("mod", &modification_time($folder)),"\n";
print &ui_hidden("body", $in{'body'}),"\n";
print &ui_hidden("start", $in{'start'}),"\n";
foreach $s (@sub) {
	print &ui_hidden("sub", $s),"\n";
	}

# Find any delivery status attachment
($dstatus) = grep { $_->{'type'} eq 'message/delivery-status' } @attach;

# Check for signing
($sigcode, $sigmessage) = &check_signature_attachments(\@attach, $textbody);

if ($userconfig{'top_buttons'} == 2 && &editable_mail($mail)) {
	&show_buttons(1, scalar(@sub));
	print "<br>\n";
	}

# Start of headers section
@hmode = ( );
if ($in{'headers'}) {
	push(@hmode, "<a href='$baseurl&body=$in{'body'}&headers=0&images=$in{'images'}'>$text{'view_noheaders'}</a>");
	}
else {
	push(@hmode, "<a href='$baseurl&body=$in{'body'}&headers=1&images=$in{'images'}'>$text{'view_allheaders'}</a>");
	}
push(@hmode, "<a href='$baseurl&body=$in{'body'}&raw=1&images=$in{'images'}'>$text{'view_raw'}</a>");
print &ui_table_start($text{'view_headers'},
		      "width=100%", 2, [ "width=10% nowrap" ],
		      &ui_links_row(\@hmode));

if ($in{'headers'}) {
	# Show all the headers
	if ($mail->{'fromline'}) {
		print &ui_table_row($text{'mail_rfc'},
			&eucconv_and_escape($mail->{'fromline'}));
		}
	foreach $h (@{$mail->{'headers'}}) {
		print &ui_table_row("$h->[0]:",
			&eucconv_and_escape(&decode_mimewords($h->[1])));
		}
	}
else {
	# Just show the most useful headers
	local @addrs = &split_addresses(&decode_mimewords(
				$mail->{'header'}->{'from'}));
	local @toaddrs = &split_addresses(&decode_mimewords(
				$mail->{'header'}->{'to'}));
	print &ui_table_row($text{'mail_from'},
		&left_right_align(&address_link($mail->{'header'}->{'from'}),
			  &search_link("from", $text{'mail_fromsrch'},
				       $addrs[0]->[0], $addrs[0]->[1]).
			  &filter_link("From", $text{'mail_fromfilter'},
				       $addrs[0]->[0])));
	print &ui_table_row($text{'mail_to'},
		&left_right_align(&address_link($mail->{'header'}->{'to'}),
			  &search_link("to", $text{'mail_tosrch'},
				       $toaddrs[0]->[0], $toaddrs[0]->[1]).
			  &filter_link("To", $text{'mail_tofilter'},
				       $toaddrs[0]->[0])));
	if ($mail->{'header'}->{'cc'}) {
		print &ui_table_row($text{'mail_cc'},
			&address_link($mail->{'header'}->{'cc'}));
		}
	if ($mail->{'header'}->{'bcc'}) {
		print &ui_table_row($text{'mail_bcc'},
			&address_link($mail->{'header'}->{'bcc'}));
		}
	print &ui_table_row($text{'mail_date'},
		&eucconv_and_escape(
			&simplify_date($mail->{'header'}->{'date'})));

	local $subj = $mail->{'header'}->{'subject'};
	$subj =~ s/^((Re:|Fwd:|\[\S+\])\s*)+//g;
	print &ui_table_row($text{'mail_subject'},
		&left_right_align(&eucconv_and_escape(&decode_mimewords(
				  $mail->{'header'}->{'subject'})),
			  &search_link("subject", $text{'mail_subsrch'},
				       $subj).
			  &filter_link("Subject", $text{'mail_subfilter'},
				       $subj)));
	}
print &ui_table_end();

# Show body attachment, with properly linked URLs
$image_mode = defined($in{'images'}) ? $in{'images'}
				     : $userconfig{'view_images'};
@bodyright = ( );
if ($body && $body->{'data'} =~ /\S/) {
	if ($body eq $textbody) {
		# Show plain text
		$bodycontents = "<pre>";
		foreach $l (&wrap_lines(&eucconv($body->{'data'}),
					$userconfig{'wrap_width'})) {
			$bodycontents .= &link_urls_and_escape($l,
						$userconfig{'link_mode'})."\n";
			}
		$bodycontents .= "</pre>";
		if ($htmlbody) {
			# Link to show HTML
			push(@bodyright, "<a href='$baseurl&body=2&headers=$in{'headers'}'>$text{'view_ashtml'}</a>");
			}
		}
	elsif ($body eq $htmlbody) {
		# Attempt to show HTML
		($bodycontents, $bodystuff) = &safe_html($body->{'data'});
		@imagesurls = ( );
		$bodycontents = &disable_html_images($bodycontents, $image_mode,
						     \@imageurls);
		$bodycontents = &fix_cids($bodycontents, \@attach,
			"detach.cgi?id=$qid&folder=$in{'folder'}$subs");
		if ($textbody) {
			# Link to show text
			push(@bodyright, "<a href='$baseurl&body=1&headers=$in{'headers'}&images=$in{'images'}'>$text{'view_astext'}</a>");
			}
		if (@imageurls && $image_mode) {
			# Link to show images
			push(@bodyright, "<a href='$baseurl&body=$in{'body'}&headers=$in{'headers'}&images=0'>$text{'view_images'}</a>");
			}
		}
	}
if ($bodycontents) {
	print &ui_table_start($text{'view_body'}, "width=100%", 1,
			      undef, &ui_links_row(\@bodyright));
	print &ui_table_row(undef, $bodycontents, undef, [ undef, $bodystuff ]);
	print &ui_table_end();
	}

# If *this* message is a delivery status, display it
if ($dstatus) {
	&show_delivery_status($dstatus);
	}

# Display other attachments
@attach = &remove_body_attachments($mail, \@attach);
@attach = &remove_cid_attachments($mail, \@attach);
if (@attach) {
	# Table of attachments
	$viewurl = "view_mail.cgi?id=".&urlize($in{'id'}).
		   "&folder=$folder->{'index'}$subs";
	$detachurl = "detach.cgi?id=".&urlize($in{'id'}).
		     "&folder=$folder->{'index'}$subs";
	@detach = &attachments_table(\@attach, $folder, $viewurl, $detachurl,
				     undef, undef, undef);

	# Links to download all / slideshow
	@links = ( );
	if (@attach > 1 && &can_download_all()) {
		push(@links, "<a href='detachall.cgi/attachments.zip?folder=$in{'folder'}&id=$qid$subs'>$text{'view_aall'}</a>");
		}
	@iattach = grep { $_->{'type'} =~ /^image\// } @attach;
	if (@iattach > 1) {
		push(@links, "<a href='slideshow.cgi?folder=$in{'folder'}&id=$qid$subs'>$text{'view_aslideshow'}</a>");
		}
	print &ui_links_row(\@links) if (@links);

	# Show form to detact to server, if enabled
	if ($config{'server_attach'} == 2 && @detach) {
		print &ui_table_start($text{'view_dheader'}, "width=100%", 1);
		$dtach = &ui_submit($text{'view_detach'}, 'detach');
		$dtach .= &ui_hidden("bindex", $body->{'idx'}) if ($body);
		$dtach .= &ui_hidden("sindex", $sindex) if (defined($sindex));
		$dtach .= &ui_select("attach", undef,
				[ [ '*', $text{'view_dall'} ],
				  @detach ]);
		$dtach .= "<b>$text{'view_dir'}</b>\n";
		$dtach .= &ui_textbox("dir", undef, 60)." ".
			  &file_chooser_button("dir", 1);
		print &ui_table_row(undef, $dtach);
		print &ui_table_end();
		}
	}

# Display GnuPG results
if (defined($sigcode)) {
	print &ui_table_start($text{'view_gnupg'}, "width=100%", 1);
	$sigmessage = &html_escape($sigmessage);
	$sigmessage = $sigmessage if ($sigcode == 4);
	print &ui_table_row(undef, &text('view_gnupg_'.$sigcode, $sigmessage));
	if ($sigcode == 3) {
		print &ui_table_row(undef,
			&text('view_recv', $sigmessage, "/gnupg/recv.cgi?id=$sigmessage&return=".&urlize($baseurl)."&returnmsg=".&urlize($text{'view_return'})));
		}
	print &ui_table_end();
	}
if ($deccode) {
	print &ui_table_start($text{'view_crypt'}, "width=100%", 1);
	print &ui_table_row(undef,
		&text('view_crypt_'.$deccode, "<pre>$decmessage</pre>"));
	print &ui_table_end();
	}

# Display DSN status
if ($sent_dsn_to || $send_dsn_button || $got_dsn || @delmsgs) {
	print &ui_table_start($text{'view_dsn'}, "width=100%", 1);
	if ($sent_dsn_to) {
		print &ui_table_row(undef,
		      &text($sent_dsn ? 'view_dnsnow' : 'view_dsnbefore',
			    &html_escape($sent_dsn_to),
			    ($dsntm = localtime($sent_dsn_at))));
		}
	elsif ($send_dsn_button) {
		print &ui_table_row(undef,
			&text('view_dsnreq', &html_escape($dsn_req))."<br>".
			&ui_submit($text{'view_dsnsend'}, "dsn"));
		}
	elsif ($got_dsn) {
		print &ui_table_row(undef,
			&text('view_dsngot', &html_escape($got_dsn_from),
			     ($dsntm = localtime($got_dsn))));
		}
	elsif (@delmsgs) {
		print &ui_table_row(undef,
			join("<br>\n", @delmsgs));
		}
	print &ui_table_end();
	}

if (!$folder->{'sent'} && !$folder->{'drafts'}) {
	# Show quick reply form
	print &ui_hidden_table_start($text{'view_quick'}, "width=100%", 1,
				     "quick", 0);
	$wcols = $userconfig{'wrap_compose'};
	print &ui_table_row(undef,
		&ui_textarea("quick", undef, 5, $wcols || 80,
			     $wcols ? "hard" : "",
			     0, $wcols ? "" : "style='width:100%'"), 2);
	print &ui_table_row(undef,
		&ui_submit($text{'view_quick_send'}, "quick_send")." ".
		&ui_checkbox("quick_all", 1, $text{'view_quick_all'}, 0)." ".
		&ui_checkbox("quick_quote", 1, $text{'view_quick_quote'}, 1),2);
	print &ui_hidden_table_end();
	}

&show_buttons(2, scalar(@sub)) if (&editable_mail($mail));
if ($userconfig{'arrows'} == 2 && !@sub) {
	print "<br>\n";
	&show_arrows();
	}
print "</form>\n";

if ($refresh) {
	# Refresh left frame if we have changed the read status
	if (defined(&theme_post_save_folder)) {
		&theme_post_save_folder($folder, 'read');
		}
	}

# Show footer links
local @sr = !@sub ? ( ) :
    ( "view_mail.cgi?id=$qid&folder=$in{'folder'}", $text{'view_return'} ),
&mail_page_footer(@sub ? ( "view_mail.cgi?id=$qid&folder=$in{'folder'}",
		 $text{'view_return'} ) : ( ),
	"index.cgi?folder=$in{'folder'}&start=$in{'start'}",
	$text{'mail_return'});

&pop3_logout_all();

# show_buttons(pos, submode)
sub show_buttons
{
local $spacer = "&nbsp;\n";
if ($folder->{'sent'} || $folder->{'drafts'}) {
	print &ui_submit($text{'view_enew'}, "enew");
	print &ui_submit($text{'view_reply'}, "ereply");
	print &ui_submit($text{'view_reply2'}, "erall");
	}
else {
	print &ui_submit($text{'view_reply'}, "reply");
	print &ui_submit($text{'view_reply2'}, "rall");
	}
print $spacer;

if ($userconfig{'open_mode'}) {
	# Compose button needs to pop up a window
	print &ui_submit($text{'mail_compose'}, "new", undef,
	      "onClick='window.open(\"reply_mail.cgi?new=1\", \"compose\", \"toolbar=no,menubar=no,scrollbars=yes,width=1024,height=768\"); return false'>");
	}
else {
	# Compose button can just submit and redirect
	print &ui_submit($text{'mail_compose'}, "new");
	}
print $spacer;

print &ui_submit($text{'view_forward'}, "forward");
print $spacer;

if (!$_[1]) {
	# Show mark buttons, except for current mode
	if (!$folder->{'sent'} && !$folder->{'drafts'}) {
		$m = &get_mail_read($folder, $mail);
		foreach $i (0 .. 2) {
			if ($m != $i) {
				print &ui_submit($text{'view_markas'.$i},
						 "markas".$i);
				}
			}
		print $spacer;
		}

	if (@folders > 1) {
		print &movecopy_select($_[0], \@folders, $folder);
		print $spacer;
		}

	print &ui_submit($text{'view_delete'}, "delete");
	print $spacer;
	}
else {
	if (@folders > 1) {
		print &movecopy_select($_[0], \@folders, $folder, 1);
		print $spacer;
		}
	}
print &ui_submit($text{'view_print'}, "print", undef,
	"onClick='window.open(\"reply_mail.cgi?print=1&id=".&urlize($in{'id'}).
	"&folder=".&urlize($in{'folder'}).
	"&print=1\", \"print\"); return false'");
print $spacer;

if (!$_[1]) {
	# Show spam and/or ham report buttons
	if (&can_report_spam($folder) &&
	    $userconfig{'spam_buttons'} =~ /mail/) {
		print &ui_submit($text{'view_black'}, "black");
		if ($userconfig{'spam_del'}) {
			print &ui_submit($text{'view_razordel'}, "razor");
			}
		else {
			print &ui_submit($text{'view_razor'}, "razor");
			}
		print $spacer;
		}
	if (&can_report_ham($folder) &&
	    $userconfig{'ham_buttons'} =~ /mail/) {
		if ($userconfig{'white_move'} && $folder->{'spam'}) {
			print &ui_submit($text{'view_whitemove'}, "white");
			}
		else {
			print &ui_submit($text{'view_white'}, "white");
			}
		if ($userconfig{'ham_move'} && $folder->{'spam'}) {
			print &ui_submit($text{'view_hammove'}, "ham");
			}
		else {
			print &ui_submit($text{'view_ham'}, "ham");
			}
		print $spacer;
		}
	}
print "<br>\n";
}

sub show_arrows
{
print "<center>\n";
if (!@sub) {
	# Get next and previous emails, where they exist
	local $c = &mailbox_folder_size($folder, 1);
	local $prv = $mail->{'sortidx'} == 0 ? 0 : $mail->{'sortidx'}-1;
	local $nxt = $mail->{'sortidx'} == $c-1 ? $c-1 : $mail->{'sortidx'}+1;
	local @beside = &mailbox_list_mails_sorted($prv, $nxt, $folder, 1);

	if ($mail->{'sortidx'} != 0) {
		local $mailprv = $beside[$prv];
		print "<a href='view_mail.cgi?id=",&urlize($mailprv->{'id'}),
		      "&folder=$in{'folder'}&start=$in{'start'}'>",
		      "<img src=../images/left.gif border=0 ",
		      "align=middle></a>\n";
		}
	else {
		print "<img src=../images/left-grey.gif align=middle>\n";
		}
	print "<font size=+1>",&text('view_desc', $mail->{'sortidx'}+1,
			$folder->{'name'}),"</font>\n";
	if ($mail->{'sortidx'} < $c-1) {
		local $mailnxt = $beside[$nxt];
		print "<a href='view_mail.cgi?id=",&urlize($mailnxt->{'id'}),
		      "&folder=$in{'folder'}&start=$in{'start'}'>",
		      "<img src=../images/right.gif border=0 ",
		      "align=middle></a>\n";
		}
	else {
		print "<img src=../images/right-grey.gif align=middle>\n";
		}
	}
else {
	print "<font size=+1>$text{'view_sub'}</font>\n";
	}
print "</center>\n";
}

# search_link(field, text, what, ...)
# Returns HTML for a link to search for mails with the same sender or subject
sub search_link
{
local ($field, $text, @what) = @_;
local $fid;
if ($userconfig{'related_search'}) {
	# Search is across all folders
	$fid = -$userconfig{'related_search'};
	}
elsif (!$folder->{'searchable'}) {
	# Search is source folder
	if ($mail->{'subfolder'}) {
		$fid = $mail->{'subfolder'}->{'index'};
		}
	else {
		return undef;
		}
	}
else {
	# Search is in this folder
	$fid = $in{'folder'};
	}
if ($_[1]) {
	local $qtext = &quote_escape($text);
	local $whats;
	local $fields;
	local $i = 0;
	foreach my $w (@what) {
		if ($w) {
			$fields .= "&field_".$i."=".&urlize($field);
			$whats .= "&what_".$i."=".&urlize($w);
			$i++;
			}
		}
	return "<a href='mail_search.cgi?folder=".$fid."&and=0".
	       $fields.$whats.
	       "'><img src=images/search.gif ".
	       "alt='$qtext' title='$qtext' border=0></a>";
	}
else {
	return undef;
	}
}

# filter_link(field, text, value)
# Returns HTML for creating an email filter matching some field, if possible
sub filter_link
{
local ($field, $text, $what) = @_;
return undef if (!$can_create_filter);
local $qtext = &quote_escape($text);
return "<a href='../filter/edit.cgi?new=1&header=".&urlize($field).
       "&value=".&urlize($what)."'><img src=images/filter.gif ".
       "alt='$qtext' title='$qtext' border=0></a>";
}

