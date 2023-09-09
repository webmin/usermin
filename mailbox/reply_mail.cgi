#!/usr/local/bin/perl
# Display a form for replying to or composing an email
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in, %config, %gconfig, %userconfig);
our $module_name;
our @remote_user_info;
our $user_module_config_directory;
our $current_theme;

require './mailbox-lib.pl';
require '../html-editor-lib.pl';

&ReadParse();
&set_module_index($in{'folder'});
my @folders = &list_folders();
my $folder = $folders[$in{'folder'}];

# XXX Egads, this is hairy!
my $html_edit;
my $quote;
my ($to, $from, $rto, $cc, $bcc, $replyfrom, $sig);
my @replyfrom;
my @mailforwardids;
my @fwdmail;
my $mail;
my $viewlink;
my $mode;
my ($subject, $textbody, $htmlbody, $body);
my (@attach, @dattach);
my $deleted;
my $inbox;
my $ouser;
my $subs; # XXX Very hairy!
my @sub;
if ($in{'new'}) {
	# Composing a new email
	if (defined($in{'html'})) {
		$html_edit = $in{'html'};
		}
	else {
		$html_edit = $userconfig{'html_edit'} == 2 ? 1 : 0;
		}
	my $sig = &get_signature();
	if ($html_edit && $sig) {
		$sig =~ s/\n/<br>\n/g;
		$quote = "<html><body>$sig</body></html>";
		}
	else {
		$quote = "\n\n$sig" if ($sig);
		}
	$to = $in{'to'};
	if ($userconfig{'charset'}) {
		# Force this charset for compose
		$main::force_charset = $userconfig{'charset'};
		}
	else {
		$main::force_charset = &get_charset();
		}
	&mail_page_header($text{'compose_title'});
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

	# Find the body parts and set the character set
	($textbody, $htmlbody, $body) =
		&find_body($mail, $userconfig{'view_html'});
	my $mail_charset = &get_mail_charset($mail, $body);
	if (&get_charset() eq 'UTF-8' &&
	    &can_convert_to_utf8(undef, $mail_charset)) {
		# Convert to UTF-8
		$body->{'data'} = &convert_to_utf8($body->{'data'},
						   $mail_charset);
		$main::force_charset = 'UTF-8';
		}
	else {
		# Set the character set for the page to match email
		$main::force_charset = $mail_charset;
		}

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
	elsif ($in{'markas0'} || $in{'markas1'} || $in{'markas2'}) {
		# Just mark the message as read/special
		my $oldread = &get_mail_read($folder, $mail);
		my $mark = $in{'markas0'} ? 0 : $in{'markas1'} ? 1 : 2;
		&set_mail_read($folder, $mail, ($oldread&4)+$mark);
		&redirect_to_previous(1);
		exit;
		}
	elsif ($in{'move1'} || $in{'move2'}) {
		# Move to another folder
		&error_setup($text{'reply_errm'});
		my $mfolder = $folders[$in{'move1'} ? $in{'mfolder1'} : $in{'mfolder2'}];
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
		my $mfolder = $folders[$in{'copy1'} ? $in{'mfolder1'} : $in{'mfolder2'}];
		my $qerr = &would_exceed_quota($mfolder, $mail);
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

		my @paths;
		foreach my $attach (@dattach) {
			my $path;
			if (-d $in{'dir'}) {
				# Just write to the filename in the directory
				my $fn;
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

		for(my $i=0; $i<@dattach; $i++) {
			# Try to write the files
			open(my $FILE, ">", "$paths[$i]") ||
				&error(&text('detach_eopen',
					     "<tt>$paths[$i]</tt>", $!));
			(print $FILE $dattach[$i]->{'data'}) ||
				&error(&text('detach_ewrite',
					     "<tt>$paths[$i]</tt>", $!));
			close($FILE) ||
				&error(&text('detach_ewrite',
					     "<tt>$paths[$i]</tt>", $!));
			}

		# Show a message about the new files
		&mail_page_header($text{'detach_title'});

		for(my $i=0; $i<@dattach; $i++) {
			my $sz = (int(length($dattach[$i]->{'data'}) /
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
		my $conf = &spam::get_config();
		my @from = map { @{$_->{'words'}} }
			    	  &spam::find($mode."list_from", $conf);
		my %already = map { $_, 1 } @from;
		my ($spamfrom) = &address_parts($mail->{'header'}->{'from'});
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
				"index.cgi?folder=$in{'folder'}&".
				"start=$in{'start'}",
				  $text{'mail_return'});
			}
		else {
			&mail_page_footer(
				$viewlink, $text{'view_return'},
				"index.cgi?folder=$in{'folder'}&".
				"start=$in{'start'}",
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
		my $temp = &transname();
		&send_mail($mail, $temp, 0, 1);

		if ($userconfig{'spam_del'} && $mode eq "razor") {
			# Delete message too
			&lock_folder($folder);
			&mailbox_delete_mail($folder, $mail);
			&unlock_folder($folder);
			}

		my $cmd = $mode eq "razor" ? &spam_report_cmd()
					   : &ham_report_cmd();
		open(my $OUT, "$cmd <$temp 2>&1 |");
		my $error;
		while(<$OUT>) {
			print &html_escape($_);
			$error++ if (/failed/i);
			}
		close($OUT);
		unlink($temp);
		print "</pre>\n";
		$deleted = 0;
		my $loc;
		if ($? || $error) {
			print "<b>",$text{'razor_err'},"</b><p>\n";
			}
		else {
			$inbox = &get_spam_inbox_folder();
			if ($userconfig{'spam_del'} && $mode eq "razor") {
				# Delete message too
				print "<b>$text{'razor_deleted'}</b><p>\n";
				$deleted = 1;
				$loc = "index.cgi?folder=$in{'folder'}";
				}
			elsif ($userconfig{'ham_move'} &&
			       $folder->{'spam'} && $in{'ham'}) {
				# Move mail to inbox and tell user
				if (&remove_spam_subject($mail)) {
					&mailbox_modify_mail(
						$mail, $mail, $folder);
					}
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
			}

		&mail_page_footer(
			$deleted ? ( ) :
			( $viewlink, $text{'view_return'} ),
			"index.cgi?folder=$in{'folder'}&start=$in{'start'}",
			 $text{'mail_return'});
		exit;
		}
	elsif ($in{'dsn'}) {
		# Send DSN to sender
		my %dsn;
		&open_dbm_db(\%dsn, "$user_module_config_directory/dsn", 0600);
		my $dsnaddr = &send_delivery_notification($mail, undef, 1);
		if ($dsnaddr) {
			my $mid = $mail->{'header'}->{'message-id'};
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
			$replyfrom = $mail->{'header'}->{'to'};
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

	# If replying, work out address it was sent to - this can be later used
	# as the from address
	if ($replyfrom) {
		$replyfrom = &decode_mimewords($replyfrom);
		@replyfrom = &split_addresses($replyfrom);
		$replyfrom = @replyfrom ? $replyfrom[0]->[0] : undef;
		}

	# Remove our own emails from to/cc addresses
	if (($in{'rall'} || $in{'erall'}) && !$in{'enew'} &&
	    !$userconfig{'reply_self'}) {
		$to = &remove_own_email($to);
		$cc = &remove_own_email($cc);
		$bcc = &remove_own_email($bcc);
		}

	# Work out new subject, depending on whether we are replying
	# our forwarding a message (or neither)
	my $qu = !$in{'enew'} &&
		    (!$in{'forward'} || !$userconfig{'fwd_mode'});
	$subject = &convert_header_for_display($mail->{'header'}->{'subject'},
					       undef, 1);
	$subject = "Re: ".$subject if ($subject !~ /^Re:/i && !$in{'forward'} &&
				       !@fwdmail && !$in{'enew'});
	$subject = "Fwd: ".$subject if ($subject !~ /^Fwd:/i &&
					($in{'forward'} || @fwdmail));

	# Remove signature
	&check_signature_attachments($mail->{'attach'}, $textbody);

	# Construct the initial mail text
	$sig = &get_signature();
	($quote, $html_edit, $body) = &quoted_message(
		$mail, $qu, $sig, $in{'body'}, $userconfig{'sig_mode'});
	# Load images using server in replies
	$quote = &disable_html_images($quote, 3);

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
		my $qmid = &urlize($mail->{'id'});
		$quote = &fix_cids($quote, \@attach,
			"detach.cgi?id=$qmid&folder=$in{'folder'}$subs");
		}

	&mail_page_header(
		$in{'forward'} || @fwdmail ? $text{'forward_title'} :
		$in{'enew'} ? $text{'enew_title'} :
			      $text{'reply_title'});
	}

# Script to validate fields
my $noto_msg = &quote_escape($text{'send_etomsg'}, '"');
my $nosubject_msg = &quote_escape($text{'send_esubjectmsg'}, '"');
my $close_msg = &quote_escape($text{'send_eclosemsg'}, '"');
print <<EOF;
<script>
function check_fields()
{
form = document.forms[0];
window.submit_clicked = true;
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
function prompt_save(event)
{
form = document.forms[0];
if (window.submit_clicked) {
	return null;
	}
if (form.body.value != '' &&
    form.body.value != '<html><body></body></html>') {
	return "$close_msg";
	}
return null;
}
window.onbeforeunload = prompt_save;
window.submit_clicked = false;
</script>
EOF

# Show form start, with upload progress tracker hook
my $upid = time().$$;
my ($froms, $doms); # XXX More globals.
my $onsubmit = &read_parse_mime_javascript($upid, [ map { "attach$_" } (0..10) ]);
$onsubmit =~ s/='/='ok = check_fields(); if (!ok) { return false; } /;
if ($main::force_charset) {
	$onsubmit .= " accept-charset=$main::force_charset";
	}
print &ui_form_start("send_mail.cgi?id=$upid", "form-data", undef, $onsubmit);

# Output various hidden fields
print &ui_hidden("ouser", $ouser);
print &ui_hidden("id", $in{'id'});
print &ui_hidden("folder", $in{'folder'});
print &ui_hidden("start", $in{'start'});
print &ui_hidden("new", $in{'new'});
print &ui_hidden("enew", $in{'enew'});
foreach my $s (@sub) {
	print &ui_hidden("sub", $s);
	}
if ($in{'reply'} || $in{'rall'} || $in{'ereply'} || $in{'erall'}) {
	# Message ID and usermin ID being replied to
	print &ui_hidden("rid", $mail->{'header'}->{'message-id'});
	print &ui_hidden("replyid", $mail->{'id'});
	}
print &ui_hidden("charset", $main::force_charset);

# Start tabs for from / to / cc / bcc / signing / options
# Subject is separate
print &ui_table_start($text{'reply_headers'}, "width=100%", 2);
print "<tbody><tr><td>";
my $has_gpg;
my @keys;
if (&has_command("gpg") && &foreign_check("gnupg") &&
    &foreign_available("gnupg")) {
	&foreign_require("gnupg", "gnupg-lib.pl");
	@keys = &gnupg::list_keys_sorted();
	$has_gpg = @keys ? 1 : 0;
	}
my @tabs = ( [ "from", $text{'reply_tabfrom'} ],
	  $userconfig{'reply_to'} ne 'x' ?
		( [ "rto", $text{'reply_tabreplyto'} ] ) : ( ),
	  [ "to", $text{'reply_tabto'} ],
	  $userconfig{'cc_tabs'} ? ( ) :
		( [ "cc", $text{'reply_tabcc'} ],
		  [ "bcc", $text{'reply_tabbcc'} ] ),
	  $has_gpg ? ( [ "signing", $text{'reply_tabsigning'} ] ) : ( ),
	  [ "options", $text{'reply_taboptions'} ] );
print &ui_tabs_start(\@tabs, "tab", "to", 0);

# From address tab
my @froms;
if ($from) {
	# Got From address already, such as when editing old email
	@froms = ( $from );
	}
else {
	# Work out From: addresses
	($froms, $doms) = &list_from_addresses();
	@froms = @$froms;
	}

# Find preferred From address from addressbook, if set
my @faddrs = grep { $_->[3] } &list_addresses();
my ($defaddr) = grep { $_->[3] == 2 } @faddrs;

# If replying to an email and the original to address is in our addressbook,
# use that as the from address
my $replyaddr;
if ($replyfrom) {
	($replyaddr) = grep { $_->[0] eq $replyfrom } @faddrs;
	$defaddr = $replyaddr if ($replyaddr);
	}

if ($folder->{'fromaddr'}) {
	# Folder has a specified From: address
	($defaddr) = &split_addresses($folder->{'fromaddr'});
	}
my $deffrom;
my $frominput;
if ($config{'edit_from'} == 1) {
	# User can enter any from address he wants
	if ($defaddr) {
		# Address book contains a default from address
		$deffrom = $defaddr->[1] ? "\"$defaddr->[1]\" <$defaddr->[0]>"
					 : $defaddr->[0];
		}
	else {
		$deffrom = $froms[0];
		}
	$frominput = &ui_address_field("from", $deffrom, 1, 0);
	}
elsif ($config{'edit_from'} == 2) {
	# Only the real name and username part is editable
	my ($real, $user, $dom);
	my ($sp) = $defaddr || &split_addresses($froms[0]);
	$real = $sp->[1];
	if ($sp->[0] =~ /^(\S+)\@(\S+)$/) {
		$user = $1; $dom = $2;
		}
	else {
		$user = $sp->[0];
		}
	$frominput = &ui_textbox("real", $real, 15)."\n".
		     "&lt;".&ui_textbox("user", $user, 10)."\@";
	if ($doms && @$doms > 1) {
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
		$deffrom = $froms[0];
		if ($replyfrom) {
			# Use from address from original email if possible
			foreach my $f (@froms) {
				my @f = &split_addresses($f);
				if (@f && $f[0]->[0] eq $replyfrom) {
					$deffrom = $f;
					last;
					}
				}
			}
		$frominput = &ui_select("from", $deffrom,
				[ map { [ $_, &html_escape($_) ] } @froms ]);
		}
	else {
		$frominput = "<tt>".&html_escape($froms[0])."</tt>".
			     &ui_hidden("from", $froms[0]);
		}
	}
print &ui_tabs_start_tab("tab", "from");
print &ui_div_row($text{'mail_from'}, $frominput);
print &ui_tabs_end_tab();

# Show the Reply-To field
if ($userconfig{'reply_to'} ne 'x') {
	$rto = $userconfig{'reply_to'} if ($userconfig{'reply_to'} ne '*');
	print &ui_tabs_start_tab("tab", "rto");
	print &ui_div_row($text{'mail_replyto'},
			    &ui_address_field("replyto", $rto, 1, 0));
	print &ui_tabs_end_tab();
	}

$bcc ||= $userconfig{'bcc_to'};
if ($userconfig{'cc_tabs'}) {
	# Show all address fields in a tab
	print &ui_tabs_start_tab("tab", "to");

	print &ui_div_row($text{'mail_to'}, &ui_address_field("to", $to,
			    0, 1));
	print &ui_div_row($text{'mail_cc'}, &ui_address_field("cc", $cc,
			    0, 1));
	print &ui_div_row($text{'mail_bcc'}, &ui_address_field("bcc", $bcc,
			    0, 1));

	print &ui_tabs_end_tab();
	}
else {
	# Show To: field in a tab
	print &ui_tabs_start_tab("tab", "to");
	print &ui_div_row($text{'mail_to'}, &ui_address_field("to", $to,
			    0, 1));
	print &ui_tabs_end_tab();

	# Show Cc: field in a tab
	print &ui_tabs_start_tab("tab", "cc");
	print &ui_div_row($text{'mail_cc'}, &ui_address_field("cc", $cc,
			    0, 1));
	print &ui_tabs_end_tab();

	# Show Bcc: field in a tab
	print &ui_tabs_start_tab("tab", "bcc");
	print &ui_div_row($text{'mail_bcc'}, &ui_address_field("bcc", $bcc,
			    0, 1));
	print &ui_tabs_end_tab();
	}

# Ask for signing and encryption
if ($has_gpg) {
	print &ui_tabs_start_tab("tab", "signing");
	my @signs;
	my $def_sign = "";
	my @crypts;
	foreach my $k (@keys) {
		my $n = $k->{'name'}->[0];
		$n = substr($n, 0, 40)."..." if (length($n) > 40);
		if ($k->{'email'}->[0]) {
			$n .= " &lt;".$k->{'email'}->[0]."&gt;";
			}
		else {
			$n .= " ($k->{'key'})";
			}
		if ($k->{'secret'}) {
			push(@signs, [ $k->{'index'}, $n ]);
			}
		if ($k->{'secret'} && $userconfig{'def_sign'}) {
			my $def_signer = lc($userconfig{'def_sign'});
			for(my $i=0; $i<@{$k->{'name'}}; $i++) {
				if (lc($k->{'name'}->[$i]) eq $def_signer ||
				    lc($k->{'email'}->[$i]) eq $def_signer) {
					$def_sign = $k->{'index'};
					}
				}
			}
		push(@crypts, [ $k->{'index'}, $n ]);
		}
	print &ui_div_row($text{'mail_sign'},
		&ui_select("sign", $def_sign,
		   [ [ "", $text{'mail_nosign'} ], @signs ]));
	print &ui_div_row($text{'mail_crypt'},
		&ui_select("crypt", $userconfig{'def_crypt'} ? -1 : "",
		   [ [ "", $text{'mail_nocrypt'} ],
		     [ -1, $text{'mail_samecrypt'} ], @crypts ]));
	print &ui_tabs_end_tab();
	}

# Show tab for options
print &ui_tabs_start_tab("tab", "options");
print &ui_div_row($text{'mail_pri'},
		&ui_select("pri", "",
			[ [ 1, $text{'mail_highest'} ],
			  [ 2, $text{'mail_high'} ],
			  [ "", $text{'mail_normal'} ],
			  [ 4, $text{'mail_low'} ],
			  [ 5, $text{'mail_lowest'} ] ]));

if ($userconfig{'req_dsn'} == 2) {
	# Ask for a disposition (read) status
	print &ui_div_row($text{'reply_dsn'},
		&ui_radio("dsn", 0, [ [ 1, $text{'yes'} ],
				      [ 0, $text{'no'} ] ]));
	}

if ($userconfig{'req_del'} == 2) {
	# Ask for a delivery status
	print &ui_div_row($text{'reply_del'},
		&ui_radio("del", 0, [ [ 1, $text{'yes'} ],
				      [ 0, $text{'no'} ] ]));
	}

# Ask if should add to address book
print &ui_div_row(" ",
    &ui_checkbox("abook", 1, $text{'reply_aboot'}, $userconfig{'add_abook'}));
print &ui_tabs_end_tab();

print &ui_tabs_end();

# JS to disable enter in subject field
print <<EOF;
<script type="text/javascript">
function noenter() {
	return !(window.event && window.event.keyCode == 13);
	}
</script>
EOF

# Field for subject is always at the bottom
if ($userconfig{'send_buttons'}) {
	print &ui_div_row($text{'mail_subject'},
		&ui_textbox("subject", $subject, 40, 0, undef,
			    "style='width:50%' onKeyPress='return noenter()'").
		"&nbsp;&nbsp;".&ui_submit($text{'reply_send'}).
		&ui_submit($text{'reply_draft'}, "draft", undef,
			   "onClick='form.draft_clicked = 1'").
		&ui_submit($text{'reply_save'}, "save", undef,
			   "onClick='form.draft_clicked = 1'"));
	}
else {
	# Subject only
	print &ui_div_row($text{'mail_subject'},
		&ui_textbox("subject", $subject, 40, 0, undef,
			    "style='width:90%' onKeyPress='return noenter()'"));
	}
print "</td></tr></tbody>";
print &ui_table_end();

# Create link for switching to HTML/text mode for new mail
my @bodylinks;
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
# Process email quote
my $iframe_quote;
$iframe_quote = &iframe_quote($quote)
	if (!$in{'new'} && !$in{'enew'});
my $draft;
$draft = $quote if ($in{'new'} || $in{'enew'});

if ($html_edit) {
	# Get HTML editor and replies
	my $html_editor = &html_editor(
	      { textarea =>
	          { target => { name => 'body', attr => 'name' },
	            sync =>
	              { position => 'after',
	                data => [ { iframe => '#quote-mail-iframe',
	                            elements => ['#webmin-iframe-quote'] } ] }
	          },
	      	type => $userconfig{'html_edit_mode'} || 'simple',
	        after =>
	           { editor => $iframe_quote }
	      });
	# Output HTML editor textarea
	$sig =~ s/\n/<br>/g,
	$sig =~ s/^\s+//g,
	$sig = "<br><br>$sig<br><br>"
		if ($sig);
	print &ui_table_row(undef,
		&ui_textarea("body", $draft || $sig, 16, 80, undef, 0,
		             "style='display: none' id=body data-html-mode='$userconfig{'html_edit_mode'}'").
		$html_editor, 2);
	}
else {
	# Show text editing area
	my $wm = $config{'wrap_mode'};
	$wm =~ s/^wrap=//g;
	my $wcols = $userconfig{'wrap_compose'};
	print &ui_table_row(undef,
		&ui_textarea("body", "\n".($draft || "\n\n$sig\n\n$quote"), 16,
			     $wcols || 80,
			     $wcols ? "hard" : "",
			     0,
			     $wcols ? "" : "style='width:100%'"), 2);
	}
if (&has_command("ispell") && !$userconfig{'nospellcheck'}) {
	print &ui_table_row(undef,
	      &ui_checkbox("spell", 1, $text{'reply_spell'},
			   $userconfig{'spell_check'}), 2);
	}
print &ui_table_end();
print &ui_hidden("html_edit", $html_edit);
print &ui_hidden("html_edit_config", $userconfig{'html_edit'});

# Display forwarded attachments - but exclude those referenced in the body,
# as they get included automatically
my $viewurl = "view_mail.cgi?id=".&urlize($in{'id'}).
	   "&folder=$folder->{'index'}$subs";
my $detachurl = "detach.cgi?id=".&urlize($in{'id'}).
	     "&folder=$folder->{'index'}$subs";
my $mailurl = "view_mail.cgi?folder=$folder->{'index'}$subs";
my @non_body_attach;
if (@attach) {
	@non_body_attach = &remove_cid_attachments($mail, \@attach);
	}
if (@non_body_attach) {
	&attachments_table(\@non_body_attach, $folder, $viewurl, $detachurl,
			   $mailurl, 'id', "forward");
	}
foreach my $a (@attach) {
	if (&indexof($a, @non_body_attach) < 0) {
		# Body attachment .. always include
		print &ui_hidden("forward", $a->{'idx'});
		}
	}

# Display forwarded mails
if (@fwdmail) {
	&attachments_table(\@fwdmail, $folder, $viewurl, $detachurl,
			   $mailurl, 'id', undef);
	foreach my $fwdid (@mailforwardids) {
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
my ($deccode, $decmessage);
foreach my $s (@sub) {
	# We are looking at a mail within a mail ..
	&decrypt_attachments($mail);
	my $amail = &extract_mail(
			$mail->{'attach'}->[$s]->{'data'});
	&parse_mail($amail);
	$mail = $amail;
	}
($deccode, $decmessage) = &decrypt_attachments($mail);
}

sub redirect_to_previous
{
my ($refresh) = @_;
$refresh = time().$$ if ($refresh);
my $perpage = $folder->{'perpage'} || $userconfig{'perpage'};
my $s = int($mail->{'sortidx'} / $perpage) * $perpage;
if ($userconfig{'open_mode'}) {
	&redirect($viewlink);
	}
else {
	&redirect("index.cgi?folder=$in{'folder'}&start=$s&refresh=$refresh");
	}
}
