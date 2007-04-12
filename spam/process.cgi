#!/usr/local/bin/perl
# process.cgi
# Delete, move or whitelist messages

require './spam-lib.pl';
&foreign_require("mailbox", "mailbox-lib.pl");
$folder = &spam_file_folder();
&disable_indexing($folder);
&ReadParse();

@delete = sort { $a <=> $b } split(/\0/, $in{'d'});
@mail = &mailbox::mailbox_list_mails_sorted($delete[0], $delete[@delete-1],
				     $folder);
foreach $d (@delete) {
	push(@delmail, $mail[$d]);
	}

if ($in{'inbox'} || $in{'whitelist'} || $in{'ham'}) {
	# Move mails to inbox
	@delete || &error($mailbox::text{'delete_emnone'});
	@folders = &mailbox::list_folders();
	($inbox) = grep { $_->{'inbox'} } @folders;
	if ($userconfig{'inbox'}) {
		$mfolder = &mailbox::find_named_folder(
				$userconfig{'inbox'}, \@folders);
		}
	$mfolder ||= $inbox;
	foreach $d (@delete) {
		push(@movemail, $mail[$d]);
		push(@addrs, map { $_->[0] } &mailbox::split_addresses($mail[$d]->{'header'}->{'from'}));
		}

	# Pass through spamassassin to remove headers, then add to Inbox
	&mailbox::lock_folder($mfolder);
	foreach $d (@movemail) {
		local $temp = &transname();
		&mailbox::send_mail($d, $temp);
		local $newmail = &mailbox::read_mail_file("$config{'spamassassin'} -d <$temp |");
		$newmail || &error($text{'process_eclean'});
		&mailbox::write_mail_folder($newmail, $mfolder);
		unlink($temp);
		}
	&mailbox::unlock_folder($mfolder);

	# Delete from spam folder
	&mailbox::lock_folder($folder);
	&mailbox::mailbox_delete_mail($folder, $mfolder, @movemail);
	&mailbox::unlock_folder($folder);
	}
if ($in{'whitelist'}) {
	# Add senders to whitelist
	foreach $d (@delete) {
		push(@addrs, map { $_->[0] } &mailbox::split_addresses($mail[$d]->{'header'}->{'from'}));
		}
	&lock_file($local_cf);
	$conf = &get_config();
	@from = map { @{$_->{'words'}} } &find("whitelist_from", $conf);
	%already = map { $_, 1 } @from;
	@newaddrs = grep { !$already{$_} } &unique(@addrs);
	push(@from, @newaddrs);
	&save_directives($conf, 'whitelist_from', \@from, 1);
	&flush_file_lines();
	&unlock_file($local_cf);
	}
if ($in{'ham'}) {
	# Report to spamassassin as ham
	local $temp = &transname();
	foreach $d (@delmail) {
		&mailbox::send_mail($d, $temp);
		local $out = `$config{'sa_learn'} --ham <$temp 2>&1`;
		unlink($temp);
		if ($? || $out =~ /failed/i) {
			&error(&text('process_ereport',
				     "<pre>$out</pre>"));
			}
		}
	}
if ($in{'delete'} || $in{'razor'}) {
	# Delete messages
	@delete || &error($mailbox::text{'delete_enone'});
	&mailbox::lock_folder($folder);
	&mailbox::mailbox_delete_mail($folder, @delmail);
	&mailbox::unlock_folder($folder);
	}
if ($in{'razor'}) {
	# Report to spamassassin as spam
	local $temp = &transname();
	foreach $d (@delmail) {
		&mailbox::send_mail($d, $temp);
		local $out = `$config{'spamassassin'} -r <$temp 2>&1`;
		unlink($temp);
		if ($? || $out =~ /failed/i) {
			&error(&text('process_ereport',
				     "<pre>$out</pre>"));
			}
		}
	}

&redirect("mail.cgi");

