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

# Mark this mail as read
&open_read_hash();
$mid = $mail->{'header'}->{'message-id'};
if ($userconfig{'auto_mark'}) {
	eval { $read{$mid} = 1 } if (!$read{$mid});
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

# XXX look for text/calendar body

# Check for signing
if (&has_command("gpg") && &foreign_check("gnupg")) {
	# Check for GnuPG signatures
	local $sig;
	foreach $a (@attach) {
		$sig = $a if ($a->{'type'} =~ /^application\/pgp-signature/);
		}
	if ($sig) {
		# Verify the signature against the rest of the attachment
		&foreign_require("gnupg", "gnupg-lib.pl");
		local $rest = $sig->{'parent'}->{'attach'}->[0];
		$rest->{'raw'} =~ s/\r//g;
		$rest->{'raw'} =~ s/\n/\r\n/g;
		($sigcode, $sigmessage) = &foreign_call("gnupg",
				"verify_data", $rest->{'raw'}, $sig->{'data'});
		@attach = grep { $_ ne $sig } @attach;
		$sindex = $sig->{'idx'};
		}
	elsif ($textbody && $textbody->{'data'} =~ /(-+BEGIN PGP SIGNED MESSAGE-+\n(Hash:\s+(\S+)\n\n)?([\000-\377]+\n)-+BEGIN PGP SIGNATURE-+\n([\000-\377]+)-+END PGP SIGNATURE-+\n)/i) {
		# Signature is in body text!
		local $sig = $1;
		local $text = $4;
		&foreign_require("gnupg", "gnupg-lib.pl");
		($sigcode, $sigmessage) = &foreign_call("gnupg",
							"verify_data", $sig);
		$body = $textbody;
		if ($sigcode == 0 || $sigcode == 1) {
			# XXX what about replying?
			$body->{'data'} = $text;
			}
		}
	}

# Strip out attachments not to display as icons
@attach = grep { $_ ne $body && $_ ne $dstatus } @attach;
@attach = grep { !$_->{'attach'} } @attach;

if ($userconfig{'top_buttons'} == 2 && &editable_mail($mail)) {
	&show_buttons(1, scalar(@sub));
	print "<br>\n";
	}

# Start of headers section
if ($in{'headers'}) {
	$hmode = "<a href='view_mail.cgi?id=$qid&body=$in{'body'}&headers=0&folder=$in{'folder'}&start=$in{'start'}$subs'>$text{'view_noheaders'}</a>\n";
	}
else {
	$hmode = "<a href='view_mail.cgi?id=$qid&body=$in{'body'}&headers=1&folder=$in{'folder'}&start=$in{'start'}$subs'>$text{'view_allheaders'}</a>\n";
	}
$hmode .= "&nbsp;&nbsp;<a href='view_mail.cgi?id=$qid&raw=1&folder=$in{'folder'}&start=$in{'start'}$subs'>$text{'view_raw'}</a>";
print &ui_table_start(&left_right_align("<b>$text{'view_headers'}</b>", $hmode),
		      "width=100%", 2, [ "width=10% nowrap" ]);

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
				  &search_link("from", $addrs[0]->[0],
					       $text{'mail_fromsrch'})));
	print &ui_table_row($text{'mail_to'},
		&left_right_align(&address_link($mail->{'header'}->{'to'}),
				  &search_link("to", $toaddrs[0]->[0],
					       $text{'mail_tosrch'})));
	if ($mail->{'header'}->{'cc'}) {
		print &ui_table_row($text{'mail_cc'},
			&address_link($mail->{'header'}->{'cc'}));
		}
	if ($mail->{'header'}->{'bcc'}) {
		print &ui_table_row($text{'mail_bcc'},
			&address_link($mail->{'header'}->{'bcc'}));
		}
	print &ui_table_row($text{'mail_date'},
		&eucconv_and_escape($mail->{'header'}->{'date'}));

	local $subj = $mail->{'header'}->{'subject'};
	$subj =~ s/^((Re:|Fwd:|\[\S+\])\s*)+//g;
	print &ui_table_row($text{'mail_subject'},
		&left_right_align(&eucconv_and_escape(&decode_mimewords(
					$mail->{'header'}->{'subject'})),
				  &search_link("subject", $subj,
					       $text{'mail_subsrch'})));
	}
print &ui_table_end();

# Show body attachment, with properly linked URLs
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
			$bodyright = "<a href='view_mail.cgi?id=$qid&body=2&headers=$in{'headers'}&folder=$in{'folder'}&start=$in{'start'}$subs'>$text{'view_ashtml'}</a>";
			}
		}
	elsif ($body eq $htmlbody) {
		# Attempt to show HTML
		($bodycontents, $bodystuff) = &safe_html($body->{'data'});
		$bodycontents = &fix_cids($bodycontents, \@attach,
			"detach.cgi?id=$qid&folder=$in{'folder'}$subs",
			\@cidattach);
		if ($textbody) {
			$bodyright = "<a href='view_mail.cgi?id=$qid&body=1&headers=$in{'headers'}&folder=$in{'folder'}&start=$in{'start'}$subs'>$text{'view_astext'}</a>";
			}
		%ciddone = map { $_->{'index'}, 1 } @cidattach;
		@attach = grep { !$ciddone{$_->{'index'}} } @attach;
		}
	}
if ($bodycontents) {
	print &ui_table_start(
		&left_right_align("<b>$text{'view_body'}</b>", $bodyright),
		"width=100%", 1);
	print &ui_table_row(undef, $bodycontents, undef, [ undef, $bodystuff ]);
	print &ui_table_end();
	}

# If *this* message is a delivery status, display it
if ($dstatus) {
	local $ds = &parse_delivery_status($dstatus->{'data'});
	$dtxt = $ds->{'status'} =~ /^2\./ ? $text{'view_dstatusok'}
					  : $text{'view_dstatus'};
	print &ui_table_start($dtxt, "width=100%", 2, [ "width=10% nowrap" ]);

	foreach $dsh ('final-recipient', 'diagnostic-code',
		      'remote-mta', 'reporting-mta') {
		if ($ds->{$dsh}) {
			$ds->{$dsh} =~ s/^\S+;//;
			print &ui_table_row($text{'view_'.$dsh},
					    &html_escape($ds->{$dsh}));
			}
		}
	print &ui_table_end();
	}

# Display other attachments
if (@attach) {
	foreach $a (@attach) {
		local $fn;
		$size = &nice_size(length($a->{'data'}));
		local $cb;
		if ($a->{'type'} eq 'message/rfc822') {
			push(@files, $text{'view_sub'});
			}
		elsif ($a->{'filename'}) {
			# Known filename
			push(@files, &decode_mimewords($a->{'filename'}));
			$fn = &decode_mimewords($a->{'filename'});
			push(@detach, [ $a->{'idx'}, $fn ]);
			}
		else {
			# No filename
			push(@files, "<i>$text{'view_anofile'}</i>");
			$a->{'type'} =~ /\/(\S+)$/;
			$fn = "file.$1";
			push(@detach, [ $a->{'idx'}, $fn ]);
			}
		push(@sizes, $size);
		push(@titles, $files[$#files]."<br>".$size);
		if ($a->{'error'}) {
			$titles[$#titles] .= "<br><font size=-1>($a->{'error'})</font>";
			}
		$fn =~ s/ /_/g;
		$fn =~ s/\#/_/g;
		$fn = &html_escape($fn);
		if ($a->{'type'} eq 'message/rfc822') {
			push(@links, "view_mail.cgi?id=$qid&folder=$in{'folder'}$subs&sub=$a->{'idx'}");
			}
		else {
			push(@links, "detach.cgi/$fn?id=$qid&folder=$in{'folder'}&attach=$a->{'idx'}$subs");
			}
		if ($userconfig{'thumbnails'} &&
		    ($a->{'type'} =~ /image\/gif/i && &has_command("giftopnm")&&
		     &has_command("pnmscale") && &has_command("cjpeg") ||
		     $a->{'type'} =~ /image\/jpeg/i && &has_command("djpeg") &&
		     &has_command("pnmscale") && &has_command("cjpeg"))) {
			# Can show an image icon
			push(@icons, "detach.cgi?scale=1&id=$qid&folder=$in{'folder'}&attach=$a->{'idx'}$subs");
			$imgicons++;
			}
		else {
			push(@icons, "images/boxes.gif");
			}
		}
	print &ui_columns_start([
		$text{'view_afile'},
		$text{'view_atype'},
		$text{'view_asize'},
		], 100, 0, [ "width=60%", "width=25%", "width=15%" ]);
	for(my $i=0; $i<@files; $i++) {
		print &ui_columns_row([
			"<a href='$links[$i]'>$files[$i]</a>",
			$attach[$i]->{'type'},
			$sizes[$i],
			]);
		}
	print &ui_columns_end();

	# Show form to detact to server
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
		local $url = "/$module_name/view_mail.cgi?id=$qid&folder=$in{'folder'}$subs";
		print &ui_table_row(undef,
			&text('view_recv', $sigmessage, "/gnupg/recv.cgi?id=$sigmessage&return=".&urlize($url)."&returnmsg=".&urlize($text{'view_return'})));
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

&show_buttons(2, scalar(@sub)) if (&editable_mail($mail));
if ($userconfig{'arrows'} == 2 && !@sub) {
	print "<br>\n";
	&show_arrows();
	}
print "</form>\n";

dbmclose(%read);

# Show footer links
local @sr = !@sub ? ( ) :
    ( "view_mail.cgi?id=$qid&folder=$in{'folder'}", $text{'view_return'} ),
&mail_page_footer(@sub ? ( "view_mail.cgi?idx=$qid&folder=$in{'folder'}",
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
print &ui_submit($text{'view_print'}, "print");
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
		pritn &ui_submit($text{'view_white'}, "white");
		pritn &ui_submit($text{'view_ham'}, "ham");
		print $spacer;
		}
	}
print "<br>\n";
}

# address_link(address)
sub address_link
{
## split_addresses() pattern-matches "[<>]", so 7-bit encodings
## such as ISO-2022-JP must be converted to EUC before feeding.
local @addrs = &split_addresses(&eucconv(&decode_mimewords($_[0])));
local @rv;
foreach $a (@addrs) {
	## TODO: is $inbook{} MIME or locale-encoded?
	if ($inbook{lc($a->[0])}) {
		push(@rv, &eucconv_and_escape($a->[2]));
		}
	else {
		## name= will be EUC encoded now since split_addresses()
		## is feeded with EUC converted value.
		push(@rv, "<a href='add_address.cgi?addr=".&urlize($a->[0]).
			  "&name=".&urlize($a->[1])."&id=$qid".
			  "&folder=$in{'folder'}&start=$in{'start'}$subs'>".
			  &eucconv_and_escape($a->[2])."</a>");
		}
	}
return join(" , ", @rv);
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

# search_link(field, what, text)
sub search_link
{
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
	return "<a href='mail_search.cgi?field_0=".&urlize($_[0]).
	       "&what_0=".&urlize($_[1]).
	       "&folder=".$fid."'>$_[2]</a>";
	}
else {
	return undef;
	}
}

