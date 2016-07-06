#!/usr/local/bin/perl
# delete_mail.cgi
# Delete, mark, move or copy multiple messages
use strict;
use warnings;
our (%text, %in, %userconfig, %gconfig);

require './mailbox-lib.pl';
&ReadParse();
my @ids = sort { $a <=> $b } split(/\0/, $in{'d'});
my @folders = &list_folders();
my $folder = $folders[$in{'folder'}];
my $r = time().$$;

my @delmail;
my $mark; # XXX I think the use of $mark below will never be defined.
if (!$in{'new'}) {
	# Get the messages. We only need the headers when marking, or when
	# deleting unless moving to the trash
	my $headersonly = defined($mark) ||
		       $in{'delete'} && $userconfig{'delete_mode'} != 1;
	@delmail = &mailbox_select_mails($folder, \@ids, $headersonly);
	}

$mark = $in{'markas0'} ? 0 : $in{'markas1'} ? 1 : $in{'markas2'} ? 2 : undef;
if (defined($mark)) {
	# Marking emails with some status
	@ids || &error($text{'delete_emnone'});
	foreach my $mail (@delmail) {
		my $oldread = &get_mail_read($folder, $mail);
		&set_mail_read($folder, $mail, ($oldread&4)+$mark);
		}
	my $perpage = $folder->{'perpage'} || $userconfig{'perpage'};
	&redirect("index.cgi?start=$in{'start'}&folder=$in{'folder'}&refresh=$r");
	}
elsif ($in{'move1'} || $in{'move2'}) {
	# Moving mails to some other folder
	&error_setup($text{'delete_errm'});
	@delmail || &error($text{'delete_emnone'});
	my $mfolder = $folders[$in{'move1'} ? $in{'mfolder1'} : $in{'mfolder2'}];
	$mfolder->{'noadd'} && &error($text{'delete_enoadd'});
	&lock_folder($folder);
	&lock_folder($mfolder);
	&mailbox_move_mail($folder, $mfolder, @delmail);
	&unlock_folder($mfolder);
	&unlock_folder($folder);
	&redirect("index.cgi?start=$in{'start'}&folder=$in{'folder'}&refresh=$r");
	}
elsif ($in{'copy1'} || $in{'copy2'}) {
	# Copying mails to some other folder
	&error_setup($text{'delete_errc'});
	@delmail || &error($text{'delete_emnone'});
	my $cfolder = $folders[$in{'copy1'} ? $in{'mfolder1'} : $in{'mfolder2'}];
	my $qerr = &would_exceed_quota($cfolder, @delmail);
	&error($qerr) if ($qerr);
	&lock_folder($cfolder);
	&mailbox_copy_mail($folder, $cfolder, @delmail);
	&unlock_folder($cfolder);
	&redirect("index.cgi?start=$in{'start'}&folder=$in{'folder'}&refresh=$r");
	}
elsif ($in{'forward'}) {
	# Forwarding selected mails .. redirect
	@delmail || &error($text{'delete_efnone'});
	&redirect("reply_mail.cgi?folder=$in{'folder'}&".
		  join("&", map { "mailforward=".&urlize($_) } @ids));
	}
elsif ($in{'new'}) {
	# Need to redirect to compose form
	&redirect("reply_mail.cgi?new=1&folder=$in{'folder'}");
	}
elsif ($in{'black'} || $in{'white'}) {
	# Deny or allow all senders
	my $dir = $in{'black'} ? "blacklist_from" : "whitelist_from";
	@delmail || &error($in{'black'} ? $text{'delete_ebnone'}
				       : $text{'delete_ewnone'});
	my @addrs;
	foreach my $mail (@delmail) {
		push(@addrs, map { $_->[0] } &split_addresses($mail->{'header'}->{'from'}));
		}
	&foreign_require("spam", "spam-lib.pl");
	my $conf = &spam::get_config();
	my @from = map { @{$_->{'words'}} }
			  &spam::find($dir, $conf);
	my %already = map { $_, 1 } @from;
	my @newaddrs = grep { !$already{$_} && /\@/ } &unique(@addrs);
	push(@from, @newaddrs);
	&spam::save_directives($conf, $dir, \@from, 1);
	&flush_file_lines();

	# Also move messages to inbox
	my $inbox = &get_spam_inbox_folder();
	if ($userconfig{'white_move'} && $folder->{'spam'} && $in{'white'}) {
		&mailbox_move_mail($folder, $inbox, @delmail);
		}
	&redirect("index.cgi?folder=$in{'folder'}");
	}
elsif ($in{'razor'} || $in{'ham'}) {
	# Report as ham or spam all messages
	@delmail || &error($in{'razor'} ? $text{'delete_ebnone'}
				       : $text{'delete_ehnone'});

	&ui_print_header(undef, $in{'razor'} ? $text{'razor_title'}
					     : $text{'razor_title2'}, "");
	if ($in{'razor'}) {
		print "<b>$text{'razor_report2'}</b>\n";
		}
	else {
		print "<b>$text{'razor_report3'}</b>\n";
		}
	print "<pre>";

	# Write all messages to a temp file
	my $temp = &transname();
	my $cmd = $in{'razor'} ? &spam_report_cmd() : &ham_report_cmd();
	foreach my $mail (@delmail) {
		&send_mail($mail, $temp);
		}

	if ($userconfig{'spam_del'} && $in{'razor'}) {
		# Delete spam too
		&lock_folder($folder);
		&mailbox_delete_mail($folder, @delmail);
		&unlock_folder($folder);
		}

	# Call reporting command on them
	no strict "subs";
	&open_execute_command(OUT, "$cmd <$temp 2>&1", 1);
	my $error;
	while(<OUT>) {
		print &html_escape($_);
		$error++ if (/failed/i);
		}
	close(OUT);
	use strict "subs";
	unlink($temp);
	print "</pre>\n";
	if ($? || $error) {
		print "<b>$text{'razor_err'}</b><p>\n";
		}
	else {
		my $inbox = &get_spam_inbox_folder();
		if ($userconfig{'spam_del'} && $in{'razor'}) {
			# Tell user it was deleted
			print "<b>$text{'razor_deleted'}</b><p>\n";
			}
		elsif ($userconfig{'ham_move'} &&
		       $folder->{'spam'} && $in{'ham'}) {
			# Move mail to inbox and tell user
			&mailbox_move_mail($folder, $inbox, @delmail);
			print "<b>",&text('razor_moved', $inbox->{'name'}),
			      "</b><p>\n";
			}
		else {
			# Tell user it was done
			print "<b>$text{'razor_done'}</b><p>\n";
			}
		print "<script>\n";
		print "window.location = 'index.cgi?folder=$in{'folder'}';\n";
		print "</script>\n";
		}
	&ui_print_footer("index.cgi?folder=$in{'folder'}",
			 $text{'mail_return'});
	}
elsif ($in{'delete'}) {
	# Just deleting emails
	@delmail || $in{'all'} || &error($text{'delete_enone'});
	if (!$in{'confirm'} && (&need_delete_warn($folder) || $in{'all'})) {
		# Need to ask for confirmation before deleting
		&ui_print_header(undef, $text{'confirm_title'}, "");
		print &ui_confirmation_form(
			"delete_mail.cgi",
			($in{'all'} ?
				&text('confirm_warnallf', $folder->{'name'}) :
				&text('confirm_warnf', scalar(@delmail),
						       $folder->{'name'})).
			"<br>".
			($userconfig{'delete_warn'} ne 'y' ?
				$text{'confirm_warn2'}."<p>" :
			 $folder->{'type'} == 0 ?
				$text{'confirm_warn4'}."<p>" : ""),
			[ &inputs_to_hiddens(\%in) ],
			[ [ 'confirm', $text{'confirm_ok'} ] ],
			);
		&ui_print_footer("index.cgi?start=$in{'start'}&".
				 "folder=$in{'folder'}", $text{'index'});
		}
	else {
		# Go ahead and delete
		$gconfig{'logfiles'} = 0;
		&lock_folder($folder);
		my @mail;
		if ($in{'all'}) {
			# Clear the whole folder, unless the first email
			# is non-editable
			@mail = &mailbox_list_mails_sorted(0, 0, $folder);
			if (&editable_mail($mail[0])) {
				# Trash the lot
				&mailbox_empty_folder($folder);
				}
			else {
				# Delete all mail except the first
				my $fsz = &mailbox_folder_size($folder);
				@mail = &mailbox_list_mails_sorted(1,
					$fsz-1, $folder);
				my @delmailrest = @mail[0..$#mail];
				&mailbox_delete_mail($folder, @delmailrest);
				}
			}
		else {
			# Just delete selected messages
			&mailbox_delete_mail($folder, @delmail);
			}
		&unlock_folder($folder);
		&redirect("index.cgi?start=$in{'start'}&folder=$in{'folder'}&refresh=$r");
		}
	}
else {
	&error("No button clicked!");
	}
&pop3_logout_all();
