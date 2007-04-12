#!/usr/local/bin/perl
# view_mail.cgi
# View a single email message 

## kabe 2007/02/19:
##  fixed display of ISO-2022-JP encoded From: display 

require './mailbox-lib.pl';

&ReadParse();
foreach $a (&list_addresses()) {
	$inbook{$a->[0]}++;
	}

@folders = &list_folders_sorted();
($folder) = grep { $_->{'index'} == $in{'folder'} } @folders;
$qmid = &urlize($in{'mid'});
if ($in{'idx'} =~ /^(\d+)\/(.*)$/) {
	# Fix links where idx contains index and message ID (when in open_mode)
	$in{'idx'} = $1;
	$in{'mid'} = $2;
	}
@mail = &mailbox_list_mails_sorted($in{'idx'}, $in{'idx'}, $folder,
				   0, undef);
$mail = &find_message_by_index(\@mail, $folder, $in{'idx'}, $in{'mid'});
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

print "<form action=reply_mail.cgi>\n";
print &ui_hidden("idx", $in{'idx'}),"\n";
print &ui_hidden("mid", $in{'mid'}),"\n";
print &ui_hidden("folder", $in{'folder'}),"\n";
print &ui_hidden("mod", &modification_time($folder)),"\n";
print &ui_hidden("body", $in{'body'}),"\n";
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
	print "<p>\n";
	}

print "<table width=100% border=1>\n";
print "<tr> <td><table width=100% cellpadding=0 cellspacing=0><tr $tb>",
      "<td><b>$text{'view_headers'}</b></td> <td align=right>\n";
if ($in{'headers'}) {
	print "<a href='view_mail.cgi?idx=$in{'idx'}&mid=$qmid&body=$in{'body'}&headers=0&folder=$in{'folder'}$subs'>$text{'view_noheaders'}</a>\n";
	}
else {
	print "<a href='view_mail.cgi?idx=$in{'idx'}&mid=$qmid&body=$in{'body'}&headers=1&folder=$in{'folder'}$subs'>$text{'view_allheaders'}</a>\n";
	}
print "&nbsp;&nbsp;<a href='view_mail.cgi?idx=$in{'idx'}&mid=$qmid&raw=1&folder=$in{'folder'}$subs'>$text{'view_raw'}</a></td>\n";
print "</tr></table></td> </tr>\n";

print "<tr $cb> <td><table width=100%>\n";
if ($in{'headers'}) {
	# Show all the headers
	if ($mail->{'fromline'}) {
		print "<tr> <td><b>$text{'mail_rfc'}</b></td>",
		      "<td>",&eucconv_and_escape($mail->{'fromline'}),
		      "</td> </tr>\n";
		}
	foreach $h (@{$mail->{'headers'}}) {
		print "<tr> <td><b>$h->[0]:</b></td> ",
		      "<td>",&eucconv_and_escape(&decode_mimewords($h->[1])),
		      "</td> </tr>\n";
		}
	}
else {
	# Just show the most useful headers
	local @addrs = &split_addresses(&decode_mimewords(
				$mail->{'header'}->{'from'}));
	local @toaddrs = &split_addresses(&decode_mimewords(
				$mail->{'header'}->{'to'}));
	print "<tr> <td valign=top><b>$text{'mail_from'}</b></td> ",
	      "<td>",&address_link($mail->{'header'}->{'from'}),"</td>",
	      "<td align=right>",&search_link("from", $addrs[0]->[0],
			$text{'mail_fromsrch'}),"</td> </tr>\n";
	print "<tr> <td valign=top><b>$text{'mail_to'}</b></td> ",
	      "<td>",&address_link($mail->{'header'}->{'to'}),"</td>",
	      "<td align=right>",&search_link("to", $toaddrs[0]->[0],
			$text{'mail_tosrch'}),"</td> </tr>\n";
	print "<tr> <td valign=top><b>$text{'mail_cc'}</b></td> ",
	      "<td>",&address_link($mail->{'header'}->{'cc'}),"</td> </tr>\n"
		if ($mail->{'header'}->{'cc'});
	print "<tr> <td valign=top><b>$text{'mail_bcc'}</b></td> ",
	      "<td>",&address_link($mail->{'header'}->{'bcc'}),"</td> </tr>\n"
		if ($mail->{'header'}->{'bcc'});
	print "<tr> <td><b>$text{'mail_date'}</b></td> ",
	      "<td>",&eucconv_and_escape($mail->{'header'}->{'date'}),
	      "</td> </tr>\n";
	local $subj = $mail->{'header'}->{'subject'};
	$subj =~ s/^((Re:|Fwd:|\[\S+\])\s*)+//g;
	print "<tr> <td><b>$text{'mail_subject'}</b></td> ",
	      "<td>",&eucconv_and_escape(&decode_mimewords(
			$mail->{'header'}->{'subject'})),"</td> ",
	      "<td align=right>",&search_link("subject", $subj,
			$text{'mail_subsrch'}),"</td> </tr>\n";
	}
print "</table></td></tr></table><p>\n";

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
			$bodyright = "<a href='view_mail.cgi?idx=$in{'idx'}&mid=$qmid&body=2&headers=$in{'headers'}&folder=$in{'folder'}$subs'>$text{'view_ashtml'}</a>";
			}
		}
	elsif ($body eq $htmlbody) {
		# Attempt to show HTML
		($bodycontents, $bodystuff) = &safe_html($body->{'data'});
		$bodycontents = &fix_cids($bodycontents, \@attach,
			"detach.cgi?idx=$in{'idx'}&folder=$in{'folder'}$subs",
			\@cidattach);
		if ($textbody) {
			$bodyright = "<a href='view_mail.cgi?idx=$in{'idx'}&mid=$qmid&body=1&headers=$in{'headers'}&folder=$in{'folder'}$subs'>$text{'view_astext'}</a>";
			}
		%ciddone = map { $_->{'index'}, 1 } @cidattach;
		@attach = grep { !$ciddone{$_->{'index'}} } @attach;
		}
	}
if ($bodycontents) {
	print "<table width=100% border=1>\n";
	print "<tr $tb> <td><table width=100% cellpadding=0 cellspacing=0><tr>",
	      "<td><b>$text{'view_body'}</b></td> ",
	      "<td align=right>$bodyright</td> </tr></table></td> </tr>\n";
	print "<tr $cb> <td $bodystuff>\n";
	print $bodycontents;
	print "</td></tr></table><p>\n";
	}

# If *this* message is a delivery status, display it
if ($dstatus) {
	local $ds = &parse_delivery_status($dstatus->{'data'});
	$dtxt = $ds->{'status'} =~ /^2\./ ? $text{'view_dstatusok'}
					  : $text{'view_dstatus'};
	print "<table width=100% border=1>\n";
	print "<tr $tb> <td><b>$dtxt</b></td> </tr>\n";
	print "<tr $cb> <td><table>\n";

	foreach $dsh ('final-recipient', 'diagnostic-code',
		      'remote-mta', 'reporting-mta') {
		if ($ds->{$dsh}) {
			$ds->{$dsh} =~ s/^\S+;//;
			print "<tr> <td nowrap valign=top><b>",
			      $text{'view_'.$dsh},"</b></td>\n";
			print "<td>",&html_escape($ds->{$dsh}),"</td> </tr>\n";
			}
		}

	print "</table></td></tr></table><p>\n";
	}

# Display other attachments
if (@attach) {
	print "<table width=100% border=1>\n";
	print "<tr $tb> <td><b>$text{'view_attach'}</b></td> </tr>\n";
	print "<tr $cb> <td>\n";
	foreach $a (@attach) {
		local $fn;
		$size = (int(length($a->{'data'})/1000)+1)." Kb";
		local $cb;
		if ($a->{'type'} eq 'message/rfc822') {
			push(@titles, "$text{'view_sub'}<br>$size");
			}
		elsif ($a->{'filename'}) {
			push(@titles, &decode_mimewords($a->{'filename'}).
				      "<br>$size");
			$fn = &decode_mimewords($a->{'filename'});
			push(@detach, [ $a->{'idx'}, $fn ]);
			}
		else {
			push(@titles, "$a->{'type'}<br>$size");
			$a->{'type'} =~ /\/(\S+)$/;
			$fn = "file.$1";
			push(@detach, [ $a->{'idx'}, $fn ]);
			}
		if ($a->{'error'}) {
			$titles[$#titles] .= "<br><font size=-1>($a->{'error'})</font>";
			}
		$fn =~ s/ /_/g;
		$fn =~ s/\#/_/g;
		$fn = &html_escape($fn);
		if ($a->{'type'} eq 'message/rfc822') {
			push(@links, "view_mail.cgi?idx=$in{'idx'}&mid=$qmid&folder=$in{'folder'}$subs&sub=$a->{'idx'}");
			}
		else {
			push(@links, "detach.cgi/$fn?idx=$in{'idx'}&mid=$qmid&folder=$in{'folder'}&attach=$a->{'idx'}$subs");
			}
		if ($userconfig{'thumbnails'} &&
		    ($a->{'type'} =~ /image\/gif/i && &has_command("giftopnm")&&
		     &has_command("pnmscale") && &has_command("cjpeg") ||
		     $a->{'type'} =~ /image\/jpeg/i && &has_command("djpeg") &&
		     &has_command("pnmscale") && &has_command("cjpeg"))) {
			# Can show an image icon
			push(@icons, "detach.cgi?scale=1&idx=$in{'idx'}&folder=$in{'folder'}&attach=$a->{'idx'}$subs");
			$imgicons++;
			}
		else {
			push(@icons, "images/boxes.gif");
			}
		}
	&icons_table(\@links, \@titles, \@icons, 6, undef,
		     $imgicons ? ( 0, 0 ) : ( ));
	if ($config{'server_attach'} == 2 && @detach) {
		print "<input type=submit name=detach value='$text{'view_detach'}'>\n";
		print "<input type=hidden name=bindex value='$body->{'idx'}'>\n" if ($body);
		print "<input type=hidden name=sindex value='$sindex'>\n" if (defined($sindex));
		print "<select name=attach>\n";
		print "<option value=*>$text{'view_dall'}\n";
		foreach $a (@detach) {
			printf "<option value=%s>%s\n",
				$a->[0], $a->[1];
			}
		print "</select>\n";
		print "<b>$text{'view_dir'}</b>\n";
		print "<input name=dir size=40> ",
			&file_chooser_button("dir", 1),"\n";
		}
	print "</td></tr></table><p>\n";
	}

# Display GnuPG results
if (defined($sigcode)) {
	print "<table border width=100%>\n";
	print "<tr $tb> <td><b>$text{'view_gnupg'}</b></td> </tr>\n";
	print "<tr $cb> <td>";
	$sigmessage = &html_escape($sigmessage);
	$sigmessage = $sigmessage if ($sigcode == 4);
	print &text('view_gnupg_'.$sigcode, $sigmessage),"\n";
	if ($sigcode == 3) {
		local $url = "/$module_name/view_mail.cgi?idx=$in{'idx'}&mid=$qmid&folder=$in{'folder'}$subs";
		print "<p>",&text('view_recv', $sigmessage, "/gnupg/recv.cgi?id=$sigmessage&return=".&urlize($url)."&returnmsg=".&urlize($text{'view_return'})),"\n";
		}
	print "</td> </tr></table><p>\n";
	}
if ($deccode) {
	print "<table border width=100%>\n";
	print "<tr $tb> <td><b>$text{'view_crypt'}</b></td> </tr>\n";
	print "<tr $cb> <td>";
	print &text('view_crypt_'.$deccode, "<pre>$decmessage</pre>");
	print "</td> </tr></table><p>\n";
	}

# Display DSN status
if ($sent_dsn_to || $send_dsn_button || $got_dsn || @delmsgs) {
	print "<table border width=100%>\n";
	print "<tr $tb> <td><b>$text{'view_dsn'}</b></td> </tr>\n";
	print "<tr $cb> <td>";
	if ($sent_dsn_to) {
		print &text($sent_dsn ? 'view_dnsnow' : 'view_dsnbefore',
			    &html_escape($sent_dsn_to),
			    ($dsntm = localtime($sent_dsn_at)));
		}
	elsif ($send_dsn_button) {
		print &text('view_dsnreq', &html_escape($dsn_req)),"<br>\n";
		print &ui_submit($text{'view_dsnsend'}, "dsn");
		}
	elsif ($got_dsn) {
		print &text('view_dsngot', &html_escape($got_dsn_from),
			    ($dsntm = localtime($got_dsn))),"<br>\n";
		}
	elsif (@delmsgs) {
		print join("<br>\n", @delmsgs),"<br>\n";
		}
	print "</td> </tr></table><p>\n";
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
    ( "view_mail.cgi?idx=$in{'idx'}", $text{'view_return'} ),
$s = int((@mail - $in{'idx'} - 1) / $userconfig{'perpage'}) *
	$userconfig{'perpage'};
&mail_page_footer(@sub ? ( "view_mail.cgi?idx=$in{'idx'}&mid=$in{'mid'}&folder=$in{'folder'}",
		 $text{'view_return'} ) : ( ),
	"index.cgi?folder=$in{'folder'}&start=$in{'start'}",
	$text{'mail_return'});

&pop3_logout_all();

# show_buttons(pos, submode)
sub show_buttons
{
local $spacer = "&nbsp;\n";
if ($folder->{'sent'} || $folder->{'drafts'}) {
	print "<input type=submit value=\"$text{'view_enew'}\" name=enew>";
	}
else {
	print "<input type=submit value=\"$text{'view_reply'}\" name=reply>";
	print "<input type=submit value=\"$text{'view_reply2'}\" name=rall>";
	}
print $spacer;

print "<input type=submit value=\"$text{'view_forward'}\" name=forward>";
print $spacer;

if ($userconfig{'open_mode'}) {
	# Compose button needs to pop up a window
	print "<input type=submit name=new value=\"$text{'mail_compose'}\" ",
	      "onClick='window.open(\"reply_mail.cgi?new=1\", \"compose\", \"toolbar=no,menubar=no,scrollbars=yes,width=1024,height=768\"); return false'>";
	}
else {
	# Compose button can just submit and redirect
	print "<input type=submit name=new value=\"$text{'mail_compose'}\">";
	}
print $spacer;

if (!$_[1]) {
	if (!$folder->{'sent'} && !$folder->{'drafts'}) {
		$m = $read{$mail->{'header'}->{'message-id'}};
		print "<input name=mark$_[0] type=submit value=\"$text{'view_mark'}\">";
		print "<select name=mode$_[0]>\n";
		foreach $i (0 .. 2) {
			printf "<option value=%d %s>%s\n",
				$i, $m == $i ? 'selected' : '', $text{"view_mark$i"};
			}
		print "</select>";
		print $spacer;
		}

	if (@folders > 1) {
		print &movecopy_select($_[0], \@folders, $folder);
		print $spacer;
		}

	print "<input type=submit value=\"$text{'view_delete'}\" name=delete ",
	      "onClick='return check_clicks(form)'>";
	print $spacer;
	}
else {
	if (@folders > 1) {
		print &movecopy_select($_[0], \@folders, $folder, 1);
		print $spacer;
		}
	}
print "<input type=submit value=\"$text{'view_print'}\" name=print>";
print $spacer;

if (!$_[1]) {
	# Show spam and/or ham report buttons
	if (&can_report_spam($folder) &&
	    $userconfig{'spam_buttons'} =~ /mail/) {
		print "<input type=submit value=\"$text{'view_black'}\" name=black>";
		if ($userconfig{'spam_del'}) {
			print "<input type=submit value=\"$text{'view_razordel'}\" name=razor>";
			}
		else {
			print "<input type=submit value=\"$text{'view_razor'}\" name=razor>";
			}
		print $spacer;
		}
	if (&can_report_ham($folder) &&
	    $userconfig{'ham_buttons'} =~ /mail/) {
		print "<input type=submit value=\"$text{'view_white'}\" name=white>";
		print "<input type=submit value=\"$text{'view_ham'}\" name=ham>";
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
	if ($inbook{$a->[0]}) {
		push(@rv, &eucconv_and_escape($a->[2]));
		}
	else {
		## name= will be EUC encoded now since split_addresses()
		## is feeded with EUC converted value.
		push(@rv, "<a href='add_address.cgi?addr=".&urlize($a->[0]).
			  "&name=".&urlize($a->[1])."&idx=$in{'idx'}".
			  "&folder=$in{'folder'}$subs'>".
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
	local $c = scalar(@mail);
	local $prv = $mail->{'sortidx'} == 0 ? 0 : $mail->{'sortidx'}-1;
	local $nxt = $mail->{'sortidx'} == $c-1 ? $c-1 : $mail->{'sortidx'}+1;
	local @beside = &mailbox_list_mails_sorted($prv, $nxt, $folder, 1);

	if ($mail->{'sortidx'} != 0) {
		local $mailprv = $beside[$prv];
		print "<a href='view_mail.cgi?idx=",($mail->{'sortidx'}-1),
		      "&mid=",&urlize($mailprv->{'header'}->{'message-id'}),
		      "&folder=$in{'folder'}'>",
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
		print "<a href='view_mail.cgi?idx=",($mail->{'sortidx'}+1),
		      "&mid=",&urlize($mailnxt->{'header'}->{'message-id'}),
		      "&folder=$in{'folder'}'>",
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

