#!/usr/local/bin/perl
# send_mail.cgi
# Send off an email message
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in, %config, %userconfig);
our @remote_user_info;

require './mailbox-lib.pl';
require '../html-editor-lib.pl';

# Check inputs
my %getin;
&ReadParse(\%getin, "GET");
&ReadParseMime(undef, \&read_parse_mime_callback, [ $getin{'id'} ], 1);
foreach my $k (keys %in) {
	$in{$k} = join("\0", @{$in{$k}}) if ($k !~ /^attach\d+/);
	}
&set_module_index($in{'folder'});
my @folders = &list_folders_sorted(); 
my ($folder) = grep { $_->{'index'} == $in{'folder'} } @folders;
$folder || &error($text{'view_efolder'});
&error_setup($text{'send_err'});
if (!$in{'subject'}) {
	if ($userconfig{'force_subject'} eq 'error') {
		&error($text{'send_esubject'});
		}
	elsif ($userconfig{'force_subject'}) {
		$in{'subject'} = $userconfig{'force_subject'};
		}
	}
my @sub = $in{'sub'} ? split(/\0/, $in{'sub'}) : ();
my $subs = join("", map { "&sub=$_" } @sub);
my $draft = $in{'draft'} || $in{'save'};

no warnings "once";
$main::force_charset = $in{'charset'};
use warnings "once";

# Construct the email
if ($config{'edit_from'} == 2) {
	$in{'user'} || &error($text{'send_efrom'});
	$in{'from'} = $in{'dom'} ? "$in{'user'}\@$in{'dom'}" : $in{'user'};
	if ($in{'real'}) {
		$in{'from'} = "\"$in{'real'}\" <$in{'from'}>";
		}
	}
else {
	$in{'from'} || &error($text{'send_efrom'});
	}
$in{'to'} = &expand_to($in{'to'});
$in{'cc'} = &expand_to($in{'cc'});
$in{'bcc'} = &expand_to($in{'bcc'});
my $newmid = &generate_message_id($in{'from'});
my %enc = ( 'Charset' => $in{'charset'} );
my $mail;
$mail->{'headers'} = [ [ 'From', &encode_mimewords_address($in{'from'}, %enc) ],
		       [ 'Subject', &encode_mimewords($in{'subject'}, %enc) ],
		       [ 'To', &encode_mimewords_address($in{'to'}, %enc) ],
		       [ 'Message-Id', $newmid ] ];
if ($in{'cc'}) {
	push(@{$mail->{'headers'}},
	     [ 'Cc', &encode_mimewords_address($in{'cc'}, %enc) ]);
	}
if ($in{'bcc'}) {
	push(@{$mail->{'headers'}},
	     [ 'Bcc', &encode_mimewords_address($in{'bcc'}, %enc) ]);
	}
&add_mailer_ip_headers($mail->{'headers'});
$mail->{'header'}->{'message-id'} = $newmid;
push(@{$mail->{'headers'}}, [ 'X-Priority', $in{'pri'} ]) if ($in{'pri'});
push(@{$mail->{'headers'}}, [ 'In-Reply-To', $in{'rid'} ]) if ($in{'rid'});
if ($userconfig{'req_dsn'} == 1 ||
    $userconfig{'req_dsn'} == 2 && $in{'dsn'}) {
	push(@{$mail->{'headers'}}, [ 'Disposition-Notification-To',
			      &encode_mimewords_address($in{'from'}, %enc) ]);
	push(@{$mail->{'headers'}}, [ 'Read-Receipt-To',
			      &encode_mimewords_address($in{'from'}, %enc) ]);
	}
if ($in{'replyto'}) {
	# Add real name to reply-to address, if not given and if possible
	my $r2 = $in{'replyto'};
	my ($r2parts) = &split_addresses($r2);
	$r2 = $r2parts->[1] || !$userconfig{'real_name'} ||
		    !$remote_user_info[6] ? $in{'replyto'} :
			"\"$remote_user_info[6]\" <$r2parts->[0]>";
	push(@{$mail->{'headers'}}, [ 'Reply-To',
				&encode_mimewords_address($r2, %enc) ]);
	}

# Make sure we have a recipient
$in{'to'} =~ /\S/ || $in{'cc'} =~ /\S/ || $in{'bcc'} =~ /\S/ || $draft ||
	&error($text{'send_eto'});

$in{'body'} =~ s/\r//g;
my %cidmap;
my (@attach, $bodyattach);
my @inline_images;
my $quoted_printable;
if ($in{'body'} =~ /\S/) {
	if ($in{'html_edit'}) {
		$in{'body'} = &html_editor_substitute_classes_with_styles($in{'body'});
		}
	my $preplainbody = $in{'body'};
	my $prehtmlbody = $in{'body'};
	
	# Extract inline images if any
	@inline_images = ($in{'body'} =~ /(data:image\/.*?;base64,)(.*?)"/g);
	if (@inline_images) {
	    my $iid = 1;
	    for (my $i = 0; $i < scalar(@inline_images) - 1; $i += 2) {
	        if ($inline_images[$i] =~ /data:image/) {
	            my ($type) = $inline_images[$i] =~ /data:image\/(.*?);base64,/;
	            my $cid = "ii_".(time() + $i).'@'."$type";
	            my $replace_html = "$inline_images[$i]$inline_images[$i+1]";
	            my @data = split('@', $cid);
            	$inline_images[$i] = \@data;
	            $inline_images[$i+1] = decode_base64($inline_images[$i+1]);

	            # $cid = "cid:$cid\" style=\"width: 60%";
	            $cid = "cid:$cid";

	            # Replace for HTML
	            $in{'body'} =~ s/\Q$replace_html/$cid/;

	            # Replace for plain text
	            $preplainbody =~ s/<img[^>]*>/[image: inline-image$iid.$type]/;
	            $iid++;
	            }
	        }
	        $prehtmlbody = $in{'body'};
	    }
	my $plainbody = $in{'html_edit'} ? &html_to_text($preplainbody)
					    : $prehtmlbody;
	# Perform spell check on body if requested
	if ($in{'spell'}) {
		my @errs = &spell_check_text($plainbody);
		if (@errs) {
			# Spelling errors found!
			&mail_page_header($text{'compose_title'});
			print "<b>$text{'send_espell'}</b><p>\n";
			print map { $_."<p>\n" } @errs;
			&ui_print_footer(
				"javascript:back()", $text{'reply_return'},
				"index.cgi?folder=$in{'folder'}",
				$text{'mail_return'});
			exit;
			}
		}

	# For a HTML body, replace images from detach.cgi on the original
	# email with cid: references.
	if ($in{'html_edit'}) {
		$in{'body'} = &create_cids($in{'body'}, \%cidmap);
		}

	# Create the body attachment
	my $mt = $in{'html_edit'} ? "text/html" : "text/plain";
	my $wrapped_body = $in{'body'};
	if (!$in{'html_edit'}) {
		$wrapped_body = join("\n", &wrap_lines($wrapped_body, 998));
		}
	my $charset = $in{'charset'} || $userconfig{'charset'};
	$mt .= "; charset=$charset";
	if ($config{'html_base64'} == 2) {
		# Use base64 encoding
		@attach = ( { 'headers' => [ [ 'Content-Type', $mt ],
					     [ 'Content-Transfer-Encoding',
					       'base64' ] ],
			      'data' => $wrapped_body } );
		}
	elsif ($in{'body'} =~ /[\177-\377]/ || $config{'html_base64'} == 1) {
		# Contains 8-bit characters .. need to make quoted-printable
		$quoted_printable++;
		@attach = ( { 'headers' => [ [ 'Content-Type', $mt ],
					     [ 'Content-Transfer-Encoding',
					       'quoted-printable' ] ],
			      'data' => quoted_encode($wrapped_body) } );
		}
	else {
		# Plain 7-bit ascii text
		@attach = ( { 'headers' => [ [ 'Content-Type', $mt ],
					     [ 'Content-Transfer-Encoding',
					       '7bit' ] ],
			      'data' => $wrapped_body } );
		}
	$bodyattach = $attach[0];

	if ($in{'html_edit'}) {
		# Create an attachment which contains both the HTML and plain
		# bodies as alternatives
		my @alts = ( $attach[0] );
		my $mt = "text/plain; charset=$charset";
		if ($plainbody =~ /[\177-\377]/) {
			unshift(@alts,
			  { 'headers' => [ [ 'Content-Type', $mt ],
					   [ 'Content-Transfer-Encoding',
					     'quoted-printable' ] ],
			    'data' => quoted_encode($plainbody) });
			}
		else {
			unshift(@alts,
			  { 'headers' => [ [ 'Content-Type', $mt ],
					   [ 'Content-Transfer-Encoding',
					     '7bit' ] ],
			    'data' => $plainbody });
			}

		# Set content type to multipart/alternative, to tell mail
		# clients about the optional body
		my $bound = "altsbound".time();
		$attach[0] = {
			'headers' => [ [ 'Content-Type',
					 'multipart/alternative; '.
					 'boundary="'.$bound.'"' ],
				       [ 'Content-Transfer-Encoding',
					 '7bit' ] ],
			'data' => join("", &unparse_mail(\@alts, "\n", $bound))
			};
		}
	}

# Add inline images
if (@inline_images) {
    my $iid = 1;
    for (my $i = 0; $i < scalar(@inline_images) - 1; $i += 2) {
        my $cid = $inline_images[$i][0]."@".$inline_images[$i][1];
        my $type = $inline_images[$i][1];
        my $image_name = "inline-image$iid.$type";
        my $data = $inline_images[$i + 1];
        push(@attach,
             {  'data'    => $data,
                'headers' => [['Content-type',              "image/$type; name=\"$image_name\""],
                              ['Content-Disposition',       "inline; filename=\"$image_name\""],
                              ['Content-ID',                "<$cid>"],
                              ['Content-Transfer-Encoding', 'base64']
                ]
             });
        $iid++;
    	}
	}

# Add uploaded attachments
my $attachsize = 0;
for(my $i=0; defined($in{"attach$i"}); $i++) {
	next if (!$in{"attach$i"});
	for(my $j=0; $j<@{$in{"attach$i"}}; $j++) {
		next if (!$in{"attach${i}"}->[$j]);
		&test_max_attach(length($in{"attach${i}"}->[$j]));
		my $filename = $in{"attach${i}_filename"}->[$j];
		$filename =~ s/^.*(\\|\/)//;
		my $type = $in{"attach${i}_content_type"}->[$j].
			      "; name=\"".$filename."\"";
		my $disp = "attachment; filename=\"".$filename."\"";
		push(@attach, { 'data' => $in{"attach${i}"}->[$j],
				'headers' => [ [ 'Content-type', $type ],
					       [ 'Content-Disposition', $disp ],
					       [ 'Content-Transfer-Encoding',
						 'base64' ] ] });
		}
	}

# Add server-side attachments
for(my $i=0; defined($in{"file$i"}); $i++) {
	next if (!$in{"file$i"} || !$config{'server_attach'});
	if ($in{"file$i"} !~ /^\//) {
		$in{"file$i"} = $remote_user_info[7]."/".$in{"file$i"};
		}
	-r $in{"file$i"} && !-d $in{"file$i"} ||
		&error(&text('send_efile', $in{"file$i"}));
	my @st = stat($in{"file$i"});
	&test_max_attach($st[7]);
	my $data;
	open(my $DATA, "<", $in{"file$i"}) ||
		&error(&text('send_efile', $in{"file$i"}));
	while(<$DATA>) {
		$data .= $_;
		}
	close($DATA);
	$in{"file$i"} =~ s/^.*\///;
	my $type = &guess_mime_type($in{"file$i"}).
		      "; name=\"".$in{"file$i"}."\"";
	my $disp = "attachments; filename=\"".$in{"file$i"}."\"";
	push(@attach, { 'data' => $data,
			'headers' => [ [ 'Content-type', $type ],
				       [ 'Content-Disposition', $disp ],
				       [ 'Content-Transfer-Encoding',
					 'base64' ] ] });
	}

# Add forwarded attachments
my @fwd = split(/\0/, $in{'forward'});
my ($sortfield, $sortdir) = &get_sort_field($folder);
if (@fwd) {
	my $fwdmail = &mailbox_get_mail($folder, $in{'id'}, 0);
	&parse_mail($fwdmail);
	&decrypt_attachments($fwdmail);

	foreach my $s (@sub) {
		# We are looking at a mail within a mail ..
		&decrypt_attachments($fwdmail);
		my $amail = &extract_mail(
			$fwdmail->{'attach'}->[$s]->{'data'});
		&parse_mail($amail);
		$fwdmail = $amail;
		}

	foreach my $f (@fwd) {
		&test_max_attach(length($fwdmail->{'attach'}->[$f]->{'data'}));
		$a = $fwdmail->{'attach'}->[$f];
		if ($cidmap{$f}) {
			# This attachment has been inlined .. set a content-id
			$a->{'headers'} = [
				grep { lc($_->[0]) ne 'content-id' &&
				       lc($_->[0]) ne 'content-location' }
				     @{$a->{'headers'}} ];
			push(@{$a->{'headers'}},
			     [ 'Content-Id', "<$cidmap{$f}>" ]);
			}
		push(@attach, $a);
		}
	}

# Add forwarded emails
my @mailfwdids = split(/\0/, $in{'mailforward'});
if (@mailfwdids) {
	my @mailfwd = &mailbox_select_mails($folder, \@mailfwdids, 0);
	foreach my $fwdmail (@mailfwd) {
		my $headertext;
		foreach my $h (@{$fwdmail->{'headers'}}) {
			$headertext .= $h->[0].": ".$h->[1]."\n";
			}
		push(@attach, { 'data' => $headertext."\n".$fwdmail->{'body'},
				'headers' => [ [ 'Content-type', 'message/rfc822' ],
					       [ 'Content-Description',
						  $fwdmail->{'header'}->{'subject'} ] ]
			      });
		}
	}
if ($in{'sign'} ne '' && !$draft) {
	# Put all the attachments into a single attachment, with the signature
	# as the second attachment
	&foreign_require("gnupg", "gnupg-lib.pl");
	my @keys = &foreign_call("gnupg", "list_keys");
	my $key = $keys[$in{'sign'}];

	# Create the new attachment
	push(@{$mail->{'headers'}}, [ 'Content-Type', 'multipart/signed; micalg=pgp-sha1; protocol="application/pgp-signature"' ] );
	my ($tempdata, $tempheaders, $tempbody);
	if (@attach == 1) {
		# Just use one part
		$tempdata = &write_attachment($attach[0]);
		$tempheaders = $attach[0]->{'headers'};
		$tempbody = $attach[0]->{'data'};
		}
	else {
		# Create new attachment containing all the parts
		my $bound = "sign".time();
		foreach my $a (@attach) {
			$tempbody .= "\r\n";
			$tempbody .= "--".$bound."\r\n";
			$tempbody .= &write_attachment($a);
			}
		$tempbody .= "\r\n";
		$tempbody .= "--".$bound."--\r\n";
		$tempdata ="Content-Type: multipart/mixed; boundary=\"$bound\"\r\n".
			   "\r\n".
			   $tempbody;
		$tempheaders = [ [ "Content-Type", "multipart/mixed; boundary=\"$bound\"" ] ];
		}

	# Sign the file
	my $sigdata;
	my $rv = &foreign_call("gnupg", "sign_data", $tempdata, \$sigdata,
				  $key, 2);
	if ($rv) {
		&error(&text('send_esign', $rv));
		}

	@attach = ( { 'data' => $tempbody,
		      'headers' => $tempheaders },
		    { 'data' => $sigdata,
		      'headers' => [ [ "Content-Type", "application/pgp-signature; name=signature.asc" ] ] }
		  );
	}
$mail->{'attach'} = \@attach;

if ($in{'crypt'} ne '' && !$draft) {
	# Encrypt the entire mail
	&foreign_require("gnupg", "gnupg-lib.pl");
	my @keys = &foreign_call("gnupg", "list_keys");
	my @ekeys;
	my $key;
	if ($in{'crypt'} == -1) {
		# Find the keys for the To:, Cc: and Bcc: address
		my @addrs = ( &address_parts($in{'to'}),
				 &address_parts($in{'cc'}),
				 &address_parts($in{'bcc'}) );
		foreach my $a (@addrs) {
			my $k = &find_email_in_keys($a, \@keys);
			if (!$k) {
				# Check keyserver for it
				my @srv = grep { !$_->{'revoked'} }
					    &gnupg::search_gpg_keys($a);
				if (@srv) {
					my ($ok, $msg) = &gnupg::fetch_gpg_key(
						$srv[0]->{'key'});
					if ($ok == 0) {
						$k = $msg;
						}
					}
				}
			if ($k) {
				push(@ekeys, $k);
				}
			else {
				&error(&text('send_ekey', $a));
				}
			}
		}
	else {
		@ekeys = ( $keys[$in{'crypt'}] );
		}
	if ($userconfig{'self_crypt'}) {
		my ($skey) = grep { $_->{'secret'} } @keys;
		push(@ekeys, $skey);
		}
	my $temp = &transname();
	&send_mail($mail, $temp);
	my ($tempdata, $buf);
	open(my $TEMP, "<", $temp);
	my $dummy = <$TEMP>;	# skip From line
	while(read($TEMP, $buf, 1024) > 0) {
		$tempdata .= $buf;
		}
	close($TEMP);
	unlink($temp);
	my $crypted;
	my $rv = &foreign_call("gnupg", "encrypt_data", $tempdata,
				  \$crypted, \@ekeys, 1);
	$rv && &error(&text('send_ecrypt', $rv));

	# Put into new attachments format
	$mail->{'headers'} =
	       [ ( grep { lc($_->[0]) ne 'content-type' } @{$mail->{'headers'}} ),
	         [ 'Content-Type',
		   'multipart/encrypted; protocol="application/pgp-encrypted"' ] ];
	$mail->{'attach'} =
		[ { 'headers' => [ [ 'Content-Transfer-Encoding', '7bit' ],
				   [ 'Content-Type', 'application/pgp-encrypted'] ],
		    'data' => "Version: 1\n" },
		  { 'headers' => [ [ 'Content-Transfer-Encoding', '7bit' ],
				   [ 'Content-Type', 'application/octet-stream' ] ],
		    'data' => $crypted }
		];
	}

# Check for text-only email
my $textonly = $userconfig{'no_mime'} && !$quoted_printable &&
	    @{$mail->{'attach'}} == 1 &&
	    $mail->{'attach'}->[0] eq $bodyattach && !$in{'html_edit'};

# Tell the user what is happening
if (!$in{'save'}) {
	&mail_page_header($draft ? $text{'send_title2'} : $text{'send_title'});
	my @tos = ( split(/,/, $in{'to'}), split(/,/, $in{'cc'}),
		 split(/,/, $in{'bcc'}) );
	my $tos = join(" , ", map { "<tt>".&html_escape($_)."</tt>" } @tos);
	print &text($draft ? 'send_draft' : 'send_sending',
		    $tos || $text{'send_nobody'}),"<p>\n";
	}

my $savefolder = $folder;
my $dfolder; # XXX Hairy.
if ($draft) {
	# Save in the drafts folder
	($dfolder) = grep { $_->{'drafts'} } @folders;
	my $qerr = &would_exceed_quota($dfolder, $mail);
	&error($qerr) if ($qerr);
	&lock_folder($dfolder);
	if ($in{'enew'} && $folder->{'drafts'} &&
	    $folder->{'type'} != 2 && $folder->{'type'} != 4) {
		# Update existing draft mail (unless on IMAP)
		my ($dsortfield, $dsortdir) = &get_sort_field($dfolder);
		my $oldmail = &mailbox_get_mail($folder, $in{'id'}, 0);
		$oldmail || &error($text{'view_egone'});
		&mailbox_modify_mail($oldmail, $mail, $dfolder, $textonly);
		}
	else {
		# Save as a new draft
		&write_mail_folder($mail, $dfolder, $textonly);
		}
	&unlock_folder($dfolder);
	$savefolder = $dfolder;
	}
else {
	# Send it off and optionally save in sent mail
	my $sfolder;
	if ($userconfig{'save_sent'}) {
		($sfolder) = grep { $_->{'sent'} } @folders;
		if ($sfolder) {
			my $qerr = &would_exceed_quota($sfolder, $mail);
			&error($qerr) if ($qerr);
			}
		}
	my $notify = $userconfig{'req_del'} == 1 ||
		  $userconfig{'req_del'} == 2 && $in{'del'} ?
			[ "SUCCESS","FAILURE" ] : undef;
	&send_mail($mail, undef, $textonly, $config{'no_crlf'},
		   undef, undef, undef, undef,
		   $notify);
	if ($sfolder) {
		&lock_folder($sfolder);
		&write_mail_folder($mail, $sfolder, $textonly);
		&unlock_folder($sfolder);
		$savefolder = $sfolder;
		}
	}

# Mark the new message as read
&set_mail_read($savefolder, $mail, 1);

if ($in{'replyid'}) {
	# Mark the original as being replied to
	my ($replymail) = &mailbox_select_mails($folder, [ $in{'replyid'} ], 1);
	if ($replymail) {
		my $replyread = &get_mail_read($folder, $replymail);
		$replyread = ($replyread|4);
		&set_mail_read($folder, $replymail, $replyread);
		}
	}

if ($in{'abook'}) {
	# Add all recipients to the address book, if missing
	my @recips = ( &split_addresses($in{'to'}),
		    	  &split_addresses($in{'cc'}),
		    	  &split_addresses($in{'bcc'}) );
	my @addrs = &list_addresses();
	foreach my $r (@recips) {
		my ($already) = grep { $_->[0] eq $r->[0] } @addrs;
		if (!$already) {
			&create_address($r->[0], $r->[1]);
			push(@addrs, [ $r->[0], $r->[1] ]);
			}
		}
	}

if ($userconfig{'white_rec'}) {
	# Add all recipients to the SpamAssassin whitelist
	my @recips = ( &split_addresses($in{'to'}),
		    	  &split_addresses($in{'cc'}),
		    	  &split_addresses($in{'bcc'}) );
	my @recip_addrs = map { $_->[0] } @recips;
	&addressbook_add_whitelist(@recip_addrs);
	}

if ($in{'save'}) {
	# Redirect back to editing the email
	my $folder_id = $dfolder->{'id'} || $dfolder->{'file'};
	&redirect("reply_mail.cgi?folder=$dfolder->{'index'}&folder_type=$folder->{'type'}&folder_id=$folder_id&id=$mail->{'id'}&enew=1");
	exit;
	}

if ($userconfig{'send_return'}) {
	# Return to mail list
	print &js_redirect("index.cgi?folder=$in{'folder'}&start=$in{'start'}");
	}

# Print footer
print "$text{'send_done'}<p>\n";
if ($in{'id'} ne '') {
	&mail_page_footer(
	    "view_mail.cgi?id=".&urlize($in{'id'}).
	    "&folder=$in{'folder'}&start=$in{'start'}$subs",
	     $text{'view_return'},
	    "index.cgi?folder=$in{'folder'}&start=$in{'start'}",
	     $text{'mail_return'});
	}
else {
	&mail_page_footer(
	       "reply_mail.cgi?new=1&folder=$in{'folder'}&start=$in{'start'}",
			 $text{'reply_return'},
			 "index.cgi?folder=$in{'folder'}&start=$in{'start'}",
			 $text{'mail_return'});
	}

# write_attachment(&attach)
sub write_attachment
{
my ($a) = @_;
my ($enc, $rv);
foreach my $h (@{$a->{'headers'}}) {
	$rv .= $h->[0].": ".$h->[1]."\r\n";
	$enc = $h->[1]
	    if (lc($h->[0]) eq 'content-transfer-encoding');
	}
$rv .= "\r\n";
if (lc($enc) eq 'base64') {
	my $encoded = &encode_base64($a->{'data'});
	$encoded =~ s/\r//g;
	$encoded =~ s/\n/\r\n/g;
	$rv .= $encoded;
	}
else {
	$a->{'data'} =~ s/\r//g;
	$a->{'data'} =~ s/\n/\r\n/g;
	$rv .= $a->{'data'};
	if ($a->{'data'} !~ /\n$/) {
		$rv .= "\r\n";
		}
	}
return $rv;
}

sub test_max_attach
{
$attachsize += $_[0];
if ($config{'max_attach'} && $attachsize > $config{'max_attach'}) {
	&error(&text('send_eattachsize', $config{'max_attach'}));
	}
}

# find_email_in_keys(email, &keys)
# Given a list of keys, return the one that contains some email
sub find_email_in_keys
{
my ($a, $keys) = @_;
foreach my $k (@$keys) {
	if (&indexoflc($a, @{$k->{'email'}}) >= 0) {
		return $k;
		}
	}
return undef;
}
