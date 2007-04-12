#!/usr/local/bin/perl
# view_mail.cgi
# View a single email message 

require './spam-lib.pl';
&foreign_require("mailbox", "mailbox-lib.pl");
$folder = &spam_file_folder();
&disable_indexing($folder);

$force_charset = '';
&ReadParse();

&ui_print_header(undef, $mailbox::text{'view_title'}, "");
@mail = &mailbox::mailbox_list_mails_sorted($in{'idx'}, $in{'idx'}, $folder);
$mail = $mail[$in{'idx'}];
&mailbox::parse_mail($mail);
@sub = split(/\0/, $in{'sub'});
$subs = join("", map { "&sub=$_" } @sub);
foreach $s (@sub) {
        # We are looking at a mail within a mail ..
	&mailbox::decrypt_attachments($mail);
        local $amail = &mailbox::extract_mail($mail->{'attach'}->[$s]->{'data'});
        &mailbox::parse_mail($amail);
        $mail = $amail;
        }

dbmopen(%read, "$user_config_directory/mailbox/read", 0600);
if ($mailbox::userconfig{'auto_mark'}) {
	eval { $read{$mail->{'header'}->{'message-id'}} = 1 }
		if (!$read{$mail->{'header'}->{'message-id'}});
	}

print "<center>\n";
if (!@sub) {
	if ($in{'idx'}) {
		print "<a href='view_mail.cgi?idx=",
		      $in{'idx'}-1,"'>",
		      "<img src=/images/left.gif border=0 ",
		      "align=middle></a>\n";
		}
	print "<font size=+1>",&mailbox::text('view_desc', $in{'idx'}+1,
			$folder->{'name'}),"</font>\n";
	if ($in{'idx'} < @mail-1) {
		print "<a href='view_mail.cgi?idx=",
		      $in{'idx'}+1,"'>",
		      "<img src=/images/right.gif border=0 ",
		      "align=middle></a>\n";
		}
	}
else {
	print "<font size=+1>$text{'view_sub'}</font>\n";
	}
print "</center>\n";

# Check for encryption
($deccode, $decmessage) = &mailbox::decrypt_attachments($mail);
@attach = @{$mail->{'attach'}};

# Find body attachment and type
($textbody, $htmlbody, $body) = &mailbox::find_body($mail);

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
		}
	elsif ($body && $body eq $textbody && $body->{'data'} =~ /(-+BEGIN PGP SIGNED MESSAGE-+\n(Hash:\s+(\S+)\n\n)?([\000-\377]+\n)-+BEGIN PGP SIGNATURE-+\n([\000-\377]+)-+END PGP SIGNATURE-+\n)/i) {
		# Signature is in body text!
		local $sig = $1;
		local $text = $4;
		&foreign_require("gnupg", "gnupg-lib.pl");
		($sigcode, $sigmessage) = &foreign_call("gnupg",
							"verify_data", $sig);
		if ($sigcode == 0 || $sigcode == 1) {
			# XXX what about replying?
			$body->{'data'} = $text;
			}
		}
	}

# Strip out attachments not to display as icons
@attach = grep { $_ ne $body } @attach;
@attach = grep { !$_->{'attach'} } @attach;

print "<table width=100% border=1>\n";
print "<tr> <td $tb><table width=100% cellpadding=0 cellspacing=0><tr>",
      "<td><b>$mailbox::text{'view_headers'}</b></td>\n";
if ($in{'headers'}) {
	print "<td align=right><a href='view_mail.cgi?idx=$in{'idx'}&headers=0$subs'>$mailbox::text{'view_noheaders'}</a></td>\n";
	}
else {
	print "<td align=right><a href='view_mail.cgi?idx=$in{'idx'}&headers=1$subs'>$mailbox::text{'view_allheaders'}</a></td>\n";
	}
print "</tr></table></td> </tr>\n";

print "<tr> <td $cb><table width=100%>\n";
if ($in{'headers'}) {
	# Show all the headers
	if ($mail->{'fromline'}) {
		print "<tr> <td><b>$text{'mail_rfc'}</b></td>",
		      "<td>",&mailbox::eucconv(&html_escape($mail->{'fromline'})),
		      "</td> </tr>\n";
		}
	foreach $h (@{$mail->{'headers'}}) {
		print "<tr> <td><b>$h->[0]:</b></td> ",
		      "<td>",&mailbox::eucconv(&html_escape(&mailbox::decode_mimewords($h->[1]))),
		      "</td> </tr>\n";
		}
	}
else {
	# Just show the most useful headers
	print "<tr> <td><b>$mailbox::text{'mail_from'}</b></td> ",
	      "<td>",&address_link($mail->{'header'}->{'from'}),"</td> </tr>\n";
	print "<tr> <td><b>$mailbox::text{'mail_to'}</b></td> ",
	      "<td>",&address_link($mail->{'header'}->{'to'}),"</td> </tr>\n";
	print "<tr> <td><b>$mailbox::text{'mail_cc'}</b></td> ",
	      "<td>",&address_link($mail->{'header'}->{'cc'}),"</td> </tr>\n"
		if ($mail->{'header'}->{'cc'});
	print "<tr> <td><b>$mailbox::text{'mail_date'}</b></td> ",
	      "<td>",&mailbox::eucconv(&html_escape($mail->{'header'}->{'date'})),
	      "</td> </tr>\n";
	print "<tr> <td><b>$mailbox::text{'mail_subject'}</b></td> ",
	      "<td>",&mailbox::eucconv(&html_escape(&mailbox::decode_mimewords(
			$mail->{'header'}->{'subject'}))),"</td> </tr>\n";
	if (!@sub) {
		print "<tr> <td><b>$text{'mail_level2'}</b></td> ",
		      "<td>",length($mail->{'header'}->{'x-spam-level'}),"</td> </tr>\n";
		}
	}
print "</table></td></tr></table><p>\n";

# Show body attachment, with properly linked URLs
if ($body && $body->{'data'} =~ /\S/) {
	if ($body eq $textbody) {
		# Show plain text
		print "<table width=100% border=1><tr><td $cb><pre>\n";
		foreach $l (&mailbox::wrap_lines($body->{'data'},
					$mailbox::userconfig{'wrap_width'})) {
			print &mailbox::link_urls_and_escape($l),"\n";
			}
		print "</pre></td></tr></table><p>\n";
		}
	elsif ($body eq $htmlbody) {
		# Attempt to show HTML
		print "<table width=100% border=1><tr><td>\n";
		print &mailbox::safe_html($body->{'data'});
		print "</td></tr></table><p>\n";
		}
	}

# Display other attachments
if (@attach) {
	print "<table width=100% border=1>\n";
	print "<tr> <td $tb><b>$mailbox::text{'view_attach'}</b></td> </tr>\n";
	print "<tr> <td $cb>\n";
	foreach $a (@attach) {
		local $fn;
		$size = (int(length($a->{'data'})/1000)+1)." Kb";
		local $cb;
		if ($a->{'type'} eq 'message/rfc822') {
			push(@titles, "$mailbox::text{'view_sub'}<br>$size");
			}
		elsif ($a->{'filename'}) {
			push(@titles, &mailbox::decode_mimewords($a->{'filename'}).
				      "<br>$size");
			$fn = &mailbox::decode_mimewords($a->{'filename'});
			push(@detach, [ $a->{'idx'}, $fn ]);
			}
		else {
			push(@titles, "$a->{'type'}<br>$size");
			$a->{'type'} =~ /\/(\S+)$/;
			$fn = "file.$1";
			push(@detach, [ $a->{'idx'}, $fn ]);
			}
		$fn =~ s/ /_/g;
		$fn =~ s/\#/_/g;
		$fn = &html_escape($fn);
		if ($a->{'type'} eq 'message/rfc822') {
			push(@links, "view_mail.cgi?idx=$in{'idx'}$subs&sub=$a->{'idx'}");
			}
		else {
			push(@links, "detach.cgi/$fn?idx=$in{'idx'}&attach=$a->{'idx'}$subs");
			}
		push(@icons, "/mailbox/images/boxes.gif");
		}
	&icons_table(\@links, \@titles, \@icons, 8);
	print "</td></tr></table><p>\n";
	}

# Display GnuPG results
if (defined($sigcode)) {
	print "<table border width=100%>\n";
	print "<tr $tb> <td><b>$mailbox::text{'view_gnupg'}</b></td> </tr>\n";
	print "<tr $cb> <td>";
	$sigmessage = &html_escape($sigmessage);
	$sigmessage = $sigmessage if ($sigcode == 4);
	print &mailbox::text('view_gnupg_'.$sigcode, $sigmessage),"\n";
	if ($sigcode == 3) {
		local $url = "/$module_name/view_mail.cgi?idx=$in{'idx'}&folder=$in{'folder'}$subs";
		print "<p>",&mailbox::text('view_recv', $sigmessage, "/gnupg/recv.cgi?id=$sigmessage&return=".&urlize($url)."&returnmsg=".&urlize($text{'view_return'})),"\n";
		}
	print "</td> </tr></table><p>\n";
	}
if ($deccode) {
	print "<table border width=100%>\n";
	print "<tr $tb> <td><b>$text{'view_crypt'}</b></td> </tr>\n";
	print "<tr $cb> <td>";
	print &mailbox::text('view_crypt_'.$deccode, "<pre>$decmessage</pre>");
	print "</td> </tr></table><p>\n";
	}

dbmclose(%read);

local @sr = !@sub ? ( ) :
    ( "view_mail.cgi?idx=$in{'idx'}", $mailbox::text{'view_return'} ),
$s = int((@mail - $in{'idx'} - 1) / $mailbox::userconfig{'perpage'}) *
	$mailbox::userconfig{'perpage'};
&ui_print_footer(@sub ? ( "view_mail.cgi?idx=$in{'idx'}",
		 $mailbox::text{'view_return'} ) : ( ),
	"mail.cgi", $text{'mail_return'});

# address_link(address)
sub address_link
{
local @addrs = &mailbox::split_addresses(&mailbox::decode_mimewords($_[0]));
local @rv;
foreach $a (@addrs) {
	push(@rv, &html_escape($a->[2]));
	}
return join(" , ", @rv);
}

