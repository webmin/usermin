#!/usr/local/bin/perl
# Display a form for replying to or composing an email

require './mailbox-lib.pl';

&ReadParse();
&set_module_index($in{'folder'});
@folders = &list_folders();
$folder = $folders[$in{'folder'}];

if ($in{'new'}) {
	# Composing a new email
	if (defined($in{'html'})) {
		$html_edit = $in{'html'};
		}
	else {
		$html_edit = $userconfig{'html_edit'} == 2 ? 1 : 0;
		}
	$sig = &get_signature();
	if ($html_edit) {
		$sig =~ s/\n/<br>\n/g;
		$quote = "<html><body>$sig</body></html>";
		}
	else {
		$quote = "\n\n$sig" if ($sig);
		}
	$to = $in{'to'};
	&mail_page_header($text{'compose_title'},
			  undef,
			  $html_edit ? "onload='initEditor()'" : "");
	}
elsif ($in{'quick_send'} || $in{'quick'} && $in{'reply'}) {
	# Sending a quick reply
	$mail = &mailbox_get_mail($folder, $in{'id'}, 0);
	$mail || &error($text{'view_egone'});
	&decode_and_sub();
	$in{'quick'} =~ s/\r//g;
	$textonly = $userconfig{'no_mime'};

	# Remove signature
	($textbody, $htmlbody, $body) =
		&find_body($mail, $userconfig{'view_html'});
	&check_signature_attachments($mail->{'attach'}, $textbody);

	if ($in{'quick_quote'}) {
		# Get the original body to construct the email
		$sig = &get_signature();
		($quote, $html_edit, $body) = &quoted_message($mail, 1, $sig,
							     $in{'body'});
		if ($html_edit) {
			# HTML quoting
			$quick_type = "text/html";
			$quick_body = "<pre>".$in{'quick'}."</pre>".
				      "<p>\n".$quote;
			$textonly = 0;
			}
		else {
			# Text quoting
			$quick_type = "text/plain";
			$in{'quick'} =~ s/\s*$//g;
			$quick_body = $in{'quick'}."\n\n".$quote;
			}
		}
	else {
		# Body is just text
		$quick_body = $in{'quick'};
		$quick_type = "text/plain";
		}

	# Work out From: address for quick reply
	$from = &get_preferred_from_address();

	# Work out the subject and recipients
	$subject = &decode_mimewords($mail->{'header'}->{'subject'});
	$subject = "Re: ".$subject if ($subject !~ /^Re/i);
	$to = $mail->{'header'}->{'reply-to'} ||
	      $mail->{'header'}->{'from'};
	$cc = "";
	if ($in{'quick_all'}) {
		$cc = $mail->{'header'}->{'to'};
		$cc .= ", ".$mail->{'header'}->{'cc'}
			if ($mail->{'header'}->{'cc'});
		}

	# Construct the email
	$newmid = &generate_message_id($from);
	$qmail->{'headers'} = [ [ 'From', &encode_mimewords($from) ],
			        [ 'Subject', &encode_mimewords($subject) ],
			        [ 'To', &encode_mimewords($to) ],
			        [ 'Cc', &encode_mimewords($cc) ],
			        [ 'Message-Id', $newmid ] ];
	&add_mailer_ip_headers($qmail->{'headers'});
	$qmail->{'header'}->{'message-id'} = $newmid;
	$rid = $mail->{'header'}->{'message-id'};
	push(@{$qmail->{'headers'}}, [ 'In-Reply-To', $rid ]) if ($rid);
	if ($userconfig{'req_dsn'} == 1) {
		push(@{$mail->{'headers'}}, [ 'Disposition-Notification-To',
					      &encode_mimewords($from) ]);
		push(@{$mail->{'headers'}}, [ 'Read-Receipt-To',
					      &encode_mimewords($from) ]);
		}

	# Add the body
	$mt = $quick_type;
	$mt .= "; charset=$userconfig{'charset'}";
	if ($quick_body =~ /[\177-\377]/) {
		# Contains 8-bit characters .. need to make quoted-printable
		$textonly = 0;
		@attach = ( { 'headers' => [ [ 'Content-Type', $mt ],
					     [ 'Content-Transfer-Encoding',
					       'quoted-printable' ] ],
			      'data' => quoted_encode($quick_body) } );
		}
	else {
		# Plain 7-bit ascii text
		@attach = ( { 'headers' => [ [ 'Content-Type', $mt ],
					     [ 'Content-Transfer-Encoding',
					       '7bit' ] ],
			      'data' => $quick_body } );
		}

	# Inline HTML images
	# XXX

	# Tell the user
	&mail_page_header($draft ? $text{'send_title2'} : $text{'send_title'});
	@tos = ( split(/,/, $to), split(/,/, $cc) );
	$tos = join(" , ", map { "<tt>".&html_escape($_)."</tt>" } @tos);
	print &text('send_sending', $tos || $text{'send_nobody'}),"<p>\n";

	# Sent it off
	$qmail->{'attach'} = \@attach;
	local $sfolder;
	if ($userconfig{'save_sent'}) {
		($sfolder) = grep { $_->{'sent'} } @folders;
		if ($sfolder) {
			$qerr = &would_exceed_quota($sfolder, $qmail);
			&error($qerr) if ($qerr);
			}
		}
	$notify = $userconfig{'req_del'} == 1;
	&send_mail($qmail, undef, $textonly, $config{'no_crlf'},
		   undef, undef, undef, undef,
		   $notify);
	if ($sfolder) {
		&lock_folder($sfolder);
		&write_mail_folder($qmail, $sfolder, $textonly) if ($sfolder);
		&unlock_folder($sfolder);
		}
	&set_mail_read($sfolder, $qmail, 1);
	print "$text{'send_done'}<p>\n";

	if ($userconfig{'send_return'}) {
		# Return to mail list
		print "<script>\n";
		print "window.location = 'index.cgi?folder=$in{'folder'}&".
		      "start=$in{'start'}';\n";
		print "</script>\n";
		}

	&mail_page_footer(
		 "index.cgi?folder=$in{'folder'}&start=$in{'start'}",
		 $text{'mail_return'});
	return;
	}
else {
	# Replying or forwarding
	if ($in{'mailforward'} ne '') {
		# Forwarding multiple .. get the messages
		@mailforwardids = split(/\0/, $in{'mailforward'});
		@fwdmail = &mailbox_select_mails($folder, \@mailforwardids, 0);
		@fwdmail || &error($text{'reply_efwdnone'});
		$mail = $fwdmail[0];
		}
	else {
		# Replying or forwarding one .. get it
		$mail = &mailbox_get_mail($folder, $in{'id'}, 0);
		$mail || &error($text{'view_egone'});
		&decode_and_sub();
		}
	$viewlink = "view_mail.cgi?id=".&urlize($in{'id'}).
		    "&folder=$in{'folder'}";
	$mail || &error($text{'mail_eexists'});

	# Find the body parts
	($textbody, $htmlbody, $body) =
		&find_body($mail, $userconfig{'view_html'});

	if ($in{'delete'}) {
		# Just delete the email
		if (!$in{'confirm'} && &need_delete_warn($folder)) {
			# Need to ask for confirmation before deleting
			&mail_page_header($text{'confirm_title'});
			print &ui_confirmation_form(
				"reply_mail.cgi",
				$text{'confirm_warn3'}."<br>".
				($userconfig{'delete_warn'} ne 'y' ?
					$text{'confirm_warn2'}."<p>" :
				 $folder->{'type'} == 0 ?
					$text{'confirm_warn4'}."<p>" : ""),
				[ &inputs_to_hiddens(\%in) ],
                                [ [ 'confirm', $text{'confirm_ok'} ] ],
                                );
			&mail_page_footer(
				$viewlink,
				$text{'view_return'},
				"index.cgi?folder=$in{'folder'}",
				$text{'index'});
			exit;
			}
		&lock_folder($folder);
		&mailbox_delete_mail($folder, $mail);
		&unlock_folder($folder);
		&pop3_logout_all();
		&redirect_to_previous();
		exit;
		}
	elsif ($in{'print'}) {
		# Show email in format suitable for printing
		&ui_print_header(undef, &decode_mimewords(
					$mail->{'header'}->{'subject'}));
		&show_mail_printable($mail, $body, $textbody, $htmlbody);
		print "<script>window.print();</script>\n";
		&ui_print_footer();
		exit;
		}
	elsif ($in{'markas0'} || $in{'markas1'} || $in{'markas2'}) {
		# Just mark the message as read/special
		$oldread = &get_mail_read($folder, $mail);
		$mark = $in{'markas0'} ? 0 : $in{'markas1'} ? 1 : 2;
		&set_mail_read($folder, $mail, ($oldread&4)+$mark);
		&redirect_to_previous(1);
		exit;
		}
	elsif ($in{'move1'} || $in{'move2'}) {
		# Move to another folder
		&error_setup($text{'reply_errm'});
		$mfolder = $folders[$in{'move1'} ? $in{'mfolder1'} : $in{'mfolder2'}];
		$mfolder->{'noadd'} && &error($text{'delete_enoadd'});
		&lock_folder($folder);
		&lock_folder($mfolder);
		&mailbox_move_mail($folder, $mfolder, $mail);
		&unlock_folder($mfolder);
		&unlock_folder($folder);
		&redirect_to_previous();
		exit;
		}
	elsif ($in{'copy1'} || $in{'copy2'}) {
		# Copy to another folder
		&error_setup($text{'reply_errc'});
		$mfolder = $folders[$in{'copy1'} ? $in{'mfolder1'} : $in{'mfolder2'}];
		$qerr = &would_exceed_quota($mfolder, $mail);
		&error($qerr) if ($qerr);
		&lock_folder($folder);
		&lock_folder($mfolder);
		&mailbox_copy_mail($folder, $mfolder, $mail);
		&unlock_folder($mfolder);
		&unlock_folder($folder);
		&redirect_to_previous();
		exit;
		}
	elsif ($in{'detach'} && $config{'server_attach'} == 2) {
		# Detach some attachment to a directory on the server
		&error_setup($text{'detach_err'});
		$in{'dir'} || &error($text{'detach_edir'});
		$in{'dir'} = "$remote_user_info[7]/$in{'dir'}"
			if ($in{'dir'} !~ /^\//);

		if ($in{'attach'} eq '*') {
			# Detaching all attachments (except the body and any
			# signature) under their filenames
			@dattach = grep { $_->{'idx'} ne $in{'bindex'} &&
					  $_->{'header'}->{'content-type'} !~
					  	/^multipart\//i }
					@{$mail->{'attach'}};
			if (defined($in{'sindex'})) {
				@dattach = grep { $_->{'idx'} ne $in{'sindex'} }
						@dattach;
				}
			}
		else {
			# Just one attachment
			@dattach = ( $mail->{'attach'}->[$in{'attach'}] );
			}

		local @paths;
		foreach $attach (@dattach) {
			local $path;
			if (-d $in{'dir'}) {
				# Just write to the filename in the directory
				local $fn;
				if ($attach->{'filename'}) {
					$fn = &decode_mimewords(
						$attach->{'filename'});
					$fn =~ s/^.*[\/\\]//;
					}
				else {
					$attach->{'type'} =~ /\/(\S+)$/;
					$fn = "file.$1";
					}
				$path = "$in{'dir'}/$fn";
				}
			else {
				# Assume a full path was given
				$path = $in{'dir'};
				}
			push(@paths, $path);
			}

		for($i=0; $i<@dattach; $i++) {
			# Try to write the files
			open(FILE, ">$paths[$i]") ||
				&error(&text('detach_eopen',
					     "<tt>$paths[$i]</tt>", $!));
			(print FILE $dattach[$i]->{'data'}) ||
				&error(&text('detach_ewrite',
					     "<tt>$paths[$i]</tt>", $!));
			close(FILE) ||
				&error(&text('detach_ewrite',
					     "<tt>$paths[$i]</tt>", $!));
			}

		# Show a message about the new files
		&mail_page_header($text{'detach_title'});

		for($i=0; $i<@dattach; $i++) {
			local $sz = (int(length($dattach[$i]->{'data'}) /
					 1000)+1)." Kb";
			print "<p>",&text('detach_ok',
					  "<tt>$paths[$i]</tt>", $sz),"<p>\n";
			}

		&mail_page_footer(
			$viewlink, $text{'view_return'},
			"index.cgi?folder=$in{'folder'}", $text{'mail_return'});
		exit;
		}
	elsif ($in{'black'} || $in{'white'}) {
		# Add sender to SpamAssassin black/write list, and tell user
		$mode = $in{'black'} ? "black" : "white";
		&mail_page_header($text{$mode.'_title'});

		&foreign_require("spam", "spam-lib.pl");
		local $conf = &spam::get_config();
		local @from = map { @{$_->{'words'}} }
			    	  &spam::find($mode."list_from", $conf);
		local %already = map { $_, 1 } @from;
		local ($spamfrom) = &address_parts($mail->{'header'}->{'from'});
		if ($already{$spamfrom}) {
			print &text($mode.'_already',
					  "<tt>$spamfrom</tt>"),"</b><p>\n";
			}
		else {
			push(@from, $spamfrom);
			&spam::save_directives($conf, $mode.'list_from',
					       \@from, 1);
			&flush_file_lines();
			print &text($mode.'_done',
					  "<tt>$spamfrom</tt>"),"</b><p>\n";
			}

		# Also move message to inbox
		$inbox = &get_spam_inbox_folder();
		if ($userconfig{'white_move'} && $folder->{'spam'} &&
		    $in{'white'}) {
			&mailbox_move_mail($folder, $inbox, $mail);
			&mail_page_footer(
				"index.cgi?folder=$in{'folder'}",
				  $text{'mail_return'});
			}
		else {
			&mail_page_footer(
				$viewlink, $text{'view_return'},
				"index.cgi?folder=$in{'folder'}",
				  $text{'mail_return'});
			}
		exit;
		}
	elsif ($in{'razor'} || $in{'ham'}) {
		# Report message to Razor as spam/ham and tell user
		$mode = $in{'razor'} ? "razor" : "ham";
		&mail_page_header($text{$mode.'_title'});

		print "<b>",$text{$mode.'_report'},"</b>\n";
		print "<pre>";
		local $temp = &transname();
		&send_mail($mail, $temp, 0, 1);

		if ($userconfig{'spam_del'} && $mode eq "razor") {
			# Delete message too
			&lock_folder($folder);
			&mailbox_delete_mail($folder, $mail);
			&unlock_folder($folder);
			}

		local $cmd = $mode eq "razor" ? &spam_report_cmd() 
					      : &ham_report_cmd();
		open(OUT, "$cmd <$temp 2>&1 |");
		local $error;
		while(<OUT>) {
			print &html_escape($_);
			$error++ if (/failed/i);
			}
		close(OUT);
		unlink($temp);
		print "</pre>\n";
		$deleted = 0;
		if ($? || $error) {
			print "<b>",$text{'razor_err'},"</b><p>\n";
			}
		else {
			if ($userconfig{'spam_del'} && $mode eq "razor") {
				# Delete message too
				print "<b>$text{'razor_deleted'}</b><p>\n";
				$deleted = 1;
				$loc = "index.cgi?folder=$in{'folder'}";
				}
			elsif ($userconfig{'ham_move'} &&
			       $folder->{'spam'} && $in{'ham'}) {
				# Move mail to inbox and tell user
				&mailbox_move_mail($folder, $inbox, $mail);
				print "<b>",&text('razor_moved',
						  $inbox->{'name'}),"</b><p>\n";
				$deleted = 1;
				$loc = "index.cgi?folder=$in{'folder'}";
				}
			else {
				# Tell user it was done 
				print "<b>",$text{'razor_done'},"</b><p>\n";
				$loc = $viewlink;
				}
			print "<script>\n";
			print "window.location = '$loc';\n";
			print "</script>\n";
			}

		&mail_page_footer(
			$deleted ? ( ) : 
			( $viewlink, $text{'view_return'} ),
			"index.cgi?folder=$in{'folder'}",
			 $text{'mail_return'});
		exit;
		}
	elsif ($in{'dsn'}) {
		# Send DSN to sender
		dbmopen(%dsn, "$user_module_config_directory/dsn", 0600);
		$dsnaddr = &send_delivery_notification($mail, undef, 1);
		if ($dsnaddr) {
			$mid = $mail->{'header'}->{'message-id'};
                        $dsn{$mid} = time()." ".$dsnaddr;
                        }
		dbmclose(%dsn);
		&redirect_to_previous();
		exit;
		}

	# Get the forwarded message and its attachments
	if (!@fwdmail) {
		&parse_mail($mail);
		&decrypt_attachments($mail);
		@attach = @{$mail->{'attach'}};
		}


	if ($in{'enew'}) {
		# Editing an existing message, so keep same fields
		$to = $mail->{'header'}->{'to'};
		$rto = $mail->{'header'}->{'reply-to'};
		$from = &decode_mimewords($mail->{'header'}->{'from'});
		$cc = $mail->{'header'}->{'cc'};
		$bcc = $mail->{'header'}->{'bcc'};
		$ouser = $1 if ($from =~ /^(\S+)\@/);
		}
	else {
		if (!$in{'forward'} && !@fwdmail) {
			# Replying to a message, so set To: field
			$to = $mail->{'header'}->{'reply-to'};
			$to = $mail->{'header'}->{'from'} if (!$to);
			}
		if ($in{'ereply'}) {
			# Replying to our own sent email - to should be
			# original to
			$to = $mail->{'header'}->{'to'};
			}
		elsif ($in{'erall'}) {
			# Replying to all of our own email - set to and cc
			$to = $mail->{'header'}->{'to'};
			$cc = $mail->{'header'}->{'cc'};
			$bcc = $mail->{'header'}->{'bcc'};
			}
		elsif ($in{'rall'}) {
			# If replying to all, add any addresses in the original
			# To: or Cc: to our new Cc: address.
			$cc = $mail->{'header'}->{'to'};
			$cc .= ", ".$mail->{'header'}->{'cc'}
				if ($mail->{'header'}->{'cc'});
			}
		}

	# Convert MIMEwords in headers to 8 bit for display
	$to = &decode_mimewords($to);
	$rto = &decode_mimewords($rto);
	$cc = &decode_mimewords($cc);
	$bcc = &decode_mimewords($bcc);

	# Remove our own emails from to/cc addresses
	if (($in{'rall'} || $in{'erall'}) && !$in{'enew'} &&
	    !$userconfig{'reply_self'}) {
		$to = &remove_own_email($to);
		$cc = &remove_own_email($cc);
		$bcc = &remove_own_email($bcc);
		}

	# Work out new subject, depending on whether we are replying
	# our forwarding a message (or neither)
	local $qu = !$in{'enew'} &&
		    (!$in{'forward'} || !$userconfig{'fwd_mode'});
	$subject = &decode_mimewords($mail->{'header'}->{'subject'});
	$subject = "Re: ".$subject if ($subject !~ /^Re/i && !$in{'forward'} &&
				       !@fwdmail && !$in{'enew'});
	$subject = "Fwd: ".$subject if ($subject !~ /^Fwd/i &&
					($in{'forward'} || @fwdmail));

	# Remove signature
	&check_signature_attachments($mail->{'attach'}, $textbody);

	# Construct the initial mail text
	$sig = &get_signature();
	($quote, $html_edit, $body) = &quoted_message($mail, $qu, $sig,
						      $in{'body'});

	# Don't include the original body as an attachment
	@attach = &remove_body_attachments($mail, \@attach);
	if (!$in{'forward'} && !$in{'enew'}) {
		# When replying, lose non-cid attachments
		@attach = grep { $_->{'header'}->{'content-id'} ||
				 $_->{'header'}->{'content-location'} } @attach;
		}

	# For a HTML reply or forward, fix up the cid: to refer to attachments
	# in the original message.
	if ($html_edit) {
		$qmid = &urlize($mail->{'id'});
		$quote = &fix_cids($quote, \@attach,
			"detach.cgi?id=$qmid&folder=$in{'folder'}$subs");
		}

	&mail_page_header(
		$in{'forward'} || @fwdmail ? $text{'forward_title'} :
		$in{'enew'} ? $text{'enew_title'} :
			      $text{'reply_title'},
		undef,
		$html_edit ? "onload='initEditor()'" : "");
	}

# Script to validate fields
$noto_msg = &quote_escape($text{'send_etomsg'}, '"');
$nosubject_msg = &quote_escape($text{'send_esubjectmsg'}, '"');
print <<EOF;
<script>
function check_fields()
{
form = document.forms[0];
if (form.to.value == '' && form.cc.value == '' && form.bcc.value == '' &&
    !form.draft_clicked) {
	alert("$noto_msg");
	return false;
	}
if (form.subject.value == '' && !form.draft_clicked) {
	if (!confirm("$nosubject_msg")) {
		return false;
		}
	}
return true;
}
</script>
EOF

# Show form start, with upload progress tracker hook
$upid = time().$$;
$onsubmit = &read_parse_mime_javascript($upid, [ map { "attach$_" } (0..10) ]);
$onsubmit =~ s/='/='ok = check_fields(); if (!ok) { return false; } /;
print &ui_form_start("send_mail.cgi?id=$upid", "form-data", undef, $onsubmit);

# Output various hidden fields
print &ui_hidden("ouser", $ouser);
print &ui_hidden("id", $in{'id'});
print &ui_hidden("folder", $in{'folder'});
print &ui_hidden("start", $in{'start'});
print &ui_hidden("new", $in{'new'});
print &ui_hidden("enew", $in{'enew'});
foreach $s (@sub) {
	print &ui_hidden("sub", $s);
	}
if ($in{'reply'} || $in{'rall'} || $in{'ereply'} || $in{'erall'}) {
	# Message ID and usermin ID being replied to
	print &ui_hidden("rid", $mail->{'header'}->{'message-id'});
	print &ui_hidden("replyid", $mail->{'id'});
	}

# Start tabs for from / to / cc / bcc / signing / options
# Subject is separate
print &ui_table_start($text{'reply_headers'}, "width=100%", 2);
if (&has_command("gpg") && &foreign_check("gnupg")) {
	&foreign_require("gnupg", "gnupg-lib.pl");
	@keys = &gnupg::list_keys_sorted();
	$has_gpg = @keys ? 1 : 0;
	}
@tds = ( "width=10%", "width=90% nowrap" );
@tabs = ( [ "from", $text{'reply_tabfrom'} ],
	  $userconfig{'reply_to'} ne 'x' ?
		( [ "rto", $text{'reply_tabreplyto'} ] ) : ( ),
	  [ "to", $text{'reply_tabto'} ],
	  [ "cc", $text{'reply_tabcc'} ],
	  [ "bcc", $text{'reply_tabbcc'} ],
	  $has_gpg ? ( [ "signing", $text{'reply_tabsigning'} ] ) : ( ),
	  [ "options", $text{'reply_taboptions'} ] );
print &ui_table_row(undef, &ui_tabs_start(\@tabs, "tab", "to", 0), 2);

# From address tab
if ($from) {
	# Got From address
	@froms = ( $from );
	}
else {
	# Work out From: address
	local ($froms, $doms) = &list_from_addresses();
	@froms = @$froms;
	}

@faddrs = grep { $_->[3] } &list_addresses();
($defaddr) = grep { $_->[3] == 2 } @faddrs;
if ($folder->{'fromaddr'}) {
	# Folder has a specified From: address
	($defaddr) = &split_addresses($folder->{'fromaddr'});
	}
if ($config{'edit_from'} == 1) {
	# User can enter any from address he wants
	if ($defaddr) {
		# Address book contains a default from address
		$froms[0] = $defaddr->[1] ? "\"$defaddr->[1]\" <$defaddr->[0]>"
					  : $defaddr->[0];
		}
	$frominput = &ui_address_field("from", $froms[0], 1, 0);
	}
elsif ($config{'edit_from'} == 2) {
	# Only the real name and username part is editable
	local ($real, $user, $dom);
	local ($sp) = $defaddr || &split_addresses($froms[0]);
	$real = $sp->[1];
	if ($sp->[0] =~ /^(\S+)\@(\S+)$/) {
		$user = $1; $dom = $2;
		}
	else {
		$user = $sp->[0];
		}
	$frominput = &ui_textbox("real", $real, 15)."\n".
		     "&lt;".&ui_textbox("user", $user, 10)."\@";
	if (@$doms > 1) {
		$frominput .= &ui_select("dom", undef,
				[ map { [ $_ ] } @$doms ])."&gt;";
		}
	else {
		$frominput .= "$dom&gt;".
			      &ui_hidden("dom", $dom);
		}
	$frominput .= &address_button("user", 0, 2, "real") if (@faddrs);
	}
else {
	# A fixed From address, or a choice of fixed options
	if (@froms > 1) {
		$frominput = &ui_select("from", undef,
				[ map { [ $_, &html_escape($_) ] } @froms ]);
		}
	else {
		$frominput = "<tt>".&html_escape($froms[0])."</tt>".
			     &ui_hidden("from", $froms[0]);
		}
	}
print &ui_tabs_start_tabletab("tab", "from");
print &ui_table_row($text{'mail_from'}, $frominput, 1, \@tds);
print &ui_tabs_end_tabletab();

# Show the Reply-To field
if ($userconfig{'reply_to'} ne 'x') {
	$rto = $userconfig{'reply_to'} if ($userconfig{'reply_to'} ne '*');
	print &ui_tabs_start_tabletab("tab", "rto");
	print &ui_table_row($text{'mail_replyto'},
			    &ui_address_field("replyto", $rto, 1, 0), 1, \@tds);
	print &ui_tabs_end_tabletab();
	}

# Show To: field
print &ui_tabs_start_tabletab("tab", "to");
print &ui_table_row($text{'mail_to'}, &ui_address_field("to", $to, 0, 1),
		    1, \@tds);
print &ui_tabs_end_tabletab();

# Show Cc: field
print &ui_tabs_start_tabletab("tab", "cc");
print &ui_table_row($text{'mail_cc'}, &ui_address_field("cc", $cc, 0, 1),
		    1, \@tds);
print &ui_tabs_end_tabletab();

# Show Bcc: field
$bcc ||= $userconfig{'bcc_to'};
print &ui_tabs_start_tabletab("tab", "bcc");
print &ui_table_row($text{'mail_bcc'}, &ui_address_field("bcc", $bcc, 0, 1),
		    1, \@tds);
print &ui_tabs_end_tabletab();

# Ask for signing and encryption
if ($has_gpg) {
	print &ui_tabs_start_tabletab("tab", "signing");
	@signs = ( );
	foreach $k (@keys) {
		local $n = $k->{'name'}->[0];
		$n = substr($n, 0, 40)."..." if (length($n) > 40);
		if ($k->{'secret'}) {
			push(@signs, [ $k->{'index'}, $n ]);
			}
		push(@crypts, [ $k->{'index'}, $n ]);
		}
	print &ui_table_row($text{'mail_sign'},
		&ui_select("sign", "", 
		   [ [ "", $text{'mail_nosign'} ], @signs ]), 1, \@tds);
	print &ui_table_row($text{'mail_crypt'},
		&ui_select("crypt", "",
		   [ [ "", $text{'mail_nocrypt'} ],
		     [ -1, $text{'mail_samecrypt'} ], @crypts ]), 1, \@tds);
	print &ui_tabs_end_tabletab();
	}

# Show tab for options
print &ui_tabs_start_tabletab("tab", "options");
print &ui_table_row($text{'mail_pri'},
		&ui_select("pri", "",
			[ [ 1, $text{'mail_highest'} ],
			  [ 2, $text{'mail_high'} ],
			  [ "", $text{'mail_normal'} ],
			  [ 4, $text{'mail_low'} ],
			  [ 5, $text{'mail_lowest'} ] ]), 1, \@tds);

if ($userconfig{'req_dsn'} == 2) {
	# Ask for a disposition (read) status
	print &ui_table_row($text{'reply_dsn'},
		&ui_radio("dsn", 0, [ [ 1, $text{'yes'} ],
				      [ 0, $text{'no'} ] ]), 1, \@tds);
	}

if ($userconfig{'req_del'} == 2) {
	# Ask for a delivery status
	print &ui_table_row($text{'reply_del'},
		&ui_radio("del", 0, [ [ 1, $text{'yes'} ],
				      [ 0, $text{'no'} ] ]), 1, \@tds);
	}

# Ask if should add to address book
print &ui_table_row(" ",
    &ui_checkbox("abook", 1, $text{'reply_aboot'}, $userconfig{'add_abook'}),
    1, \@tds);
print &ui_tabs_end_tabletab();

print &ui_table_row(undef, &ui_tabs_end());

# Field for subject is always at the bottom
if ($userconfig{'send_buttons'}) {
	print &ui_table_row($text{'mail_subject'},
		&ui_textbox("subject", $subject, 40, 0, undef,
			    "style='width:60%'").
		&ui_submit($text{'reply_send'}).
		&ui_submit($text{'reply_draft'}, "draft", undef,
			   "onClick='form.draft_clicked = 1'").
		&ui_submit($text{'reply_save'}, "save", undef,
			   "onClick='form.draft_clicked = 1'"),
		1, \@tds);
	}
else {
	# Subject only
	print &ui_table_row($text{'mail_subject'},
		&ui_textbox("subject", $subject, 40, 0, undef,
			    "style='width:95%'"), 1, \@tds);
	}
print &ui_table_end();

# Create link for switching to HTML/text mode for new mail
@bodylinks = ( );
if ($in{'new'}) {
	if ($html_edit) {
		push(@bodylinks, "<a href='reply_mail.cgi?folder=$in{'folder'}&new=1&html=0'>$text{'reply_html0'}</a>");
		}
	else {
		push(@bodylinks, "<a href='reply_mail.cgi?folder=$in{'folder'}&new=1&html=1'>$text{'reply_html1'}</a>");
		}
	}

# Output message body input
print &ui_table_start($text{'reply_body'}, "width=100%", 2, undef,
		      &ui_links_row(\@bodylinks));
if ($html_edit) {
	# Output HTML editor textarea
	print <<EOF;
<script type="text/javascript">
  _editor_url = "$gconfig{'webprefix'}/$module_name/xinha/";
  _editor_lang = "en";
</script>
<script type="text/javascript" src="xinha/htmlarea.js"></script>

<script type="text/javascript">
var editor = null;
function initEditor() {
  editor = new HTMLArea("body");
  editor.generate();
  return false;
}
</script>
EOF
	print &ui_table_row(undef,
		&ui_textarea("body", $quote, 20, 80, undef, 0,
		  	     "style='width:100%' id=body"), 2);
	}
else {
	# Show text editing area
	$wm = $config{'wrap_mode'};
	$wm =~ s/^wrap=//g;
	$wcols = $userconfig{'wrap_compose'};
	print &ui_table_row(undef,
		&ui_textarea("body", $quote, 20,
			     $wcols || 80,
			     $wcols ? "hard" : "",
			     0,
			     $wcols ? "" : "style='width:100%'"), 2);
	}
if (&has_command("ispell") && !$userconfig{'nospell'}) {
	print &ui_table_row(undef,
	      &ui_checkbox("spell", 1, $text{'reply_spell'},
			   $userconfig{'spell_check'}), 2);
	}
print &ui_table_end();
print &ui_hidden("html_edit", $html_edit);

# Display forwarded attachments
$viewurl = "view_mail.cgi?id=".&urlize($in{'id'}).
	   "&folder=$folder->{'index'}$subs";
$detachurl = "detach.cgi?id=".&urlize($in{'id'}).
	     "&folder=$folder->{'index'}$subs";
$mailurl = "view_mail.cgi?folder=$folder->{'index'}$subs";
if (@attach) {
	&attachments_table(\@attach, $folder, $viewurl, $detachurl,
			   $mailurl, 'id', "forward");
	}

# Display forwarded mails
if (@fwdmail) {
	&attachments_table(\@fwdmail, $folder, $viewurl, $detachurl,
			   $mailurl, 'id', undef);
	foreach $fwdid (@mailforwardids) {
		print &ui_hidden("mailforward", $fwdid);
		}
	}

# Display new attachment fields
&show_attachments_fields($userconfig{'def_attach'}, $config{'server_attach'});

print &ui_form_end([ [ "send", $text{'reply_send'} ],
		     [ "draft", $text{'reply_draft'}, undef, undef,
		       "onClick='form.draft_clicked = 1'" ],
		     [ "save", $text{'reply_save'}, undef, undef,
		       "onClick='form.draft_clicked = 1'" ],
		   ]);

&mail_page_footer("index.cgi?folder=$in{'folder'}&start=$in{'start'}",
		  $text{'mail_return'});
&pop3_logout_all();

sub decode_and_sub
{
return if (!$mail);
&parse_mail($mail);
@sub = split(/\0/, $in{'sub'});
$subs = join("", map { "&sub=$_" } @sub);
foreach $s (@sub) {
	# We are looking at a mail within a mail ..
	&decrypt_attachments($mail);
	local $amail = &extract_mail(
			$mail->{'attach'}->[$s]->{'data'});
	&parse_mail($amail);
	$mail = $amail;
	}
($deccode, $decmessage) = &decrypt_attachments($mail);
}

sub redirect_to_previous
{
local ($refresh) = @_;
$refresh = time().$$ if ($refresh);
local $perpage = $folder->{'perpage'} || $userconfig{'perpage'};
local $s = int($mail->{'sortidx'} / $perpage) * $perpage;
if ($userconfig{'open_mode'}) {
	&redirect($viewlink);
	}
else {
	&redirect("index.cgi?folder=$in{'folder'}&start=$s&refresh=$refresh");
	}
}

