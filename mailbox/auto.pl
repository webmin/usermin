#!/usr/local/bin/perl
# Scan through all folders, and apply the scheduled deletion policy for each
use strict;
use warnings;

our $no_acl_check++;
$ENV{'REMOTE_USER'} = getpwuid($<);
require './mailbox-lib.pl';
my @folders = &list_folders();

&open_read_hash();		# hack to force correct DBM mode

my $purge_mail = sub {
	my ($auto, $f, $folders, $delmails) = @_;
	if (@{$delmails}) {
		if ($auto->{'all'} == 1) {
			# Clear the whole folder
			&mailbox_empty_folder($f);
			}
		elsif ($auto->{'all'} == 0) {
			# Just delete mails that are over the limit
			&mailbox_delete_mail($f, reverse(@{$delmails}));
			}
		elsif ($auto->{'all'} == 2) {
			# Move to another folder
			my ($dest) = grep { &folder_name($_) eq $auto->{'dest'} }
				       @{$folders};
			if (!$dest) {
				print STDERR "destination folder ".
					    "$auto->{'dest'} does not exist!\n";
				next;
				}
			&mailbox_move_mail($f, $dest, reverse(@{$delmails}));
			}
		}
	};

foreach my $f (@folders) {
	# Skip folders for which clearing isn't active
	next if ($f->{'nowrite'});
	my $auto = &get_auto_schedule($f);
	next if (!$auto || !$auto->{'enabled'});

	my $headersonly = $auto->{'all'} == 2 ? 0 : 1;
	if ($auto->{'mode'} == 0) {
		# Find messages that are too old
		my @mails = &mailbox_list_mails(undef, undef, $f, $headersonly);
		my $cutoff = time() - $auto->{'days'}*24*60*60;
		my $future = time() + 7*24*60*60;
		foreach my $m (@mails) {
			my $time = &parse_mail_date($m->{'header'}->{'date'});
			$time ||= $m->{'time'};
			if ($time && $time < $cutoff ||
			    !$time && $auto->{'invalid'} ||
			    $time > $future && $auto->{'invalid'}) {
				my @delmails;
				push(@delmails, $m);
				&$purge_mail($auto, $f, \@folders, \@delmails);
				}
			}
		}
	else {
		# Cut folder down to size, by deleting oldest first
		my $size = &folder_size($f);
		my @mails = &mailbox_list_mails(undef, undef, $f, $headersonly);
		while($size > $auto->{'size'}) {
			last if (!@mails);	# empty!
			my $oldmail = shift(@mails);
			my @delmails;
			push(@delmails, $oldmail);
			$size -= $oldmail->{'size'};
			&$purge_mail($auto, $f, \@folders, \@delmails);
			}
		}
	}
