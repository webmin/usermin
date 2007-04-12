#!/usr/local/bin/perl
# Scan through all folders, and apply the scheduled deletion policy for each

$no_acl_check++;
$ENV{'REMOTE_USER'} = getpwuid($<);
require './mailbox-lib.pl';
@folders = &list_folders();

&open_read_hash();		# hack to force correct DBM mode

foreach $f (@folders) {
	# Skip folders for which clearing isn't active
	next if ($f->{'nowrite'});
	$auto = &get_auto_schedule($f);
	next if (!$auto || !$auto->{'enabled'});

	@delmails = ( );
	if ($auto->{'mode'} == 0) {
		# Find messages that are too old
		@mails = &mailbox_list_mails(undef, undef, $f, 1);
		$cutoff = time() - $auto->{'days'}*24*60*60;
		foreach $m (@mails) {
			$time = &parse_mail_date($m->{'header'}->{'date'});
			if ($time && $time < $cutoff ||
			    !$time && $auto->{'invalid'}) {
				push(@delmails, $m);
				}
			}
		}
	else {
		# Cut folder down to size, by deleting oldest first
		$size = &folder_size($f);
		@mails = &mailbox_list_mails(undef, undef, $f, 1);
		while($size > $auto->{'size'}) {
			last if (!@mails);	# empty!
			$oldmail = shift(@mails);
			push(@delmails, $oldmail);
			$size -= $oldmail->{'size'};
			}
		}

	if (@delmails) {
		if ($auto->{'all'}) {
			# Clear the whole folder
			&mailbox_empty_folder($f);
			}
		else {
			# Just delete mails that are over the limit
			&mailbox_delete_mail($f, reverse(@delmails));
			}
		}
	}

